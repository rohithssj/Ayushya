import type { EvidenceSection, EvidenceAssessment, EvidenceStrength, Jurisdiction } from './retrieval_api';

export interface ChatApiRequest {
  query: string;
  jurisdiction: Jurisdiction;
  domain?: string;
  top_k?: number;
}

export interface ChatApiResponse {
  request_id: string;
  query: string;
  /** Grounded answer text; null when abstained or provider error */
  answer: string | null;
  abstained: boolean;
  abstention_reason: string | null;
  evidence_strength: EvidenceStrength;
  requires_human_review: boolean;
  /** citation_ids referenced in the answer, validated against selected evidence */
  citations: string[];
  evidence: EvidenceSection;
  evidence_assessment: EvidenceAssessment;
  /** Present only on provider error (not on abstention) */
  error?: 'llm_provider_error';
  error_message?: string;
}

export type ChatErrorCode =
  | 'INVALID_REQUEST'
  | 'VALIDATION_ERROR'
  | 'RETRIEVAL_UNAVAILABLE'
  | 'LLM_UNAVAILABLE'
  | 'INTERNAL_ERROR';

export interface ChatApiErrorResponse {
  error: {
    code: ChatErrorCode;
    message: string;
    request_id: string;
  };
}
