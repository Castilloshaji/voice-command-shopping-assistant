import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { Suggestion } from '../types/suggestion';

interface RecommendationsProps {
  onItemAdded?: () => void;
  refreshTrigger?: number;
}

export const Recommendations: React.FC<RecommendationsProps> = ({ onItemAdded, refreshTrigger }) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [addingName, setAddingName] = useState<string | null>(null);
  const [addMessage, setAddMessage] = useState<string | null>(null);

  const fetchSuggestions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.getSuggestions(5);
      setSuggestions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch recommendations.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSuggestions();
  }, [fetchSuggestions, refreshTrigger]);

  const handleAddToList = async (sugg: Suggestion) => {
    const itemName = sugg.product || sugg.item_name;
    setAddingName(itemName);
    setAddMessage(null);
    try {
      await apiService.createShoppingItem({
        item_name: itemName,
        product_id: sugg.product_id || undefined,
        quantity: 1.0,
      });
      setAddMessage(`Added '${itemName}' to shopping list.`);
      if (onItemAdded) onItemAdded();
    } catch (err: any) {
      setError(err.message || `Failed to add ${itemName} to list.`);
    } finally {
      setAddingName(null);
      setTimeout(() => setAddMessage(null), 3000);
    }
  };

  return (
    <div className="section-card recommendations-card">
      <header className="section-header">
        <div className="title-group">
          <p className="eyebrow">For you</p>
          <h2>Helpful suggestions</h2>
          <p className="section-intro">A few thoughtful picks for your next shop.</p>
        </div>
        <button
          type="button"
          className="btn btn-sm btn-outline-secondary"
          onClick={fetchSuggestions}
          disabled={isLoading}
          aria-label="Refresh recommendations"
        >
          {isLoading ? 'Refreshing...' : '↻ Refresh'}
        </button>
      </header>

      {/* Action Notification */}
      {addMessage && (
        <div className="alert alert-success" role="status" aria-live="polite">
          <span>✓ {addMessage}</span>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="alert alert-error" role="alert">
          <span>{error}</span>
          <button type="button" className="btn btn-sm btn-outline" onClick={fetchSuggestions}>
            Retry
          </button>
        </div>
      )}

      {/* Recommendations Cards */}
      {isLoading && suggestions.length === 0 ? (
        <div className="loading-spinner-box" aria-live="polite">
          <div className="spinner" />
          <p>Loading smart recommendations...</p>
        </div>
      ) : suggestions.length === 0 ? (
        <div className="empty-state-box">
          <span className="empty-icon">💡</span>
          <p className="empty-text">No recommendations yet.</p>
          <p className="empty-subtext">Add or purchase items to build personalized suggestions.</p>
        </div>
      ) : (
        <div className="recommendations-list">
          {suggestions.map((sugg, idx) => {
            const displayName = sugg.product || sugg.item_name;
            return (
              <div key={sugg.product_id || idx} className="recommendation-item-card">
                <div className="rec-header">
                  <span className="rec-name">{displayName}</span>
                  <span className="score-badge" aria-label={`${sugg.score.toFixed(1)} relevance score`}>Great match</span>
                </div>

                <div className="rec-meta">
                  {sugg.category && <span className="cat-badge">{sugg.category}</span>}
                  <span className="reason-tag">💡 {sugg.reason}</span>
                </div>

                <div className="rec-actions">
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => handleAddToList(sugg)}
                    disabled={addingName === displayName}
                    aria-label={`Add recommended ${displayName} to shopping list`}
                  >
                    {addingName === displayName ? 'Adding...' : '+ Add to List'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
