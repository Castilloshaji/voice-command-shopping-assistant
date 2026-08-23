import { ParsedIntent, IntentType } from '../types/intent';
import { ListItem, ListItemCreate, ListItemUpdate } from '../types/shoppingList';
import { Product } from '../types/product';
import { Suggestion } from '../types/suggestion';

const API_BASE_URL = '/api/v1';

export interface HealthCheckResponse {
  status: string;
  app: string;
  version: string;
}

export interface CommandExecutionResponse {
  success: boolean;
  intent: IntentType;
  message: string;
  data?: any;
}

export interface ProductSearchParams {
  query?: string;
  category?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  availability?: boolean;
}

const SESSION_KEY = 'voice-shopping-session-id';

export function getConversationSessionId(): string {
  if (typeof window === 'undefined') {
    return 'server-session';
  }
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id =
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export function resetConversationSessionId(): string {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(SESSION_KEY);
  }
  return getConversationSessionId();
}

export const apiService = {
  async getHealth(): Promise<HealthCheckResponse> {
    const response = await fetch('/health');
    if (!response.ok) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }
    return response.json();
  },

  async getShoppingList(): Promise<ListItem[]> {
    const response = await fetch(`${API_BASE_URL}/items`);
    if (!response.ok) {
      throw new Error(`Failed to fetch shopping list (${response.status})`);
    }
    return response.json();
  },

  async createShoppingItem(itemData: ListItemCreate): Promise<ListItem> {
    const response = await fetch(`${API_BASE_URL}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(itemData),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Failed to create item (${response.status})`);
    }
    return response.json();
  },

  async updateShoppingItem(id: number, itemData: ListItemUpdate): Promise<ListItem> {
    const response = await fetch(`${API_BASE_URL}/items/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(itemData),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Failed to update item (${response.status})`);
    }
    return response.json();
  },

  async deleteShoppingItem(id: number): Promise<{ message: string; id: number }> {
    const response = await fetch(`${API_BASE_URL}/items/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Failed to delete item (${response.status})`);
    }
    return response.json();
  },

  async clearShoppingList(): Promise<{ message: string; deleted_count: number }> {
    const response = await fetch(`${API_BASE_URL}/items`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Failed to clear list (${response.status})`);
    }
    return response.json();
  },

  async searchProducts(params?: ProductSearchParams): Promise<Product[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      if (params.query) searchParams.append('query', params.query);
      if (params.category) searchParams.append('category', params.category);
      if (params.brand) searchParams.append('brand', params.brand);
      if (params.min_price !== undefined) searchParams.append('min_price', params.min_price.toString());
      if (params.max_price !== undefined) searchParams.append('max_price', params.max_price.toString());
      if (params.availability !== undefined) searchParams.append('availability', params.availability.toString());
    }

    const queryStr = searchParams.toString();
    const url = `${API_BASE_URL}/products${queryStr ? `?${queryStr}` : ''}`;

    const response = await fetch(url);
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Failed to fetch products (${response.status})`);
    }
    return response.json();
  },

  async getSuggestions(limit: number = 5): Promise<Suggestion[]> {
    const response = await fetch(`${API_BASE_URL}/suggestions?limit=${limit}`);
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Failed to fetch suggestions (${response.status})`);
    }
    return response.json();
  },

  async parseVoiceCommand(text: string, language?: string, sessionId?: string): Promise<ParsedIntent> {
    const session_id = sessionId || getConversationSessionId();
    const lang = language || 'en-US';
    const response = await fetch(`${API_BASE_URL}/voice/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language: lang, session_id }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || `Server returned error (${response.status})`;
      throw new Error(message);
    }

    return response.json();
  },

  async executeVoiceCommand(text: string, language?: string, sessionId?: string): Promise<CommandExecutionResponse> {
    const session_id = sessionId || getConversationSessionId();
    const lang = language || 'en-US';
    const response = await fetch(`${API_BASE_URL}/voice/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language: lang, session_id }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || `Server returned error (${response.status})`;
      throw new Error(message);
    }

    return response.json();
  },

  async getCheckoutPreview(): Promise<import('../types/checkout').CheckoutPreview> {
    const response = await fetch(`${API_BASE_URL}/checkout/preview`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to fetch checkout preview (${response.status})`);
    }
    return response.json();
  },

  async placeOrder(): Promise<import('../types/checkout').Order> {
    const response = await fetch(`${API_BASE_URL}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to place order (${response.status})`);
    }
    return response.json();
  },

  async getOrders(): Promise<import('../types/checkout').Order[]> {
    const response = await fetch(`${API_BASE_URL}/orders`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to fetch orders (${response.status})`);
    }
    return response.json();
  },

  async getOrderById(orderId: number): Promise<import('../types/checkout').Order> {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to fetch order details (${response.status})`);
    }
    return response.json();
  },
};
