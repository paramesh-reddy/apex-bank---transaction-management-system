import axios, { AxiosError } from 'axios';

// Default to relative /api/v1 (proxied by Vite to FastAPI backend) or explicit env var
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Array<{ field?: string; issue?: string }> | null;
  };
}

export function parseApiError(error: unknown): { code: string; message: string; details?: string[] } {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<ApiErrorResponse>;
    if (axiosErr.response?.data?.error) {
      const err = axiosErr.response.data.error;
      const detailsList: string[] = [];
      if (Array.isArray(err.details)) {
        err.details.forEach((d) => {
          if (typeof d === 'string') detailsList.push(d);
          else if (d.field && d.issue) detailsList.push(`${d.field}: ${d.issue}`);
          else if (d.issue) detailsList.push(d.issue);
        });
      }
      return {
        code: err.code || 'API_ERROR',
        message: err.message || 'An error occurred while processing the request.',
        details: detailsList.length > 0 ? detailsList : undefined,
      };
    }
    if (axiosErr.message === 'Network Error') {
      return {
        code: 'NETWORK_ERROR',
        message: 'Unable to reach backend service. Verify that the FastAPI backend is running.',
      };
    }
    return {
      code: `HTTP_${axiosErr.response?.status || 'ERROR'}`,
      message: axiosErr.message || 'An unexpected HTTP error occurred.',
    };
  }
  return {
    code: 'UNKNOWN_ERROR',
    message: error instanceof Error ? error.message : 'An unknown error occurred.',
  };
}
