import type {
  ChatApiRequest,
  ChatApiResponse,
  ChatApiErrorResponse,
} from "@/features/rag/types/chat_api";
import type { CitationRecord, Jurisdiction } from "@/features/rag/types/retrieval_api";

export interface LegalSource {
  title: string;
  act: string;
  section: string;
  url?: string;
  jurisdiction: string;
  authority?: string;
  page?: number | null;
  relevanceScore?: number;
}

export interface ChatMessageData {
  id: string;
  sender: "user" | "ayushya";
  text: string;
  timestamp: string;
  sources?: LegalSource[];
  confidence?: "High" | "Medium" | "Low";
  disclaimer?: string;
  requiresHumanAssistance?: boolean;
}

export interface ChatRequest {
  message: string;
  analysisId?: string;
  productName?: string;
  jurisdiction?: string;
  language?: string;
  history?: ChatMessageData[];
}

export interface ChatResponse {
  answer: string;
  sources: LegalSource[];
  confidence: "High" | "Medium" | "Low";
  disclaimer: string;
  requiresHumanAssistance: boolean;
  abstained?: boolean;
}

/**
 * Maps backend CitationRecord into clean UI LegalSource.
 * Never fabricates URLs — preserves exact source_url from metadata.
 */
function mapCitationToLegalSource(cit: CitationRecord): LegalSource {
  const parts: string[] = [];
  if (cit.section) parts.push(cit.section);
  if (cit.section_title) parts.push(cit.section_title);
  if (cit.subsection) parts.push(`(${cit.subsection})`);
  if (cit.chapter) parts.push(`[${cit.chapter}]`);
  if (cit.page_start) parts.push(`p. ${cit.page_start}`);

  const sectionStr = parts.length > 0 ? parts.join(" — ") : "Statutory Provision";

  return {
    title: cit.title || "Statutory Legal Provision",
    act: cit.document_id || cit.title || "Legal Source",
    section: sectionStr,
    jurisdiction: cit.jurisdiction || "India",
    authority: cit.authority || undefined,
    page: cit.page_start ?? undefined,
    url: cit.source_url && (cit.source_url.startsWith("http://") || cit.source_url.startsWith("https://"))
      ? cit.source_url
      : undefined,
  };
}

/**
 * Maps backend evidence_strength to UI Confidence.
 */
function mapEvidenceStrengthToConfidence(strength: string): "High" | "Medium" | "Low" {
  switch (strength.toLowerCase()) {
    case "strong":
      return "High";
    case "moderate":
      return "Medium";
    case "weak":
    case "insufficient":
    default:
      return "Low";
  }
}

/**
 * Real client communicating with POST /api/chat.
 * Calls Next.js API boundary server-side. OpenRouter API keys never touch client.
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const query = request.message.trim();
  if (!query) {
    throw new Error("Query cannot be empty.");
  }

  const rawJur = (request.jurisdiction || "India").trim().toLowerCase();
  const jurisdiction: Jurisdiction = rawJur.includes("international") ? "International" : "India";

  // If product context is provided, attach to query for grounding
  let combinedQuery = query;
  if (request.productName && !query.toLowerCase().includes(request.productName.toLowerCase())) {
    combinedQuery = `Regarding "${request.productName}": ${query}`;
  }

  const payload: ChatApiRequest = {
    query: combinedQuery,
    jurisdiction,
    top_k: 5,
  };

  let res: Response;
  try {
    res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (netErr) {
    throw new Error("Unable to reach AYUSHYA legal intelligence service. Please check your connection.");
  }

  if (!res.ok) {
    let errorDetail = "Failed to retrieve legal answer.";
    try {
      const errData: ChatApiErrorResponse = await res.json();
      if (errData.error?.message) {
        errorDetail = errData.error.message;
      }
    } catch {
      // Ignore JSON parse error on non-JSON response
    }
    throw new Error(errorDetail);
  }

  const data: ChatApiResponse = await res.json();

  // Extract selected citations
  const selectedCitations = (data.evidence?.selected || []).map((ev) =>
    mapCitationToLegalSource(ev.citation)
  );

  const confidence = mapEvidenceStrengthToConfidence(data.evidence_strength || "insufficient");

  // Handle Abstention
  if (data.abstained) {
    const abstentionText =
      data.abstention_reason ||
      "AYUSHYA could not find sufficient authoritative evidence for this question in the ingested statutory corpus.";

    return {
      answer: `${abstentionText}\n\n⚠️ Note: A human or qualified legal/regulatory review is recommended for this inquiry.`,
      sources: selectedCitations,
      confidence: "Low",
      disclaimer: "⚠️ Abstention notice: Informational guidance based on available evidence, not legal advice.",
      requiresHumanAssistance: true,
      abstained: true,
    };
  }

  // Handle Provider Error
  if (data.error === "llm_provider_error") {
    return {
      answer: "The AI reasoning provider is currently unavailable. Retrieved statutory evidence is listed below for your review.",
      sources: selectedCitations,
      confidence: confidence,
      disclaimer: "⚠️ Informational guidance based on available evidence, not legal advice.",
      requiresHumanAssistance: true,
      abstained: false,
    };
  }

  const answer = data.answer || "No grounded answer could be generated from available evidence.";

  return {
    answer,
    sources: selectedCitations,
    confidence,
    disclaimer: "⚠️ Informational guidance based on available evidence, not legal advice.",
    requiresHumanAssistance: data.requires_human_review,
    abstained: false,
  };
}
