import React, { useState, useEffect, useCallback } from 'react';
import '../styles/JokeGenerator.css';

const API_BASE = '/api/v1/tools';

const CATEGORY_ICONS = {
  any: '🎲',
  general: '😄',
  programming: '💻',
  'knock-knock': '🚪',
  dark: '🖤',
  pun: '🥁',
};

const CATEGORY_LABELS = {
  any: 'Any',
  general: 'General',
  programming: 'Programming',
  'knock-knock': 'Knock-Knock',
  dark: 'Dark',
  pun: 'Pun',
};

export default function JokeGenerator() {
  const [joke, setJoke] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [category, setCategory] = useState('any');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPunchline, setShowPunchline] = useState(false);
  const [stats, setStats] = useState({ total: 0, categories: {} });
  const [activeTab, setActiveTab] = useState('generator'); // 'generator' | 'favorites'
  const [safeMode, setSafeMode] = useState(true);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    fetchFavorites();
    fetchJoke();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchJoke = useCallback(async () => {
    setLoading(true);
    setError(null);
    setShowPunchline(false);
    try {
      const params = new URLSearchParams({ category, safe: safeMode });
      const res = await fetch(`${API_BASE}/jokes?${params}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to fetch joke');
      }
      const data = await res.json();
      setJoke(data);
      setStats((prev) => {
        const cats = { ...prev.categories };
        cats[data.category] = (cats[data.category] || 0) + 1;
        return { total: prev.total + 1, categories: cats };
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [category, safeMode]);

  const fetchFavorites = async () => {
    try {
      const res = await fetch(`${API_BASE}/jokes/favorites`);
      if (res.ok) {
        setFavorites(await res.json());
      }
    } catch {
      // non-fatal
    }
  };

  const saveFavorite = async () => {
    if (!joke) return;
    try {
      const body = {
        joke_id: joke.id,
        category: joke.category,
        setup: joke.setup,
        delivery: joke.delivery,
        joke_text: joke.joke,
        is_two_part: joke.is_two_part,
      };
      const res = await fetch(`${API_BASE}/jokes/favorites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok || res.status === 201) {
        await fetchFavorites();
      }
    } catch {
      // non-fatal
    }
  };

  const removeFavorite = async (jokeId) => {
    try {
      await fetch(`${API_BASE}/jokes/favorites/${jokeId}`, { method: 'DELETE' });
      setFavorites((prev) => prev.filter((f) => f.joke_id !== jokeId));
    } catch {
      // non-fatal
    }
  };

  const isAlreadyFavorite = joke && favorites.some((f) => f.joke_id === joke.id);

  const shareJoke = () => {
    if (!joke) return;
    const text = joke.is_two_part
      ? `${joke.setup}\n${joke.delivery}`
      : joke.joke;
    if (navigator.share) {
      navigator.share({ text });
    } else {
      navigator.clipboard.writeText(text);
      showToast('Joke copied to clipboard! 📋');
    }
  };

  return (
    <div className="joke-generator">
      {/* Toast notification */}
      {toast && <div className="toast">{toast}</div>}
      <div className="joke-header">
        <h2>😂 Joke Generator</h2>
        <p className="joke-subtitle">Powered by JokeAPI · {stats.total} jokes generated this session</p>
      </div>

      {/* Stats bar */}
      {stats.total > 0 && (
        <div className="stats-bar">
          {Object.entries(stats.categories).map(([cat, count]) => (
            <span key={cat} className="stat-chip">
              {CATEGORY_ICONS[cat] || '😄'} {cat}: {count}
            </span>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'generator' ? 'active' : ''}`}
          onClick={() => setActiveTab('generator')}
        >
          🎲 Generator
        </button>
        <button
          className={`tab-btn ${activeTab === 'favorites' ? 'active' : ''}`}
          onClick={() => setActiveTab('favorites')}
        >
          ⭐ Favorites ({favorites.length})
        </button>
      </div>

      {/* Generator tab */}
      {activeTab === 'generator' && (
        <div className="generator-panel">
          {/* Controls */}
          <div className="controls">
            <div className="category-selector">
              {Object.keys(CATEGORY_ICONS).map((cat) => (
                <button
                  key={cat}
                  className={`category-btn ${category === cat ? 'active' : ''}`}
                  onClick={() => setCategory(cat)}
                >
                  {CATEGORY_ICONS[cat]} {CATEGORY_LABELS[cat]}
                </button>
              ))}
            </div>
            <label className="safe-toggle">
              <input
                type="checkbox"
                checked={safeMode}
                onChange={(e) => setSafeMode(e.target.checked)}
              />
              &nbsp;Safe mode
            </label>
          </div>

          {/* Joke card */}
          <div className="joke-card">
            {loading && (
              <div className="loading-spinner">
                <span className="spinner" />
                <p>Fetching a hilarious joke…</p>
              </div>
            )}

            {error && !loading && (
              <div className="error-msg">
                <span>⚠️</span> {error}
              </div>
            )}

            {joke && !loading && !error && (
              <div className="joke-content">
                <span className={`category-badge cat-${joke.category}`}>
                  {CATEGORY_ICONS[joke.category] || '😄'} {joke.category}
                </span>

                {joke.is_two_part ? (
                  <div className="two-part-joke">
                    <p className="joke-setup">{joke.setup}</p>
                    {!showPunchline ? (
                      <button
                        className="reveal-btn"
                        onClick={() => setShowPunchline(true)}
                      >
                        👇 Reveal punchline
                      </button>
                    ) : (
                      <p className="joke-delivery">🥁 {joke.delivery}</p>
                    )}
                  </div>
                ) : (
                  <p className="joke-single">{joke.joke}</p>
                )}

                <div className="joke-actions">
                  <button
                    className={`action-btn favorite-btn ${isAlreadyFavorite ? 'saved' : ''}`}
                    onClick={saveFavorite}
                    disabled={isAlreadyFavorite}
                    title={isAlreadyFavorite ? 'Already saved' : 'Save to favorites'}
                  >
                    {isAlreadyFavorite ? '⭐ Saved' : '☆ Favorite'}
                  </button>
                  <button className="action-btn share-btn" onClick={shareJoke} title="Share joke">
                    📤 Share
                  </button>
                </div>
              </div>
            )}
          </div>

          <button
            className="generate-btn"
            onClick={fetchJoke}
            disabled={loading}
          >
            {loading ? '⏳ Loading…' : '🎲 Generate New Joke'}
          </button>
        </div>
      )}

      {/* Favorites tab */}
      {activeTab === 'favorites' && (
        <div className="favorites-panel">
          {favorites.length === 0 ? (
            <div className="empty-favorites">
              <p>⭐ No favorites yet – generate some jokes and save them!</p>
            </div>
          ) : (
            <div className="favorites-list">
              {favorites.map((fav) => (
                <div key={fav.joke_id} className="favorite-card">
                  <span className={`category-badge cat-${fav.category}`}>
                    {CATEGORY_ICONS[fav.category] || '😄'} {fav.category}
                  </span>
                  {fav.is_two_part ? (
                    <>
                      <p className="joke-setup">{fav.setup}</p>
                      <p className="joke-delivery">🥁 {fav.delivery}</p>
                    </>
                  ) : (
                    <p className="joke-single">{fav.joke_text}</p>
                  )}
                  <button
                    className="remove-btn"
                    onClick={() => removeFavorite(fav.joke_id)}
                    title="Remove from favorites"
                  >
                    🗑️ Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
