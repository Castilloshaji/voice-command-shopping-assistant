export interface Suggestion {
  product_id?: number | null;
  item_name: string;
  category?: string | null;
  reason: string;
  score: number;
}
