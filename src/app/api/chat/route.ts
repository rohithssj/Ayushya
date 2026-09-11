import { NextResponse } from 'next/server';
import { execFile } from 'child_process';
import path from 'path';
import fs from 'fs';
import { promisify } from 'util';
import {
  ChatApiResponse,
  ChatApiErrorResponse,
} from '@/features/rag/types/chat_api';
import {
  Jurisdiction,
  VALID_JURISDICTIONS,
  VALID_DOMAINS,
} from '@/features/rag/types/retrieval_api';

const execFileAsync = promisify(execFile);

function generateRequestId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `req_${crypto.randomUUID()}`;
  }
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

function createErrorResponse(
  code: ChatApiErrorResponse['error']['code'],
  message: string,
  requestId: string,
  status: number
) {
  return NextResponse.json(
    { error: { code, message, request_id: requestId } },
    { status }
  );
}

export async function POST(request: Request) {
  const requestId = generateRequestId();

  // ── Parse body ──
  let body: unknown;
  try {
    const text = await request.text();
    if (!text || !text.trim()) {
      return createErrorResponse('INVALID_REQUEST', 'Request body must be non-empty JSON.', requestId, 400);
    }
    body = JSON.parse(text);
  } catch {
    return createErrorResponse('INVALID_REQUEST', 'Malformed JSON payload.', requestId, 400);
  }

  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    return createErrorResponse('INVALID_REQUEST', 'Request body must be a JSON object.', requestId, 400);
  }

  const rawReq = body as Record<string, unknown>;

  // ── Validate query ──
  if (!rawReq.query || typeof rawReq.query !== 'string' || !rawReq.query.trim()) {
    return createErrorResponse('VALIDATION_ERROR', 'Field "query" is required and must be a non-empty string.', requestId, 422);
  }
  const query = rawReq.query.trim();
  if (query.length > 1000) {
    return createErrorResponse('VALIDATION_ERROR', 'Field "query" exceeds 1000 characters.', requestId, 422);
  }

  // ── Validate jurisdiction ──
  if (!rawReq.jurisdiction || typeof rawReq.jurisdiction !== 'string') {
    return createErrorResponse('VALIDATION_ERROR', 'Field "jurisdiction" is required.', requestId, 422);
  }
  const normJur = rawReq.jurisdiction.trim().toLowerCase();
  if (!VALID_JURISDICTIONS.has(normJur)) {
    return createErrorResponse(
      'VALIDATION_ERROR',
      `Invalid jurisdiction "${rawReq.jurisdiction}". Supported: "India", "International".`,
      requestId,
      422
    );
  }
  const jurisdiction: Jurisdiction = normJur === 'india' ? 'India' : 'International';

  // ── Validate domain (optional) ──
  let domain: string | null = null;
  if (rawReq.domain && typeof rawReq.domain === 'string' && rawReq.domain.trim()) {
    const normDomain = rawReq.domain.trim().toLowerCase();
    if (!VALID_DOMAINS.has(normDomain)) {
      return createErrorResponse(
        'VALIDATION_ERROR',
        `Invalid domain "${rawReq.domain}". Supported: ${Array.from(VALID_DOMAINS).join(', ')}.`,
        requestId,
        422
      );
    }
    domain = normDomain;
  }

  // ── Validate top_k (optional) ──
  let top_k = 5;
  if (rawReq.top_k !== undefined && rawReq.top_k !== null) {
    if (
      typeof rawReq.top_k !== 'number' ||
      !Number.isInteger(rawReq.top_k) ||
      rawReq.top_k < 1 ||
      rawReq.top_k > 20
    ) {
      return createErrorResponse('VALIDATION_ERROR', 'Field "top_k" must be an integer between 1 and 20.', requestId, 422);
    }
    top_k = rawReq.top_k;
  }

  // ── Resolve Python executable ──
  const baseDir = process.cwd();
  const scriptPath = path.join(baseDir, 'scripts', 'grounded_answer_api.py');

  let pythonPath = 'python';
  if (process.platform === 'win32') {
    const venvWinPy = path.join(baseDir, '.venv', 'Scripts', 'python.exe');
    if (fs.existsSync(venvWinPy)) {
      pythonPath = venvWinPy;
    }
  } else {
    const venvPosix = path.join(baseDir, '.venv', 'bin', 'python');
    if (fs.existsSync(venvPosix)) {
      pythonPath = venvPosix;
    }
  }

  // ── Security: pass API key from server env only ──
  // OPENROUTER_API_KEY is read by the Python provider from its own process env.
  // Never pass it as a CLI arg. Never log it.
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    return createErrorResponse(
      'LLM_UNAVAILABLE',
      'LLM service is not configured. OPENROUTER_API_KEY is missing.',
      requestId,
      503
    );
  }

  const args = [
    scriptPath,
    '--query', query,
    '--jurisdiction', jurisdiction,
    '--top-k', top_k.toString(),
    '--request-id', requestId,
  ];
  if (domain) {
    args.push('--domain', domain);
  }

  try {
    const { stdout } = await execFileAsync(pythonPath, args, {
      cwd: baseDir,
      timeout: 90000,  // 90s — LLM calls can be slow
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8',
        OPENROUTER_API_KEY: apiKey,
        LLM_MODEL: process.env.LLM_MODEL || 'nvidia/nemotron-3-super-120b-a12b',
        LLM_FALLBACK_MODELS: process.env.LLM_FALLBACK_MODELS || '',
        LLM_TIMEOUT_SECONDS: process.env.LLM_TIMEOUT_SECONDS || '15',
      },
    });

    if (!stdout || !stdout.trim()) {
      return createErrorResponse('LLM_UNAVAILABLE', 'Grounded answer service returned no output.', requestId, 503);
    }

    const pythonResult = JSON.parse(stdout);

    if (pythonResult.error && !pythonResult.answer && !pythonResult.abstained) {
      // Provider-level error from Python
      const errMsg = pythonResult.error_message || 'LLM provider error.';
      return createErrorResponse('LLM_UNAVAILABLE', errMsg, requestId, 503);
    }

    const responsePayload: ChatApiResponse = {
      request_id: pythonResult.request_id || requestId,
      query: pythonResult.query || query,
      answer: pythonResult.answer ?? null,
      abstained: Boolean(pythonResult.abstained),
      abstention_reason: pythonResult.abstention_reason ?? null,
      evidence_strength: pythonResult.evidence_strength || 'insufficient',
      requires_human_review: Boolean(pythonResult.requires_human_review),
      citations: Array.isArray(pythonResult.citations) ? pythonResult.citations : [],
      evidence: pythonResult.evidence || { selected: [], count: 0 },
      evidence_assessment: pythonResult.evidence_assessment || {
        strength: pythonResult.evidence_strength || 'insufficient',
        abstention_recommended: Boolean(pythonResult.abstained),
        requires_human_review: Boolean(pythonResult.requires_human_review),
        reasons: [],
      },
      ...(pythonResult.error === 'llm_provider_error' && {
        error: 'llm_provider_error',
        error_message: pythonResult.error_message,
      }),
    };

    return NextResponse.json(responsePayload, { status: 200 });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return createErrorResponse(
      'LLM_UNAVAILABLE',
      `Grounded answer service failed: ${message}`,
      requestId,
      503
    );
  }
}
