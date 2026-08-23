import React, { useState } from 'react';
import { VoiceAssistant } from './components/VoiceAssistant';
import { ShoppingList } from './components/ShoppingList';
import { ProductSearch } from './components/ProductSearch';
import { Recommendations } from './components/Recommendations';
import { Checkout } from './components/Checkout';
import { OrderHistory } from './components/OrderHistory';
import { apiService } from './services/api';

export const App: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'SHOPPING' | 'ORDERS'>('SHOPPING');

  const triggerRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleAddItemFromCheckout = async (itemName: string) => {
    try {
      await apiService.createShoppingItem({ item_name: itemName, quantity: 1 });
      triggerRefresh();
    } catch (err) {
      console.error('Failed to add substitute item:', err);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">S</span>
          <div className="header-title-group">
            <p className="eyebrow">Your everyday assistant</p>
            <h1>Shop by voice.</h1>
            <p className="app-subtitle">Build your list, discover products, and stay one step ahead.</p>
          </div>
        </div>

        <div className="header-right-actions" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div className="tab-navigation" role="tablist" aria-label="Main view tabs">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'SHOPPING'}
              className={`btn btn-sm ${activeTab === 'SHOPPING' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setActiveTab('SHOPPING')}
            >
              Shopping List
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'ORDERS'}
              className={`btn btn-sm ${activeTab === 'ORDERS' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setActiveTab('ORDERS')}
            >
              Order History
            </button>
          </div>
          <span className="header-status"><span aria-hidden="true" /> Voice ready</span>
        </div>
      </header>

      {/* Main Responsive Grid Layout */}
      <main>
        <div className="app-main-grid">
          <section className="voice-panel" aria-label="Voice Command Assistant Module">
            <VoiceAssistant onCommandExecuted={triggerRefresh} />
          </section>
        </div>

        {activeTab === 'SHOPPING' ? (
          <>
            <div className="content-grid">
              <section aria-label="Shopping List Manager Module">
                <ShoppingList
                  onListChange={triggerRefresh}
                  refreshTrigger={refreshTrigger}
                  onOpenCheckout={() => setIsCheckoutOpen(true)}
                />
              </section>
              <section aria-label="Smart Recommendations Module">
                <Recommendations onItemAdded={triggerRefresh} refreshTrigger={refreshTrigger} />
              </section>
            </div>
            <div className="discovery-panel">
              <section aria-label="Product Catalog Search Module">
                <ProductSearch onItemAdded={triggerRefresh} />
              </section>
            </div>
          </>
        ) : (
          <div className="orders-panel" style={{ marginTop: '1.5rem' }}>
            <section aria-label="Order History Module">
              <OrderHistory />
            </section>
          </div>
        )}
      </main>

      {/* Checkout Modal */}
      <Checkout
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        onOrderPlaced={() => {
          triggerRefresh();
          setActiveTab('ORDERS');
        }}
        onAddItem={handleAddItemFromCheckout}
      />

      {/* Footer */}
      <footer className="app-footer">
        <p>Shop smarter, one command at a time.</p>
      </footer>
    </div>
  );
};

export default App;
