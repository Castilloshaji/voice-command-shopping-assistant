import { useEffect, useState } from 'react';
import { apiService, HealthCheckResponse } from './services/api';

export function App() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiService.getHealth()
      .then(setHealth)
      .catch((err) => setError(err.message || 'Health check failed'));
  }, []);

  return (
    <main className="container">
      <header className="header">
        <h1 className="title">Voice Command Shopping Assistant</h1>
        <span className="badge">Phase 1 — Foundation Initialized</span>
      </header>

      <section className="status-card">
        <h3>Backend API Connection</h3>
        {error ? (
          <p style={{ color: '#ef4444', marginTop: '0.5rem' }}>Status: Disconnected ({error})</p>
        ) : health ? (
          <p style={{ color: '#22c55e', marginTop: '0.5rem' }}>
            Status: Connected ({health.app} v{health.version})
          </p>
        ) : (
          <p style={{ marginTop: '0.5rem' }}>Checking backend health...</p>
        )}
      </section>
    </main>
  );
}

export default App;
