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
        <div className="header-title-group">
          <h1>Voice Command Shopping Assistant</h1>
          <p className="app-subtitle">Smart Local Voice & Catalog Shopping Assistant</p>
        </div>
      </header>

      {/* Main Responsive Grid Layout */}
      <main className="app-main-grid">
        {/* Primary Left Column */}
        <div className="layout-column column-left">
          <section aria-label="Voice Command Assistant Module">
            <VoiceAssistant onCommandExecuted={triggerRefresh} />
          </section>

          <section aria-label="Shopping List Manager Module">
            <ShoppingList onListChange={triggerRefresh} refreshTrigger={refreshTrigger} />
          </section>
        </div>

        {/* Secondary Right Column */}
        <div className="layout-column column-right">
          <section aria-label="Smart Recommendations Module">
            <Recommendations onItemAdded={triggerRefresh} refreshTrigger={refreshTrigger} />
          </section>

          <section aria-label="Product Catalog Search Module">
            <ProductSearch onItemAdded={triggerRefresh} />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Voice Command Shopping Assistant • Built with React & FastAPI • 100% Deterministic & Local</p>
      </footer>
    </div>
  );
};

export default App;
