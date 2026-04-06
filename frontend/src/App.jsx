import React, { useState } from 'react';
import JokeGenerator from './pages/JokeGenerator.jsx';
import './styles/global.css';

function App() {
  const [view, setView] = useState('jokes');

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌌 AI Universe</h1>
        <nav>
          <button
            onClick={() => setView('dashboard')}
            className={view === 'dashboard' ? 'nav-btn active' : 'nav-btn'}
          >
            Dashboard
          </button>
          <button
            onClick={() => setView('jokes')}
            className={view === 'jokes' ? 'nav-btn active' : 'nav-btn'}
          >
            😂 Joke Generator
          </button>
          <button
            onClick={() => setView('agents')}
            className={view === 'agents' ? 'nav-btn active' : 'nav-btn'}
          >
            Agents
          </button>
        </nav>
      </header>

      <main className="app-content">
        {view === 'dashboard' && (
          <div className="placeholder-view">
            <h2>📊 Dashboard</h2>
            <p>Coming soon – agent analytics and activity feed.</p>
          </div>
        )}
        {view === 'jokes' && <JokeGenerator />}
        {view === 'agents' && (
          <div className="placeholder-view">
            <h2>🤖 Agents</h2>
            <p>Coming soon – manage your AI agents here.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
