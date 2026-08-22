import React, { useState } from 'react';
import { VoiceAssistant } from './components/VoiceAssistant';
import { ShoppingList } from './components/ShoppingList';
import { ProductSearch } from './components/ProductSearch';
import { Recommendations } from './components/Recommendations';

export const App: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const triggerRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
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
        <span className="header-status"><span aria-hidden="true" /> Voice ready</span>
      </header>

      {/* Main Responsive Grid Layout */}
      <main>
        <div className="app-main-grid">
          <section className="voice-panel" aria-label="Voice Command Assistant Module">
            <VoiceAssistant onCommandExecuted={triggerRefresh} />
          </section>
        </div>
        <div className="content-grid">
          <section aria-label="Shopping List Manager Module">
            <ShoppingList onListChange={triggerRefresh} refreshTrigger={refreshTrigger} />
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
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Shop smarter, one command at a time.</p>
      </footer>
    </div>
  );
};

export default App;
