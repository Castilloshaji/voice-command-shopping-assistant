export interface CheckoutSubstitute {
  product_id: number;
  name: string;
  brand?: string | null;
  price: number;
}

export interface CheckoutItem {
  product_id?: number | null;
  name: string;
  brand?: string | null;
  quantity: number;
  unit?: string | null;
  unit_price: number;
  line_total: number;
  is_available: boolean;
  substitutes?: CheckoutSubstitute[];
}

export interface CheckoutPreview {
  items: CheckoutItem[];
  subtotal: number;
  discount: number;
  total: number;
  item_count: number;
  has_unavailable: boolean;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id?: number | null;
  product_name_snapshot: string;
  brand_snapshot?: string | null;
  quantity: number;
  unit?: string | null;
  unit_price: number;
  line_total: number;
}

export interface Order {
  id: number;
  order_number: string;
  status: string;
  subtotal: number;
  discount: number;
  total: number;
  created_at: string;
  items: OrderItem[];
}
