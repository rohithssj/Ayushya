export type Jurisdiction = 'India' | 'International';

export const VALID_JURISDICTIONS: ReadonlySet<string> = new Set(['india', 'international']);

export const VALID_DOMAINS: ReadonlySet<string> = new Set([
  'cbd',
  'treaties',
  'trademarks',
  'biodiversity',
  'copyright',
  'trips',
  'patents',
  'drugs-cosmetics',
  'ayurveda-aahar',
  'designs',
  'gi',
]);

export interface RetrievalApiRequest {
  query: string;
  jurisdiction: Jurisdiction;
  domain?: string;
  top_k?: number;
}

export interface RetrievalResultMetadata {
  chunk_id: string;
  document_id: string;
  title: string;
  jurisdiction: string;
  domain: string;
  document_type?: string;
  authority?: string;
  source?: string;
  source_url?: string | null;
  year?: number | null;
  language?: string;
  status?: string;
  retrieved_at?: string | null;
  chapter?: string | null;
  section?: string | null;
  section_title?: string | null;
  subsection?: string | null;
  page?: number | null;
  page_start?: number | null;
  page_end?: number | null;
  char_count?: number;
  [key: string]: unknown;
}

export interface RetrievalResultItem {
  rank: number;
  score: number;
  lexical_rank: number;
  semantic_rank: number;
  matched_terms?: string[];
  text: string;
  chunk_id: string;
  document_id: string;
  title: string;
  jurisdiction: string;
  domain: string;
  metadata: RetrievalResultMetadata;
}

export type EvidenceStrength = 'strong' | 'moderate' | 'weak' | 'insufficient';

export interface EvidenceAssessment {
  strength: EvidenceStrength;
  abstention_recommended: boolean;
  requires_human_review: boolean;
  reasons: string[];
}

// ---------------------------------------------------------------------------
// Phase 7 — Evidence Selection + Citation Construction types
// ---------------------------------------------------------------------------

export interface CitationRecord {
  citation_id: string;
  chunk_id: string;
  document_id: string;
  title: string;
  section?: string | null;
  section_title?: string | null;
  subsection?: string | null;
  chapter?: string | null;
  page?: number | null;
  page_start?: number | null;
  page_end?: number | null;
  jurisdiction: string;
  domain: string;
  authority?: string | null;
  year?: number | null;
  source_url?: string | null;
}

export interface SelectedEvidence {
  evidence_id: string;
  chunk_id: string;
  text: string;
  citation: CitationRecord;
  selection_reason: string;
}

export interface EvidenceSection {
  selected: SelectedEvidence[];
  count: number;
}

export interface RetrievalApiResponse {
  request_id: string;
  query: string;
  jurisdiction: Jurisdiction;
  domain: string | null;
  retrieval_method: 'hybrid_rrf';
  top_k: number;
  result_count: number;
  evidence_strength: EvidenceStrength;
  abstention_recommended: boolean;
  requires_human_review: boolean;
  evidence_assessment: EvidenceAssessment;
  results: RetrievalResultItem[];
  /** Phase 7 — structured evidence with citations */
  evidence?: EvidenceSection;
}

export type ErrorCode =
  | 'INVALID_REQUEST'
  | 'VALIDATION_ERROR'
  | 'NO_RESULTS'
  | 'RETRIEVAL_UNAVAILABLE'
  | 'INTERNAL_ERROR';

export interface RetrievalApiErrorResponse {
  error: {
    code: ErrorCode;
    message: string;
    request_id: string;
  };
}
