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
}

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
}

export interface AnalysisApiErrorResponse {
  error: {
    code: string;
    message: string;
    request_id?: string;
  };
}
