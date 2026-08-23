import React, { useState, useEffect } from 'react';
import { Order } from '../types/checkout';
import { apiService } from '../services/api';
import { OrderDetails } from './OrderDetails';
import { formatCurrency } from '../utils/currency';

export const OrderHistory: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getOrders();
      setOrders(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch order history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const formatDate = (isoStr: string) => {
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="section-card order-history-card">
      <header className="card-header">
        <h2>Order History</h2>
        <button
          type="button"
          className="btn btn-sm btn-outline"
          onClick={fetchOrders}
          title="Refresh orders"
        >
          Refresh
        </button>
      </header>

      {loading && <p className="status-processing">Loading order history...</p>}

      {error && (
        <div className="alert alert-error" role="alert">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && orders.length === 0 && (
        <p className="empty-history-msg">No orders placed yet.</p>
      )}

      {!loading && orders.length > 0 && (
        <div className="orders-list">
          {orders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="order-main-info">
                <span className="order-number">{order.order_number}</span>
                <span className="order-date">{formatDate(order.created_at)}</span>
              </div>

              <div className="order-meta">
                <span className="item-count">{order.items.length} items</span>
                <span className="order-total">{formatCurrency(order.total)}</span>
                <span className="badge badge-success">{order.status}</span>
              </div>

              <div className="order-actions">
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  onClick={() => setSelectedOrder(order)}
                  style={{ minHeight: '44px' }}
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <OrderDetails
        order={selectedOrder}
        isOpen={selectedOrder !== null}
        onClose={() => setSelectedOrder(null)}
      />
    </div>
  );
};
