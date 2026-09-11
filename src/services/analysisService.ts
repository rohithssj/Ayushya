import type {
  AnalysisApiRequest,
  AnalysisApiResponse,
  AnalysisApiErrorResponse,
  IngredientInput,
} from "@/features/rag/types/analysis_api";
import type { Jurisdiction } from "@/features/rag/types/retrieval_api";

const STORAGE_PREFIX = "ayushya_analysis_";

export async function submitProductAnalysis(
  payload: AnalysisApiRequest
): Promise<AnalysisApiResponse> {
  let res: Response;
  try {
    res = await fetch("/api/analysis", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    throw new Error("Unable to connect to the AYUSHYA analysis service. Please check your network.");
  }

  if (!res.ok) {
    let errorMsg = "Product analysis failed.";
    try {
      const errData: AnalysisApiErrorResponse = await res.json();
      if (errData.error?.message) {
        errorMsg = errData.error.message;
      }
    } catch {
      // Ignore JSON error
    }
    throw new Error(errorMsg);
  }

  const data: AnalysisApiResponse = await res.json();

  // Safely persist to sessionStorage for results dashboard
  if (typeof window !== "undefined" && window.sessionStorage) {
    try {
      window.sessionStorage.setItem(`${STORAGE_PREFIX}${data.id}`, JSON.stringify(data));
      // Also set as latest analysis
      window.sessionStorage.setItem(`${STORAGE_PREFIX}latest`, JSON.stringify(data));
    } catch (e) {
      console.warn("Could not save analysis to sessionStorage:", e);
    }
  }

  return data;
}

export function getStoredAnalysis(id: string): AnalysisApiResponse | null {
  if (typeof window === "undefined" || !window.sessionStorage) {
    return null;
  }

  try {
    // Check specific id
    const item = window.sessionStorage.getItem(`${STORAGE_PREFIX}${id}`);
    if (item) {
      return JSON.parse(item);
    }

    // Check if latest matches
    const latest = window.sessionStorage.getItem(`${STORAGE_PREFIX}latest`);
    if (latest) {
      const parsed: AnalysisApiResponse = JSON.parse(latest);
      if (parsed.id === id || id === "latest") {
        return parsed;
      }
    }
  } catch (e) {
    console.warn("Could not read analysis from sessionStorage:", e);
  }

  return null;
}
