import React from 'react';

const Lobby = ({ gameId, onStartGame, onBackToMenu }) => {
  const copyToClipboard = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(gameId);
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = gameId;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  };

  return (
    <div className="lobby-container">
      <div className="lobby-header">
        <h1>Game Lobby</h1>
        <button onClick={onBackToMenu} className="btn btn-ghost btn-sm">
          ← Back to Menu
        </button>
      </div>
      
      <div className="lobby-card">
        <div className="game-id-display">
          <label>Game ID</label>
          <div className="game-id-value">
            <code>{gameId}</code>
            <button 
              onClick={copyToClipboard}
              className="btn btn-ghost btn-xs"
              title="Copy to clipboard"
            >
              📋
            </button>
          </div>
          <p className="game-id-hint">Share this ID with other players</p>
        </div>
        
        <div className="lobby-actions">
          <button onClick={onStartGame} className="btn btn-primary btn-lg">
            <span className="btn-icon">🚀</span>
            Start Game
          </button>
          <p className="start-hint">Need 3+ players to start</p>
        </div>
      </div>
      
      <div className="waiting-animation">
        <div className="dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <p>Waiting for players to join...</p>
      </div>
    </div>
  );
};

export default Lobby;