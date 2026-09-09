import {
  RetrievalApiRequest,
  RetrievalApiResponse,
  RetrievalApiErrorResponse,
} from '../types/retrieval_api';

export async function searchHybridRetrieval(
  req: RetrievalApiRequest
): Promise<RetrievalApiResponse> {
  const response = await fetch('/api/retrieval/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  const data = await response.json();

  if (!response.ok) {
    const errorData = data as RetrievalApiErrorResponse;
    const errorMessage =
      errorData?.error?.message || `Retrieval failed with status ${response.status}`;
    const error = new Error(errorMessage) as Error & {
      code?: string;
      request_id?: string;
      status?: number;
    };
    error.code = errorData?.error?.code;
    error.request_id = errorData?.error?.request_id;
    error.status = response.status;
    throw error;
  }

  return data as RetrievalApiResponse;
}
