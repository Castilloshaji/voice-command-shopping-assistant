import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { ListItem } from '../types/shoppingList';
import { ConfirmModal } from './ConfirmModal';

interface ShoppingListProps {
  onListChange?: () => void;
  refreshTrigger?: number;
}

export const ShoppingList: React.FC<ShoppingListProps> = ({ onListChange, refreshTrigger }) => {
  const [items, setItems] = useState<ListItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showClearModal, setShowClearModal] = useState<boolean>(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.getShoppingList();
      setItems(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load shopping list.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems, refreshTrigger]);

  const handleToggleComplete = async (item: ListItem) => {
    setUpdatingId(item.id);
    try {
      const updated = await apiService.updateShoppingItem(item.id, {
        is_completed: !item.is_completed,
      });
      setItems((prev) => prev.map((i) => (i.id === updated.id ? updated : i)));
      if (onListChange) onListChange();
    } catch (err: any) {
      setError(err.message || 'Failed to update item status.');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleQuantityChange = async (item: ListItem, delta: number) => {
    const newQty = item.quantity + delta;
    if (newQty <= 0) return; // Prevent non-positive quantities

    setUpdatingId(item.id);
    try {
      const updated = await apiService.updateShoppingItem(item.id, {
        quantity: newQty,
      });
      setItems((prev) => prev.map((i) => (i.id === updated.id ? updated : i)));
      if (onListChange) onListChange();
    } catch (err: any) {
      setError(err.message || 'Failed to update quantity.');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDeleteItem = async (id: number) => {
    setUpdatingId(id);
    try {
      await apiService.deleteShoppingItem(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
      if (onListChange) onListChange();
    } catch (err: any) {
      setError(err.message || 'Failed to delete item.');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleConfirmClear = async () => {
    setShowClearModal(false);
    setIsLoading(true);
    try {
      await apiService.clearShoppingList();
      setItems([]);
      if (onListChange) onListChange();
    } catch (err: any) {
      setError(err.message || 'Failed to clear shopping list.');
    } finally {
      setIsLoading(false);
    }
  };

  const activeItems = items.filter((i) => !i.is_completed);
  const completedItems = items.filter((i) => i.is_completed);

  return (
    <div className="section-card shopping-list-card">
      <header className="section-header">
        <div className="title-group">
          <h2>Shopping List</h2>
          <span className="badge count-badge" aria-label={`${activeItems.length} active items`}>
            {activeItems.length} Active
          </span>
        </div>
        {items.length > 0 && (
          <button
            type="button"
            className="btn btn-sm btn-outline-danger"
            onClick={() => setShowClearModal(true)}
            aria-label="Clear shopping list"
          >
            Clear List
          </button>
        )}
      </header>

      {error && (
        <div className="alert alert-error" role="alert">
          <span>{error}</span>
          <button type="button" className="btn btn-sm btn-outline" onClick={fetchItems}>
            Retry
          </button>
        </div>
      )}

      {isLoading && items.length === 0 ? (
        <div className="loading-spinner-box" aria-live="polite">
          <div className="spinner" />
          <p>Loading shopping list...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="empty-state-box">
          <span className="empty-icon">🛒</span>
          <p className="empty-text">Your shopping list is empty.</p>
          <p className="empty-subtext">Use voice commands or product search to add items.</p>
        </div>
      ) : (
        <div className="shopping-list-content">
          {/* Active Items */}
          {activeItems.length > 0 && (
            <ul className="item-list active-item-list" aria-label="Active shopping list items">
              {activeItems.map((item) => (
                <li key={item.id} className={`item-row ${updatingId === item.id ? 'updating' : ''}`}>
                  <label className="checkbox-container">
                    <input
                      type="checkbox"
                      checked={item.is_completed}
                      onChange={() => handleToggleComplete(item)}
                      disabled={updatingId === item.id}
                      aria-label={`Mark ${item.item_name} as completed`}
                    />
                    <span className="checkmark" />
                  </label>

                  <div className="item-info">
                    <span className="item-title">{item.item_name}</span>
                    {item.category && <span className="cat-badge">{item.category}</span>}
                  </div>

                  <div className="item-controls">
                    <div className="qty-picker">
                      <button
                        type="button"
                        className="qty-btn"
                        onClick={() => handleQuantityChange(item, -1)}
                        disabled={item.quantity <= 1 || updatingId === item.id}
                        aria-label={`Decrease quantity for ${item.item_name}`}
                      >
                        −
                      </button>
                      <span className="qty-value">
                        {item.quantity} {item.unit || ''}
                      </span>
                      <button
                        type="button"
                        className="qty-btn"
                        onClick={() => handleQuantityChange(item, 1)}
                        disabled={updatingId === item.id}
                        aria-label={`Increase quantity for ${item.item_name}`}
                      >
                        +
                      </button>
                    </div>

                    <button
                      type="button"
                      className="icon-btn delete-btn"
                      onClick={() => handleDeleteItem(item.id)}
                      disabled={updatingId === item.id}
                      aria-label={`Delete ${item.item_name}`}
                      title="Remove item"
                    >
                      ✕
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {/* Completed Items */}
          {completedItems.length > 0 && (
            <div className="completed-section">
              <h3 className="completed-header">Completed ({completedItems.length})</h3>
              <ul className="item-list completed-item-list" aria-label="Completed shopping list items">
                {completedItems.map((item) => (
                  <li key={item.id} className={`item-row completed-row ${updatingId === item.id ? 'updating' : ''}`}>
                    <label className="checkbox-container">
                      <input
                        type="checkbox"
                        checked={item.is_completed}
                        onChange={() => handleToggleComplete(item)}
                        disabled={updatingId === item.id}
                        aria-label={`Mark ${item.item_name} as incomplete`}
                      />
                      <span className="checkmark" />
                    </label>

                    <div className="item-info">
                      <span className="item-title completed-title">{item.item_name}</span>
                      {item.category && <span className="cat-badge muted">{item.category}</span>}
                    </div>

                    <div className="item-controls">
                      <span className="qty-value muted">
                        {item.quantity} {item.unit || ''}
                      </span>

                      <button
                        type="button"
                        className="icon-btn delete-btn"
                        onClick={() => handleDeleteItem(item.id)}
                        disabled={updatingId === item.id}
                        aria-label={`Delete completed ${item.item_name}`}
                        title="Remove item"
                      >
                        ✕
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Confirmation Modal for Clear List */}
      <ConfirmModal
        isOpen={showClearModal}
        title="Clear Shopping List"
        message="Are you sure you want to remove all items from your shopping list? This action cannot be undone."
        confirmLabel="Clear All Items"
        cancelLabel="Cancel"
        isDestructive={true}
        onConfirm={handleConfirmClear}
        onCancel={() => setShowClearModal(false)}
      />
    </div>
  );
};
