const API_BASE_URL = '/api/v1';

export interface HealthCheckResponse {
  status: string;
  app: string;
  version: string;
}

export const apiService = {
  async getHealth(): Promise<HealthCheckResponse> {
    const response = await fetch('/health');
    if (!response.ok) {
      throw new Error(Health check failed with status: );
    }
    return response.json();
  },
};
