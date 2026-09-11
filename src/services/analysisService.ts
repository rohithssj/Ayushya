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
    // 1. Check specific id exact key
    const item = window.sessionStorage.getItem(`${STORAGE_PREFIX}${id}`);
    if (item) {
      return JSON.parse(item);
    }

    // 2. Check if latest matches
    const latest = window.sessionStorage.getItem(`${STORAGE_PREFIX}latest`);
    if (latest) {
      const parsed: AnalysisApiResponse = JSON.parse(latest);
      if (parsed.id === id || parsed.id?.toLowerCase() === id?.toLowerCase() || id === "latest") {
        return parsed;
      }
    }

    // 3. Scan all session storage keys matching prefix for a matching parsed.id
    for (let i = 0; i < window.sessionStorage.length; i++) {
      const key = window.sessionStorage.key(i);
      if (key && key.startsWith(STORAGE_PREFIX) && key !== `${STORAGE_PREFIX}latest`) {
        const raw = window.sessionStorage.getItem(key);
        if (raw) {
          try {
            const parsed: AnalysisApiResponse = JSON.parse(raw);
            if (parsed.id === id || parsed.id?.toLowerCase() === id?.toLowerCase()) {
              return parsed;
            }
          } catch {
            // Ignore parse errors for stale keys
          }
        }
      }
    }
  } catch (e) {
    console.warn("Could not read analysis from sessionStorage:", e);
  }

  return null;
}
