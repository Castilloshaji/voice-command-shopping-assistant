import React, { useState, useEffect, useCallback } from 'react';
import { apiService, ProductSearchParams } from '../services/api';
import { Product } from '../types/product';
import { formatCurrency } from '../utils/currency';

interface ProductSearchProps {
  onItemAdded?: () => void;
}

export const ProductSearch: React.FC<ProductSearchProps> = ({ onItemAdded }) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [addingId, setAddingId] = useState<number | null>(null);
  const [addMessage, setAddMessage] = useState<string | null>(null);

  const fetchProducts = useCallback(async (params?: ProductSearchParams) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.searchProducts(params);
      setProducts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to search products.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();

    if (!query) {
      fetchProducts();
      return;
    }

    try {
      const parsed = await apiService.parseVoiceCommand(`Find ${query}`);
      if (parsed.intent === 'SEARCH_PRODUCT') {
        fetchProducts({
          query: parsed.item || undefined,
          brand: parsed.brand || undefined,
          min_price: parsed.min_price ?? undefined,
          max_price: parsed.max_price ?? undefined,
        });
        return;
      }
    } catch {
      // Fall through to literal catalog search to preserve basic search availability.
    }

    fetchProducts({ query });
  };

  const handleQuickFilter = (query?: string, maxPrice?: number) => {
    setSearchQuery(query || '');
    fetchProducts({
      query: query || undefined,
      max_price: maxPrice,
    });
  };

  const handleAddToList = async (prod: Product) => {
    setAddingId(prod.id);
    setAddMessage(null);
    try {
      await apiService.createShoppingItem({
        item_name: prod.name,
        product_id: prod.id,
        quantity: 1.0,
      });
      setAddMessage(`Added '${prod.name}' to shopping list.`);
      if (onItemAdded) onItemAdded();
    } catch (err: any) {
      setError(err.message || `Failed to add ${prod.name} to list.`);
    } finally {
      setAddingId(null);
      setTimeout(() => setAddMessage(null), 3000);
    }
  };

  return (
    <div className="section-card search-card">
      <header className="section-header">
        <div className="title-group">
          <p className="eyebrow">Discover</p>
          <h2>Find products you&apos;ll love</h2>
          <p className="section-intro">Search the catalog or start with a quick pick.</p>
        </div>
      </header>

      {/* Search Input & Controls */}
      <form className="search-form" onSubmit={handleSearchSubmit}>
        <div className="search-input-group">
          <input
            type="text"
            className="search-input"
            placeholder="Search products by name, category, or brand..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search products input"
          />
          <button type="submit" className="btn btn-primary search-btn" disabled={isLoading}>
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* Quick Filter Tags */}
        <div className="quick-filters">
          <span className="filter-label">Quick Filters:</span>
          <button
            type="button"
            className="tag-btn"
            onClick={() => handleQuickFilter('Toothpaste')}
          >
            Toothpaste
          </button>
          <button
            type="button"
            className="tag-btn"
            onClick={() => handleQuickFilter('Dairy')}
          >
            Dairy
          </button>
          <button
            type="button"
            className="tag-btn"
            onClick={() => handleQuickFilter(undefined, 100.0)}
          >
            Under ₹100
          </button>
          <button
            type="button"
            className="tag-btn tag-clear"
            onClick={() => handleQuickFilter('')}
          >
            All Products
          </button>
        </div>
      </form>

      {/* Action Notification */}
      {addMessage && (
        <div className="alert alert-success" role="status" aria-live="polite">
          <span>✓ {addMessage}</span>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="alert alert-error" role="alert">
          <span>{error}</span>
        </div>
      )}

      {/* Product Results List */}
      {isLoading ? (
        <div className="loading-spinner-box" aria-live="polite">
          <div className="spinner" />
          <p>Searching products...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="empty-state-box">
          <span className="empty-icon">🔍</span>
          <p className="empty-text">No products found matching your criteria.</p>
        </div>
      ) : (
        <div className="product-results-grid">
          {products.map((prod) => (
            <div key={prod.id} className={`product-card ${!prod.is_available ? 'unavailable-card' : ''}`}>
              <div className="product-card-header">
                <h3 className="product-card-name">{prod.name}</h3>
                <span className="product-card-price">{formatCurrency(prod.price)}</span>
              </div>

              <div className="product-card-meta">
                {prod.brand && <span className="brand-badge">{prod.brand}</span>}
                <span className="cat-badge">{prod.category}</span>
                {prod.size && <span className="size-badge">{prod.size}</span>}
                <span className={`avail-badge ${prod.is_available ? 'in-stock' : 'out-of-stock'}`}>
                  {prod.is_available ? 'In Stock' : 'UNAVAILABLE'}
                </span>
              </div>

              {/* Action for Available Products */}
              {prod.is_available && (
                <div className="product-card-actions">
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => handleAddToList(prod)}
                    disabled={addingId === prod.id}
                    aria-label={`Add ${prod.name} to shopping list`}
                  >
                    {addingId === prod.id ? 'Adding...' : '+ Add to List'}
                  </button>
                </div>
              )}

              {/* Substitutes Callout for Unavailable Products */}
              {!prod.is_available && (
                <div className="substitutes-section">
                  <span className="substitutes-title">Possible Substitutes:</span>
                  {prod.substitute_products && prod.substitute_products.length > 0 ? (
                    <ul className="substitutes-list">
                      {prod.substitute_products.map((sub) => (
                        <li key={sub.id} className="substitute-row">
                          <span className="sub-name">↪ {sub.name}</span>
                          <span className="sub-price">{formatCurrency(sub.price)}</span>
                          <button
                            type="button"
                            className="btn btn-xs btn-outline-success"
                            onClick={() => handleAddToList(sub)}
                            disabled={addingId === sub.id}
                            aria-label={`Add substitute ${sub.name} to shopping list`}
                          >
                            + Add Substitute
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="no-substitutes-text">No direct substitutes available in catalog.</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
