import type {
  EvidenceSection,
  EvidenceAssessment,
  EvidenceStrength,
  Jurisdiction,
  CitationRecord,
} from './retrieval_api';

export interface IngredientInput {
  name: string;
  quantity: string;
  unit: string;
}

export interface AnalysisApiRequest {
  productName: string;
  category: string;
  form?: string;
  description: string;
  ingredients: IngredientInput[];
  jurisdiction: Jurisdiction;
  domain?: string;
  /** Optional traditional knowledge / classical reference field (future UI) */
  traditional_knowledge_ref?: string;
}

// ---------------------------------------------------------------------------
// Structured analysis result types (new — all fields explicitly preliminary)
// ---------------------------------------------------------------------------

/** Preliminary product classification assessment. Never an official determination. */
export interface ClassificationAssessment {
  user_selected: string;
  preliminary_assessment: string;
  evidence_strength: EvidenceStrength;
  /** Always true — classification is never officially determined by AYUSHYA */
  requires_verification: boolean;
  supporting_citation_ids: string[];
}

/** Preliminary IP assessment for one IP type. */
export interface IPAssessmentItem {
  ip_type: string;
  relevance: 'potentially_relevant' | 'low_relevance' | 'insufficient_evidence';
  preliminary_assessment: string;
  reasoning: string;
  evidence_strength: EvidenceStrength;
  /** Always true — AYUSHYA is decision support, not a legal determination. */
  requires_verification: boolean;
  supporting_citation_ids: string[];
}

/** Preliminary regulatory framework assessment for one framework. */
export interface RegulatoryAssessmentItem {
  framework: string;
  why_applicable: string;
  relevant_provisions: string[];
  evidence_strength: EvidenceStrength;
  /** Always true — regulatory applicability must be professionally verified. */
  requires_verification: boolean;
  supporting_citation_ids: string[];
}

/** Traditional knowledge and biodiversity/ABS preliminary assessment. */
export interface TKBiodiversityAssessment {
  tk_considerations: string;
  biodiversity_considerations: string;
  abs_note: string;
  evidence_strength: EvidenceStrength;
  /** Always true — TK/biodiversity conclusions are preliminary. */
  requires_verification: boolean;
  supporting_citation_ids: string[];
  /** True if evidence was insufficient for this dimension */
  insufficient: boolean;
}

/** A single actionable compliance checklist item derived from evidence. */
export interface ComplianceItem {
  action: string;
  reason: string;
  legal_area: string;
  priority: 'high' | 'medium' | 'low';
  /** Always true — checklist items are preliminary decision support. */
  requires_verification: boolean;
  supporting_citation_id?: string;
}

// ---------------------------------------------------------------------------
// Core API response types
// ---------------------------------------------------------------------------

export interface AnalysisApiResponse {
  id: string;
  productName: string;
  category: string;
  form: string;
  description: string;
  ingredients: IngredientInput[];
  jurisdiction: Jurisdiction;
  query: string;
  answer: string | null;
  abstained: boolean;
  abstention_reason: string | null;
  evidence_strength: EvidenceStrength;
  requires_human_review: boolean;
  citations: string[];
  evidence: EvidenceSection;
  evidence_assessment: EvidenceAssessment;
  createdAt: string;
  error?: 'llm_provider_error';
  error_message?: string;
  // ── Structured analysis fields (optional — present on successful product analysis) ──
  /** Preliminary classification assessment. requires_verification is always true. */
  classification?: ClassificationAssessment;
  /** Preliminary IP protection assessments per IP type. */
  ip_assessment?: IPAssessmentItem[];
  /** Preliminary regulatory framework assessments. */
  regulatory_assessment?: RegulatoryAssessmentItem[];
  /** Traditional knowledge and biodiversity considerations. */
  tk_biodiversity?: TKBiodiversityAssessment;
  /** Evidence-backed compliance checklist items. */
  compliance_checklist?: ComplianceItem[];
  /** Legal domains queried during this analysis. */
  domains_queried?: string[];
  /** Number of targeted retrieval queries executed. */
  query_count?: number;
  /** Grounded narrative from single LLM synthesis call. */
  grounded_summary?: string | null;
  /** Analysis ID (from Python pipeline; same as id for display). */
  analysis_id?: string;
}

export interface AnalysisApiErrorResponse {
  error: {
    code: string;
    message: string;
    request_id?: string;
  };
}
