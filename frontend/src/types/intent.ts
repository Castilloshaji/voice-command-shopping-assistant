export type IntentType =
  | 'ADD_ITEM'
  | 'REMOVE_ITEM'
  | 'UPDATE_QUANTITY'
  | 'SEARCH_PRODUCT'
  | 'SHOW_LIST'
  | 'CLEAR_LIST'
  | 'GET_SUGGESTIONS'
  | 'UNKNOWN';

export interface VoiceParseRequest {
  text: string;
}

export interface ParsedIntent {
  intent: IntentType;
  item?: string | null;
  quantity?: number | null;
  unit?: string | null;
  max_price?: number | null;
  min_price?: number | null;
  brand?: string | null;
  category?: string | null;
  confidence?: number;
  original_text: string;
  normalized_text?: string | null;
  message?: string | null;
}
