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

export interface RetrievalApiResponse {
  request_id: string;
  query: string;
  jurisdiction: Jurisdiction;
  domain: string | null;
  retrieval_method: 'hybrid_rrf';
  top_k: number;
  result_count: number;
  evidence_strength: 'not_calculated';
  abstention_recommended: boolean;
  results: RetrievalResultItem[];
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
