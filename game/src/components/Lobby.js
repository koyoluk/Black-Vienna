import React, { useState } from 'react';

const Lobby = ({ gameId, lobbyData, isHost, onStartGame, onBackToMenu }) => {
  const [copied, setCopied] = useState(false);
  
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
    
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const playerCount = lobbyData?.players?.length || 0;
  const canStart = lobbyData?.can_start || false;
  const minPlayers = lobbyData?.min_players || 3;
  const maxPlayers = lobbyData?.max_players || 8;

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
              {copied ? '✓' : '📋'}
            </button>
          </div>
          <p className="game-id-hint">
            Share this ID with other players to join
          </p>
        </div>
        
        {/* Player List */}
        <div className="lobby-players">
          <h3>Players ({playerCount}/{maxPlayers})</h3>
          <div className="player-list">
            {lobbyData?.players?.map((player, index) => (
              <div key={player.id} className="lobby-player">
                <span className="player-number">{index + 1}.</span>
                <span className="player-name">{player.name}</span>
                {player.id === lobbyData?.host_id && (
                  <span className="host-badge">Host</span>
                )}
              </div>
            ))}
            
            {/* Empty slots */}
            {Array.from({ length: Math.max(0, minPlayers - playerCount) }).map((_, i) => (
              <div key={`empty-${i}`} className="lobby-player empty">
                <span className="player-number">{playerCount + i + 1}.</span>
                <span className="player-name">Waiting for player...</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Start Game Section */}
        <div className="lobby-actions">
          {isHost ? (
            <>
              <button 
                onClick={onStartGame} 
                className={`btn ${canStart ? 'btn-primary' : 'btn-disabled'} btn-lg`}
                disabled={!canStart}
              >
                <span className="btn-icon">🚀</span>
                {canStart ? 'Start Game' : `Need ${minPlayers - playerCount} more player${minPlayers - playerCount !== 1 ? 's' : ''}`}
              </button>
              <p className="start-hint">
                {canStart 
                  ? `Ready to start with ${playerCount} players!`
                  : `Need at least ${minPlayers} players to start (max ${maxPlayers})`
                }
              </p>
            </>
          ) : (
            <>
              <div className="waiting-message">
                Waiting for host to start the game...
              </div>
              <p className="start-hint">
                {canStart 
                  ? `${playerCount} players ready!`
                  : `Need ${Math.max(0, minPlayers - playerCount)} more player${minPlayers - playerCount !== 1 ? 's' : ''} to start`
                }
              </p>
            </>
          )}
        </div>
      </div>
      
      {/* Waiting Animation */}
      {!canStart && (
        <div className="waiting-animation">
          <div className="dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <p>Waiting for players to join...</p>
        </div>
      )}
    </div>
  );
};

export default Lobby;