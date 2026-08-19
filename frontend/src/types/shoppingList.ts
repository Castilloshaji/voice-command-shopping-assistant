export interface ListItem {
  id: number;
  product_id?: number | null;
  item_name: string;
  category?: string | null;
  quantity: number;
  unit?: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface ListItemCreate {
  item_name: string;
  product_id?: number | null;
  category?: string | null;
  quantity?: number;
  unit?: string | null;
}

export interface ListItemUpdate {
  quantity?: number;
  unit?: string | null;
  is_completed?: boolean;
}
