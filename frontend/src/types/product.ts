export interface Product {
  id: number;
  name: string;
  category: string;
  brand?: string | null;
  price: number;
  size?: string | null;
  is_available: boolean;
  season?: string | null;
  substitutes?: string[];
}
