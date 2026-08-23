import React, { useState, useEffect } from 'react';
import { CheckoutPreview, Order } from '../types/checkout';
import { apiService } from '../services/api';
import { formatCurrency } from '../utils/currency';

interface CheckoutProps {
  isOpen: boolean;
  onClose: () => void;
  onOrderPlaced: (order: Order) => void;
  onAddItem: (itemName: string) => void;
}

export const Checkout: React.FC<CheckoutProps> = ({
  isOpen,
  onClose,
  onOrderPlaced,
  onAddItem,
}) => {
  const [preview, setPreview] = useState<CheckoutPreview | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [placingOrder, setPlacingOrder] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [placedOrder, setPlacedOrder] = useState<Order | null>(null);

  const fetchPreview = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getCheckoutPreview();
      setPreview(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load checkout review.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      setPlacedOrder(null);
      fetchPreview();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handlePlaceOrder = async () => {
    if (!preview || preview.has_unavailable || preview.item_count === 0) return;
    setPlacingOrder(true);
    setError(null);

    try {
      const order = await apiService.placeOrder();
      setPlacedOrder(order);
      onOrderPlaced(order);
    } catch (err: any) {
      setError(err.message || 'Failed to place order.');
    } finally {
      setPlacingOrder(false);
    }
  };

  const handleAddSubstitute = async (substituteName: string) => {
    onAddItem(substituteName);
    // Refresh preview after adding substitute
    setTimeout(() => {
      fetchPreview();
    }, 300);
  };

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal-content checkout-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="checkout-title"
        aria-modal="true"
      >
        {!placedOrder ? (
          <>
            <header className="modal-header">
              <h2 id="checkout-title">Review Your Order</h2>
              <button
                type="button"
                className="close-button"
                onClick={onClose}
                aria-label="Close review order modal"
              >
                &times;
              </button>
            </header>

            <div className="modal-body">
              {loading && <p className="status-processing">Loading order review...</p>}

              {error && (
                <div className="alert alert-error" role="alert">
                  <p>{error}</p>
                </div>
              )}

              {preview && !loading && (
                <>
                  {preview.items.length === 0 ? (
                    <p className="empty-cart-msg">Your shopping list is empty.</p>
                  ) : (
                    <div className="checkout-items-list">
                      {preview.items.map((item, idx) => (
                        <div key={idx} className={`checkout-item-row ${!item.is_available ? 'unavailable-row' : ''}`}>
                          <div className="item-details">
                            <h3 className="item-name">{item.name}</h3>
                            {item.brand && <span className="item-brand">{item.brand}</span>}
                            <p className="item-qty-price">
                              {item.quantity} {item.unit || ''} &times; {formatCurrency(item.unit_price)}
                            </p>
                          </div>

                          <div className="item-price-status">
                            <span className="line-total">{formatCurrency(item.line_total)}</span>
                            {!item.is_available && (
                              <span className="badge badge-unavailable">UNAVAILABLE</span>
                            )}
                          </div>

                          {!item.is_available && item.substitutes && item.substitutes.length > 0 && (
                            <div className="substitute-box">
                              <p className="substitute-label">Possible substitute:</p>
                              {item.substitutes.slice(0, 1).map((sub) => (
                                <div key={sub.product_id} className="substitute-row">
                                  <span>{sub.name} &mdash; {formatCurrency(sub.price)}</span>
                                  <button
                                    type="button"
                                    className="btn btn-sm btn-outline"
                                    onClick={() => handleAddSubstitute(sub.name)}
                                  >
                                    Add Substitute
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="checkout-summary">
                    <div className="summary-row">
                      <span>Subtotal</span>
                      <span>{formatCurrency(preview.subtotal)}</span>
                    </div>
                    <div className="summary-row">
                      <span>Savings</span>
                      <span>{formatCurrency(preview.discount)}</span>
                    </div>
                    <div className="summary-row total-row">
                      <strong>Total</strong>
                      <strong>{formatCurrency(preview.total)}</strong>
                    </div>
                  </div>
                </>
              )}
            </div>

            <footer className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                style={{ minHeight: '44px' }}
              >
                Back
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handlePlaceOrder}
                disabled={!preview || preview.has_unavailable || preview.item_count === 0 || placingOrder}
                style={{ minHeight: '44px' }}
              >
                {placingOrder ? 'Placing Order...' : 'Place Order'}
              </button>
            </footer>
          </>
        ) : (
          /* SUCCESS INTERFACE */
          <div className="checkout-success-view" aria-live="polite">
            <div className="success-icon" aria-hidden="true">&check;</div>
            <h2>Order placed successfully!</h2>
            <p className="order-number">Order #{placedOrder.order_number}</p>
            <p className="order-info">
              {placedOrder.items.length} items &bull; Total {formatCurrency(placedOrder.total)}
            </p>
            <p className="order-subtext">Your grocery order has been recorded.</p>

            <div className="success-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                style={{ minHeight: '44px' }}
              >
                Continue Shopping
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={onClose}
                style={{ minHeight: '44px' }}
              >
                View Order
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
