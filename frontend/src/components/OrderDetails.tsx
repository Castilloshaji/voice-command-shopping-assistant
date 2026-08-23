import React from 'react';
import { Order } from '../types/checkout';
import { formatCurrency } from '../utils/currency';

interface OrderDetailsProps {
  order: Order | null;
  isOpen: boolean;
  onClose: () => void;
}

export const OrderDetails: React.FC<OrderDetailsProps> = ({ order, isOpen, onClose }) => {
  if (!isOpen || !order) return null;

  const formatDate = (isoStr: string) => {
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal-content order-details-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="order-details-title"
        aria-modal="true"
      >
        <header className="modal-header">
          <div>
            <h2 id="order-details-title">Order #{order.order_number}</h2>
            <p className="order-date">{formatDate(order.created_at)}</p>
          </div>
          <button
            type="button"
            className="close-button"
            onClick={onClose}
            aria-label="Close order details modal"
          >
            &times;
          </button>
        </header>

        <div className="modal-body">
          <div className="order-status-badge">
            <span className="badge badge-success">{order.status}</span>
          </div>

          <div className="purchased-items-list">
            <h3>Purchased Items ({order.items.length})</h3>
            {order.items.map((item) => (
              <div key={item.id} className="purchased-item-row">
                <div className="item-info">
                  <strong>{item.product_name_snapshot}</strong>
                  {item.brand_snapshot && <span className="item-brand"> &bull; {item.brand_snapshot}</span>}
                  <p className="qty-unit-snapshot">
                    {item.quantity} {item.unit || ''} &times; {formatCurrency(item.unit_price)}
                  </p>
                </div>
                <div className="item-price">
                  <span>{formatCurrency(item.line_total)}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="order-summary-box">
            <div className="summary-row">
              <span>Subtotal</span>
              <span>{formatCurrency(order.subtotal)}</span>
            </div>
            <div className="summary-row">
              <span>Discount</span>
              <span>{formatCurrency(order.discount)}</span>
            </div>
            <div className="summary-row total-row">
              <strong>Total</strong>
              <strong>{formatCurrency(order.total)}</strong>
            </div>
          </div>
        </div>

        <footer className="modal-footer">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
            style={{ minHeight: '44px' }}
          >
            Close
          </button>
        </footer>
      </div>
    </div>
  );
};
