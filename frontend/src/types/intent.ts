export type IntentType =
  | 'ADD_ITEM'
  | 'REMOVE_ITEM'
  | 'UPDATE_QUANTITY'
  | 'SEARCH_PRODUCT'
  | 'SHOW_LIST'
  | 'CLEAR_LIST'
  | 'GET_SUGGESTIONS';

export interface VoiceParseRequest {
  transcript: string;
  language?: string;
}

export interface ParsedIntent {
  intent: IntentType;
  item?: string | null;
  quantity?: number | null;
  unit?: string | null;
  category?: string | null;
  raw_transcript: string;
  confidence?: number;
}
