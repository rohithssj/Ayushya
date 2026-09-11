import { NextResponse } from 'next/server';
import { execFile } from 'child_process';
import path from 'path';
import fs from 'fs';
import { promisify } from 'util';
import type {
  AnalysisApiRequest,
  AnalysisApiResponse,
  AnalysisApiErrorResponse,
  IngredientInput,
} from '@/features/rag/types/analysis_api';
import {
  Jurisdiction,
  VALID_JURISDICTIONS,
  VALID_DOMAINS,
} from '@/features/rag/types/retrieval_api';

const execFileAsync = promisify(execFile);

function generateAnalysisId(productName: string): string {
  const cleanName = productName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'formulation';
  const rand = Math.random().toString(36).substring(2, 7);
  return `${cleanName}-${Date.now().toString(36)}-${rand}`;
}

function createErrorResponse(
  code: string,
  message: string,
  status: number
) {
  return NextResponse.json(
    { error: { code, message } },
    { status }
  );
}

export async function POST(request: Request) {
  // ── Parse body ──
  let body: unknown;
  try {
    const text = await request.text();
    if (!text || !text.trim()) {
      return createErrorResponse('INVALID_REQUEST', 'Request body must be non-empty JSON.', 400);
    }
    body = JSON.parse(text);
  } catch {
    return createErrorResponse('INVALID_REQUEST', 'Malformed JSON payload.', 400);
  }

  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    return createErrorResponse('INVALID_REQUEST', 'Request body must be a JSON object.', 400);
  }

  const rawReq = body as Record<string, unknown>;

  // ── Validate product name ──
  if (!rawReq.productName || typeof rawReq.productName !== 'string' || !rawReq.productName.trim()) {
    return createErrorResponse('VALIDATION_ERROR', 'Field "productName" is required.', 422);
  }
  const productName = rawReq.productName.trim();

  // ── Validate category ──
  const category = typeof rawReq.category === 'string' && rawReq.category.trim()
    ? rawReq.category.trim()
    : 'Ayurveda-Aahar';

  // ── Validate form ──
  const form = typeof rawReq.form === 'string' && rawReq.form.trim()
    ? rawReq.form.trim()
    : 'Tablet';

  // ── Validate description ──
  const description = typeof rawReq.description === 'string'
    ? rawReq.description.trim()
    : '';

  // ── Validate ingredients ──
  const ingredients: IngredientInput[] = [];
  if (Array.isArray(rawReq.ingredients)) {
    for (const ing of rawReq.ingredients) {
      if (typeof ing === 'object' && ing !== null) {
        const name = String((ing as Record<string, unknown>).name || '').trim();
        const quantity = String((ing as Record<string, unknown>).quantity || '').trim();
        const unit = String((ing as Record<string, unknown>).unit || 'mg').trim();
        if (name) {
          ingredients.push({ name, quantity, unit });
        }
      }
    }
  }

  // ── Validate jurisdiction ──
  if (!rawReq.jurisdiction || typeof rawReq.jurisdiction !== 'string') {
    return createErrorResponse('VALIDATION_ERROR', 'Field "jurisdiction" is required.', 422);
  }
  const normJur = rawReq.jurisdiction.trim().toLowerCase();
  const jurisdiction: Jurisdiction = normJur.includes('international') ? 'International' : 'India';

  // ── Construct targeted formulation intelligence query ──
  const ingredientNames = ingredients.map((i) => i.name).join(', ');
  const formulationContext = ingredientNames ? `Ingredients: ${ingredientNames}.` : '';
  const query = `Legal and regulatory requirements, patent eligibility, traditional knowledge exclusions under Section 3(p)/3(e), and compliance standards for "${productName}" (${category} formulation in ${form} form). ${formulationContext} Description: ${description}`.trim();

  // ── Map category to relevant legal domain filter if applicable ──
  let domain: string | null = null;
  const lowerCat = category.toLowerCase();
  if (lowerCat.includes('aahar') || lowerCat.includes('food')) {
    domain = 'ayurveda-aahar';
  } else if (lowerCat.includes('cosmetic')) {
    domain = 'drugs-cosmetics';
  } else if (lowerCat.includes('patent') || lowerCat.includes('extract')) {
    domain = 'patents';
  }

  const analysisId = generateAnalysisId(productName);
  const baseDir = process.cwd();
  const scriptPath = path.join(baseDir, 'scripts', 'grounded_answer_api.py');

  let pythonPath = path.join(baseDir, '.venv', 'Scripts', 'python.exe');
  if (!fs.existsSync(pythonPath)) {
    pythonPath = path.join(baseDir, '.venv', 'bin', 'python');
  }
  if (!fs.existsSync(pythonPath)) {
    pythonPath = 'python';
  }

  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    return createErrorResponse(
      'LLM_UNAVAILABLE',
      'LLM service is not configured. OPENROUTER_API_KEY is missing.',
      503
    );
  }

  const args = [
    scriptPath,
    '--query', query,
    '--jurisdiction', jurisdiction,
    '--top-k', '5',
    '--request-id', analysisId,
  ];
  if (domain && VALID_DOMAINS.has(domain)) {
    args.push('--domain', domain);
  }

  try {
    const { stdout } = await execFileAsync(pythonPath, args, {
      cwd: baseDir,
      timeout: 90000,
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
      return createErrorResponse('LLM_UNAVAILABLE', 'Analysis service returned empty output.', 503);
    }

    const pythonResult = JSON.parse(stdout);

    const responsePayload: AnalysisApiResponse = {
      id: analysisId,
      productName,
      category,
      form,
      description,
      ingredients,
      jurisdiction,
      query,
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
      createdAt: new Date().toISOString(),
      ...(pythonResult.error === 'llm_provider_error' && {
        error: 'llm_provider_error',
        error_message: pythonResult.error_message,
      }),
    };

    return NextResponse.json(responsePayload, { status: 200 });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return createErrorResponse(
      'ANALYSIS_FAILED',
      `Product analysis failed: ${message}`,
      500
    );
  }
}
