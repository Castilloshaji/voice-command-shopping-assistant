import React from 'react';
import { VoiceAssistant } from './components/VoiceAssistant';

export const App: React.FC = () => {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Voice Command Shopping Assistant</h1>
        <p className="app-subtitle">Phase 4 - Browser Voice Input & Intent Preview</p>
      </header>

      <main className="app-main">
        <VoiceAssistant />
      </main>

      <footer className="app-footer">
        <p>Voice Command Shopping Assistant - Built with React & FastAPI</p>
      </footer>
    </div>
  );
};

export default App;
