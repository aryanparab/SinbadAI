"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useGameContext } from '@/components/GameContext';

export default function HomeScreen() {
  const { data: session } = useSession();
  const session_id = session?.user?.email || "guest_session";
  const router = useRouter();

  const [hasSavedGame, setHasSavedGame] = useState(false);
  const [loading, setLoading] = useState(true);
  const [worldName, setWorldName] = useState("");
  const [lastNarration, setLastNarration] = useState("");
  const { setGameData } = useGameContext();
  const [loaded, setLoaded] = useState<any>(null);
  const [showStartModal, setShowStartModal] = useState(false);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const checkMemory = async () => {
      const res = await fetch("/api/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id, action: "load" }),
      });
      const data = await res.json();
      if (data.status === "loaded") {
        setHasSavedGame(true);
        setLastNarration(data.scene_state || "");
        setLoaded(data.latest_memory_data);
      }
      setLoading(false);
    };

    if (session_id) {
      checkMemory();
    }
  }, [session_id]);

  const handleNewGame = async () => {
    if (!worldName.trim()) return;

    await fetch("/api/init", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, action: "new", world: worldName }),
    });

    localStorage.removeItem("loadedMemory");
    setGameData({ worldName });
    setShowStartModal(false);
    router.push("/game");
  };

  const handleLoadGame = () => {
    localStorage.setItem("loadedMemory", JSON.stringify(loaded));
    setGameData({ loaded: loaded });
    router.push("/game");
  };

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-lg">Loading your adventure...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero" style={{ paddingTop: '80px' }}>
        <div className="hero-bg" style={{ transform: `translateY(${scrollY * 0.5}px)` }}>
          <div className="hero-gradient"></div>
          <div className="hero-grid"></div>
        </div>
        
        <div className="container hero-content">
          <div className="hero-badge fade-in">
            <span className="badge badge-primary">
              <span className="badge-dot"></span>
              Multi-Agent AI RPG
            </span>
          </div>
          
          <h1 className="hero-title fade-in" style={{ animationDelay: '0.1s' }}>
            🧙‍♂️ Welcome to Sinbad AI
          </h1>
          
          <p className="hero-description fade-in" style={{ animationDelay: '0.2s' }}>
            A narrative-driven adventure where your choices shape not just the story,
            but reveal who you truly are. Every decision matters. Every path is unique.
          </p>
          
          <div className="hero-actions fade-in" style={{ animationDelay: '0.3s' }}>
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => setShowStartModal(true)}
            >
              <span>Begin New Journey</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
            
            {hasSavedGame && (
              <button 
                className="btn btn-secondary btn-lg"
                onClick={handleLoadGame}
              >
                Continue Your Quest
              </button>
            )}

            {!hasSavedGame && (
              <button 
                className="btn btn-secondary btn-lg"
                onClick={() => scrollToSection('features')}
              >
                Learn More
              </button>
            )}
          </div>

          {hasSavedGame && (
            <div className="fade-in mt-8 bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl border border-purple-500/20 max-w-2xl mx-auto" style={{ animationDelay: '0.4s' }}>
              <h3 className="text-xl font-semibold mb-2 text-purple-300">🗂️ Saved Game Found</h3>
              <p className="text-sm text-gray-300 mb-3">
                <strong className="text-purple-400">Last memory:</strong>
              </p>
              <p className="text-gray-200 italic">
                {lastNarration.substring(0, 200)}{lastNarration.length > 200 ? '...' : ''}
              </p>
            </div>
          )}
          
          <div className="hero-stats fade-in" style={{ animationDelay: '0.5s' }}>
            <div className="stat">
              <div className="stat-value">∞</div>
              <div className="stat-label">Worlds</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat">
              <div className="stat-value">10+</div>
              <div className="stat-label">AI Agents</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat">
              <div className="stat-value">💾</div>
              <div className="stat-label">Auto-Save</div>
            </div>
          </div>
        </div>
        
        <div className="hero-scroll-indicator">
          <div className="scroll-mouse"></div>
          <span>Scroll to explore</span>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <h2 className="gradient-text">Powered by Advanced AI</h2>
            <p className="section-description">
              10+ specialized AI agents working in concert to create
              a living, breathing world that responds to your choices
            </p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3>Any World You Imagine</h3>
              <p>Enter any universe—Jurassic Park, One Piece, Cyberpunk, Medieval Fantasy. The AI builds a rich, living world around your choice.</p>
              <div className="feature-tags">
                <span className="badge badge-primary">Unlimited</span>
                <span className="badge badge-primary">Dynamic</span>
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3>NPCs That Remember</h3>
              <p>Characters remember every interaction. Help someone early? They'll remember. Betray trust? They won't forget.</p>
              <div className="feature-tags">
                <span className="badge badge-success">Persistent Memory</span>
                <span className="badge badge-success">Dynamic Trust</span>
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3>Persistent Progress</h3>
              <p>Your journey is automatically saved to MongoDB. Resume anytime, anywhere. Your story persists across sessions with Google OAuth.</p>
              <div className="feature-tags">
                <span className="badge badge-warning">Auto-Save</span>
                <span className="badge badge-warning">Cloud Sync</span>
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3>Multi-Agent Orchestration</h3>
              <p>10+ specialized AI agents coordinate behind the scenes—World Builder, NPC Manager, Quest Designer, and more.</p>
              <div className="feature-tags">
                <span className="badge badge-danger">10+ Agents</span>
                <span className="badge badge-danger">Coordinated</span>
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3>Dynamic Storytelling</h3>
              <p>AI-generated lore, scenes, and characters that evolve with your choices. Every playthrough creates a unique narrative.</p>
              <div className="feature-tags">
                <span className="badge badge-primary">Emergent</span>
                <span className="badge badge-primary">Adaptive</span>
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3>Play as Sinbad</h3>
              <p>Step into the shoes of Sinbad, the legendary adventurer. Make choices, forge alliances, and write your own legend.</p>
              <div className="feature-tags">
                <span className="badge badge-success">Role-Play</span>
                <span className="badge badge-success">Interactive</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works">
        <div className="container">
          <div className="section-header">
            <h2 className="gradient-text">How It Works</h2>
            <p className="section-description">
              A seamless blend of narrative design and AI intelligence
            </p>
          </div>
          
          <div className="steps">
            <div className="step">
              <div className="step-number">01</div>
              <div className="step-content">
                <h3>Choose Your World</h3>
                <p>Enter any universe you can imagine—pirates, cyberpunk, fantasy, sci-fi. The AI builds a rich world around your choice.</p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">02</div>
              <div className="step-content">
                <h3>Login & Save Progress</h3>
                <p>Sign in with Google OAuth. Your adventure is automatically saved to MongoDB and local storage for seamless continuation.</p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">03</div>
              <div className="step-content">
                <h3>Make Choices</h3>
                <p>Navigate through AI-generated scenes. Each choice shapes your journey, builds relationships, and determines your path.</p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">04</div>
              <div className="step-content">
                <h3>Watch the World React</h3>
                <p>NPCs remember. Quests adapt. The world changes based on your decisions. Every action has consequences.</p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">05</div>
              <div className="step-content">
                <h3>Resume Anytime</h3>
                <p>Your progress is always saved. Return to your adventure whenever you want, exactly where you left off.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="technology">
        <div className="container">
          <div className="tech-content">
            <div className="tech-visual">
              <div className="tech-diagram">
                <div className="agent-node orchestrator">
                  <div className="node-pulse"></div>
                  <span>Orchestrator</span>
                </div>
                <div className="agent-connections">
                  <div className="connection"></div>
                  <div className="connection"></div>
                  <div className="connection"></div>
                </div>
                <div className="agent-grid">
                  <div className="agent-node">World</div>
                  <div className="agent-node">NPC</div>
                  <div className="agent-node">Quest</div>
                  <div className="agent-node">Lore</div>
                  <div className="agent-node">Scene</div>
                  <div className="agent-node">Character</div>
                  <div className="agent-node">Dialogue</div>
                  <div className="agent-node">Memory</div>
                  <div className="agent-node">Story</div>
                  <div className="agent-node">Choice</div>
                </div>
              </div>
            </div>
            
            <div className="tech-info">
              <h2>Built on Advanced AI</h2>
              <p className="tech-description">
                Sinbad AI uses a sophisticated multi-agent architecture with persistent
                memory and cloud synchronization for seamless adventures.
              </p>
              
              <ul className="tech-features">
                <li>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Claude, Gemini & Groq LLM integration</span>
                </li>
                <li>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>MongoDB + Local Storage hybrid memory</span>
                </li>
                <li>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Google OAuth secure authentication</span>
                </li>
                <li>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>FastAPI + React modern stack</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="container">
          <div className="cta-card">
            <h2>Ready to Begin Your Adventure?</h2>
            <p>Your world. Your story. Your legend.</p>
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => setShowStartModal(true)}
            >
              Start Your Journey
            </button>
          </div>
        </div>
      </section>

      {/* Start Modal */}
      {showStartModal && (
        <div className="modal-overlay" onClick={() => setShowStartModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button 
              className="modal-close"
              onClick={() => setShowStartModal(false)}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <h2>🌍 Enter Your World</h2>
            <p className="modal-description">
              Choose any universe, real or imagined. The AI will build
              a rich, reactive world around your choice.
            </p>
            
            <div className="input-group">
              <label htmlFor="world-input">World / Universe</label>
              <input
                id="world-input"
                type="text"
                value={worldName}
                onChange={e => setWorldName(e.target.value)}
                placeholder="e.g., Jurassic Park, One Piece, Cyberpunk City, Medieval Fantasy..."
                className="text-input"
                autoFocus
                onKeyPress={e => e.key === 'Enter' && worldName && handleNewGame()}
              />
              <small className="input-hint">
                Try: Star Wars, Pirates of Caribbean, Post-Apocalyptic, Vikings, Noir Detective, Anime World...
              </small>
            </div>
            
            <div className="modal-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowStartModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleNewGame}
                disabled={!worldName}
              >
                Start Adventure
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <h3>Sinbad AI</h3>
              <p>Multi-Agent AI RPG Adventure</p>
            </div>
            <div className="footer-links">
              <a href="#features" onClick={e => { e.preventDefault(); scrollToSection('features'); }}>
                Features
              </a>
              <a href="https://github.com/aryanparab/SinbadAI" target="_blank" rel="noopener noreferrer">
                GitHub
              </a>
              <a href="https://www.anthropic.com" target="_blank" rel="noopener noreferrer">
                Powered by Claude
              </a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 Sinbad AI. Built with React, FastAPI, and Advanced LLMs.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}