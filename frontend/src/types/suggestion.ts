export interface Suggestion {
  product_id?: number | null;
  item_name: string;
  product?: string | null;
  category?: string | null;
  reason: string;
  score: number;
  is_substitute?: boolean;
  substitute_for?: string | null;
}

