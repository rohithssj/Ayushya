import { NextResponse } from 'next/server';
import { execFile } from 'child_process';
import path from 'path';
import fs from 'fs';
import { promisify } from 'util';
import {
  RetrievalApiResponse,
  RetrievalApiErrorResponse,
  Jurisdiction,
  VALID_JURISDICTIONS,
  VALID_DOMAINS,
  RetrievalResultItem,
  RetrievalResultMetadata,
} from '@/features/rag/types/retrieval_api';

const execFileAsync = promisify(execFile);

function generateRequestId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `req_${crypto.randomUUID()}`;
  }
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

function createErrorResponse(
  code: RetrievalApiErrorResponse['error']['code'],
  message: string,
  requestId: string,
  status: number
) {
  return NextResponse.json(
    {
      error: {
        code,
        message,
        request_id: requestId,
      },
    },
    { status }
  );
}

export async function POST(request: Request) {
  const requestId = generateRequestId();

  let body: unknown;
  try {
    const text = await request.text();
    if (!text || !text.trim()) {
      return createErrorResponse(
        'INVALID_REQUEST',
        'Request body must be non-empty JSON.',
        requestId,
        400
      );
    }
    body = JSON.parse(text);
  } catch {
    return createErrorResponse(
      'INVALID_REQUEST',
      'Malformed JSON payload.',
      requestId,
      400
    );
  }

  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    return createErrorResponse(
      'INVALID_REQUEST',
      'Request body must be a JSON object.',
      requestId,
      400
    );
  }

  const rawReq = body as Record<string, unknown>;

  // Validation: query
  if (rawReq.query === undefined || rawReq.query === null) {
    return createErrorResponse(
      'VALIDATION_ERROR',
      'Field "query" is required.',
      requestId,
      422
    );
  }
  if (typeof rawReq.query !== 'string') {
    return createErrorResponse(
      'VALIDATION_ERROR',
      'Field "query" must be a string.',
      requestId,
      422
    );
  }
  const query = rawReq.query.trim();
  if (query.length === 0) {
    return createErrorResponse(
      'VALIDATION_ERROR',
      'Field "query" must not be empty or whitespace only.',
      requestId,
      422
    );
  }
  if (query.length > 1000) {
    return createErrorResponse(
      'VALIDATION_ERROR',
      'Field "query" exceeds maximum allowed length of 1000 characters.',
      requestId,
      422
    );
  }

  // Validation: jurisdiction
  if (rawReq.jurisdiction === undefined || rawReq.jurisdiction === null) {
    return createErrorResponse(
      'VALIDATION_ERROR',
      'Field "jurisdiction" is required.',
      requestId,
      422
    );
  }
  if (typeof rawReq.jurisdiction !== 'string') {
    return createErrorResponse(
      'VALIDATION_ERROR',
      'Field "jurisdiction" must be a string.',
      requestId,
      422
    );
  }
  const normJurisdiction = rawReq.jurisdiction.trim().toLowerCase();
  if (!VALID_JURISDICTIONS.has(normJurisdiction)) {
    return createErrorResponse(
      'VALIDATION_ERROR',
      `Invalid jurisdiction "${rawReq.jurisdiction}". Supported values: "India", "International".`,
      requestId,
      422
    );
  }
  const jurisdiction: Jurisdiction =
    normJurisdiction === 'india' ? 'India' : 'International';

  // Validation: domain
  let domain: string | null = null;
  if (rawReq.domain !== undefined && rawReq.domain !== null && rawReq.domain !== '') {
    if (typeof rawReq.domain !== 'string') {
      return createErrorResponse(
        'VALIDATION_ERROR',
        'Field "domain" must be a string if provided.',
        requestId,
        422
      );
    }
    const normDomain = rawReq.domain.trim().toLowerCase();
    if (!VALID_DOMAINS.has(normDomain)) {
      return createErrorResponse(
        'VALIDATION_ERROR',
        `Invalid domain "${rawReq.domain}". Supported values: ${Array.from(VALID_DOMAINS).join(', ')}.`,
        requestId,
        422
      );
    }
    domain = normDomain;
  }

  // Validation: top_k
  let top_k = 5;
  if (rawReq.top_k !== undefined && rawReq.top_k !== null) {
    if (
      typeof rawReq.top_k !== 'number' ||
      !Number.isInteger(rawReq.top_k) ||
      rawReq.top_k < 1 ||
      rawReq.top_k > 20
    ) {
      return createErrorResponse(
        'VALIDATION_ERROR',
        'Field "top_k" must be an integer between 1 and 20.',
        requestId,
        422
      );
    }
    top_k = rawReq.top_k;
  }

  // Execute Python Bridge
  const baseDir = process.cwd();
  const scriptPath = path.join(baseDir, 'scripts', 'retrieve_hybrid_api.py');

  let pythonPath = path.join(baseDir, '.venv', 'Scripts', 'python.exe');
  if (!fs.existsSync(pythonPath)) {
    pythonPath = path.join(baseDir, '.venv', 'bin', 'python');
  }
  if (!fs.existsSync(pythonPath)) {
    pythonPath = 'python';
  }

  const args = [
    scriptPath,
    '--query',
    query,
    '--jurisdiction',
    jurisdiction,
    '--top-k',
    top_k.toString(),
  ];
  if (domain) {
    args.push('--domain', domain);
  }

  try {
    const { stdout } = await execFileAsync(pythonPath, args, {
      cwd: baseDir,
      timeout: 30000,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    });

    if (!stdout || !stdout.trim()) {
      return createErrorResponse(
        'RETRIEVAL_UNAVAILABLE',
        'Retrieval service returned no output.',
        requestId,
        503
      );
    }

    const pythonResult = JSON.parse(stdout);

    if (pythonResult.error) {
      return createErrorResponse(
        'RETRIEVAL_UNAVAILABLE',
        `Retrieval error: ${pythonResult.error}`,
        requestId,
        503
      );
    }

    const rawResults: Record<string, unknown>[] = pythonResult.results || [];

    if (rawResults.length === 0) {
      return createErrorResponse(
        'NO_RESULTS',
        'No retrievable legal chunks found matching the specified query and filters.',
        requestId,
        404
      );
    }

    const results: RetrievalResultItem[] = rawResults.map((item, index) => {
      const {
        relevance_score,
        hybrid_score,
        lexical_rank,
        semantic_rank,
        matched_terms,
        text,
        ...restMetadata
      } = item;

      const metadata = restMetadata as unknown as RetrievalResultMetadata;

      return {
        rank: index + 1,
        score: typeof relevance_score === 'number' ? relevance_score : (typeof hybrid_score === 'number' ? hybrid_score : 0),
        lexical_rank: typeof lexical_rank === 'number' ? lexical_rank : 0,
        semantic_rank: typeof semantic_rank === 'number' ? semantic_rank : 0,
        matched_terms: Array.isArray(matched_terms) ? matched_terms.map(String) : [],
        text: typeof text === 'string' ? text : '',
        chunk_id: String(metadata.chunk_id || ''),
        document_id: String(metadata.document_id || ''),
        title: String(metadata.title || ''),
        jurisdiction: String(metadata.jurisdiction || ''),
        domain: String(metadata.domain || ''),
        metadata,
      };
    });

    const responsePayload: RetrievalApiResponse = {
      request_id: requestId,
      query,
      jurisdiction,
      domain,
      retrieval_method: 'hybrid_rrf',
      top_k,
      result_count: results.length,
      evidence_strength: 'not_calculated',
      abstention_recommended: false,
      results,
    };

    return NextResponse.json(responsePayload, { status: 200 });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return createErrorResponse(
      'RETRIEVAL_UNAVAILABLE',
      `Failed to execute retrieval service: ${message}`,
      requestId,
      503
    );
  }
}
