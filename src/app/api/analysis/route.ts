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
  ClassificationAssessment,
  IPAssessmentItem,
  RegulatoryAssessmentItem,
  TKBiodiversityAssessment,
  ComplianceItem,
} from '@/features/rag/types/analysis_api';
import {
  Jurisdiction,
  VALID_JURISDICTIONS,
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

  // ── Validate category / proposed classification ──
  const category = typeof rawReq.category === 'string' && rawReq.category.trim()
    ? rawReq.category.trim()
    : typeof rawReq.proposed_classification === 'string' && rawReq.proposed_classification.trim()
    ? rawReq.proposed_classification.trim()
    : 'no_preference';

  // ── Validate form ──
  const form = typeof rawReq.form === 'string' && rawReq.form.trim()
    ? rawReq.form.trim()
    : 'Tablet';

  // ── Validate description / intended use ──
  const description = typeof rawReq.description === 'string'
    ? rawReq.description.trim()
    : '';
  const intended_use = typeof rawReq.intended_use === 'string' && rawReq.intended_use.trim()
    ? rawReq.intended_use.trim()
    : typeof rawReq.intendedUse === 'string' && rawReq.intendedUse.trim()
    ? rawReq.intendedUse.trim()
    : description;

  // ── Optional classification facts ──
  const product_claims = typeof rawReq.product_claims === 'string' ? rawReq.product_claims.trim() : typeof rawReq.productClaims === 'string' ? rawReq.productClaims.trim() : '';
  const disease_claim_flag = Boolean(rawReq.disease_claim_flag || rawReq.diseaseClaimFlag);
  const disease_claim_text = typeof rawReq.disease_claim_text === 'string' ? rawReq.disease_claim_text.trim() : typeof rawReq.diseaseClaimText === 'string' ? rawReq.diseaseClaimText.trim() : '';
  const is_classical_basis = typeof rawReq.is_classical_basis === 'string' ? rawReq.is_classical_basis.trim() : typeof rawReq.isClassicalBasis === 'string' ? rawReq.isClassicalBasis.trim() : 'unknown';
  const classical_reference = typeof rawReq.classical_reference === 'string' && rawReq.classical_reference.trim() ? rawReq.classical_reference.trim() : typeof rawReq.classicalReference === 'string' && rawReq.classicalReference.trim() ? rawReq.classicalReference.trim() : undefined;
  const manufacturing_processing = typeof rawReq.manufacturing_processing === 'string' ? rawReq.manufacturing_processing.trim() : typeof rawReq.manufacturingProcessing === 'string' ? rawReq.manufacturingProcessing.trim() : '';

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
  if (!VALID_JURISDICTIONS.has(normJur)) {
    return createErrorResponse(
      'VALIDATION_ERROR',
      `Invalid jurisdiction "${rawReq.jurisdiction}". Supported: "India", "International".`,
      422
    );
  }
  const jurisdiction: Jurisdiction = normJur === 'india' ? 'India' : 'International';

  // ── Optional traditional knowledge reference ──
  const traditional_knowledge_ref = classical_reference ||
    (typeof rawReq.traditional_knowledge_ref === 'string' && rawReq.traditional_knowledge_ref.trim()
      ? rawReq.traditional_knowledge_ref.trim()
      : undefined);

  const analysisId = generateAnalysisId(productName);
  const baseDir = process.cwd();

  // ── Locate product_analysis_api.py (dedicated product analysis script) ──
  const scriptPath = path.join(baseDir, 'scripts', 'product_analysis_api.py');

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

  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    return createErrorResponse(
      'LLM_UNAVAILABLE',
      'LLM service is not configured. OPENROUTER_API_KEY is missing.',
      503
    );
  }

  // ── Build structured payload for product_analysis_api.py ──
  const payload: Record<string, unknown> = {
    productName,
    category,
    proposed_classification: category,
    form,
    description: description || intended_use,
    intended_use,
    product_claims,
    disease_claim_flag,
    disease_claim_text,
    is_classical_basis,
    classical_reference,
    manufacturing_processing,
    ingredients,
    jurisdiction,
  };
  if (traditional_knowledge_ref) {
    payload.traditional_knowledge_ref = traditional_knowledge_ref;
  }


  const args = [
    scriptPath,
    '--analysis-id', analysisId,
  ];

  try {
    const { stdout } = await execFileAsync(pythonPath, args, {
      cwd: baseDir,
      timeout: 120000, // 2 minutes finite upper bound (accommodates cold start + retrieval + primary/fallback LLM)
      maxBuffer: 10 * 1024 * 1024, // 10MB explicit maxBuffer to prevent I/O truncation
      shell: true,
      windowsHide: true,
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8',
        PRODUCT_PAYLOAD: JSON.stringify(payload),
        OPENROUTER_API_KEY: apiKey,
        LLM_MODEL: process.env.LLM_MODEL || 'mistralai/mistral-small-24b-instruct-2501',
        LLM_FALLBACK_MODELS: process.env.LLM_FALLBACK_MODELS || 'meta-llama/llama-3.3-70b-instruct,nvidia/nemotron-3-super-120b-a12b',
        LLM_TIMEOUT_SECONDS: process.env.LLM_TIMEOUT_SECONDS || '25',
      },
    });

    if (!stdout || !stdout.trim()) {
      return createErrorResponse('LLM_UNAVAILABLE', 'Analysis service returned empty output.', 503);
    }

    let pythonResult: Record<string, unknown>;
    try {
      pythonResult = JSON.parse(stdout);
    } catch {
      console.error('[ProductAnalysisAPI] Failed to parse JSON output from python bridge.');
      return createErrorResponse('ANALYSIS_FAILED', 'Analysis service returned malformed output.', 500);
    }

    // ── Map Python result to extended AnalysisApiResponse ──
    const evidenceStrength = (pythonResult.evidence_strength as string) || 'insufficient';
    const abstained = Boolean(pythonResult.abstained);
    const groundedSummary = (pythonResult.grounded_summary as string | null) ?? null;

    // For backward compatibility 'answer' = grounded_summary
    const answer = groundedSummary;

    const responsePayload: AnalysisApiResponse = {
      id: analysisId,
      productName,
      category,
      form,
      description,
      ingredients,
      jurisdiction,
      // Human-readable summary query (not the LLM query — targeted queries were used internally)
      query: `Product formulation analysis for "${productName}" (${category}, ${form}) in ${jurisdiction} jurisdiction.`,
      answer,
      abstained,
      abstention_reason: (pythonResult.abstention_reason as string | null) ?? null,
      evidence_strength: evidenceStrength as AnalysisApiResponse['evidence_strength'],
      requires_human_review: Boolean(pythonResult.requires_human_review),
      citations: Array.isArray(pythonResult.citations) ? (pythonResult.citations as string[]) : [],
      evidence: (pythonResult.evidence as AnalysisApiResponse['evidence']) || { selected: [], count: 0 },
      evidence_assessment: (pythonResult.evidence_assessment as AnalysisApiResponse['evidence_assessment']) || {
        strength: evidenceStrength,
        abstention_recommended: abstained,
        requires_human_review: Boolean(pythonResult.requires_human_review),
        reasons: [],
      },
      createdAt: new Date().toISOString(),
      // ── Structured analysis fields ──
      grounded_summary: groundedSummary,
      analysis_id: (pythonResult.analysis_id as string) || analysisId,
      domains_queried: Array.isArray(pythonResult.domains_queried)
        ? (pythonResult.domains_queried as string[])
        : [],
      query_count: typeof pythonResult.query_count === 'number' ? pythonResult.query_count : 0,
      ...(pythonResult.classification
        ? { classification: pythonResult.classification as ClassificationAssessment }
        : {}),
      ...(Array.isArray(pythonResult.ip_assessment) && {
        ip_assessment: pythonResult.ip_assessment as IPAssessmentItem[],
      }),
      ...(Array.isArray(pythonResult.regulatory_assessment) && {
        regulatory_assessment: pythonResult.regulatory_assessment as RegulatoryAssessmentItem[],
      }),
      ...(pythonResult.tk_biodiversity
        ? { tk_biodiversity: pythonResult.tk_biodiversity as TKBiodiversityAssessment }
        : {}),
      ...(Array.isArray(pythonResult.compliance_checklist) && {
        compliance_checklist: pythonResult.compliance_checklist as ComplianceItem[],
      }),
      ...(pythonResult.error === 'llm_provider_error' && {
        error: 'llm_provider_error' as const,
        error_message: pythonResult.error_message as string,
      }),
    };

    return NextResponse.json(responsePayload, { status: 200 });
  } catch (err: unknown) {
    const errObj = err as { code?: string; killed?: boolean; signal?: string; message?: string };
    console.error(`[ProductAnalysisAPI] Subprocess error [code=${errObj.code || 'UNKNOWN'}, killed=${Boolean(errObj.killed)}, signal=${errObj.signal || 'NONE'}]`);
    const message = err instanceof Error ? err.message : String(err);
    return createErrorResponse(
      'ANALYSIS_FAILED',
      `Product analysis failed: ${message}`,
      500
    );
  }
}
