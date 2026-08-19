import { ParsedIntent } from '../types/intent';

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
      throw new Error(`Health check failed with status: ${response.status}`);
    }
    return response.json();
  },

  async parseVoiceCommand(text: string): Promise<ParsedIntent> {
    const response = await fetch(`${API_BASE_URL}/voice/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || `Server returned error (${response.status})`;
      throw new Error(message);
    }

    return response.json();
  },
};
