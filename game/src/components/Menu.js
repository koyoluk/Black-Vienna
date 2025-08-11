import React from 'react';

const Menu = ({ 
  playerName, 
  gameId, 
  onPlayerNameChange, 
  onGameIdChange, 
  onCreateGame, 
  onJoinGame 
}) => {
  return (
    <div className="menu-container">
      <div className="game-header">
        <h1 className="game-title">Black Vienna</h1>
        <p className="game-subtitle">A Game of Deduction and Mystery</p>
      </div>
      
      <div className="menu-card">
        <div className="input-group">
          <label htmlFor="playerName">Your Name</label>
          <input
            id="playerName"
            type="text"
            placeholder="Enter your detective name"
            value={playerName}
            onChange={(e) => onPlayerNameChange(e.target.value)}
            className="input-field"
            maxLength={20}
          />
        </div>
        
        <div className="menu-actions">
          <button onClick={onCreateGame} className="btn btn-primary">
            <span className="btn-icon">🎮</span>
            Create New Game
          </button>
          
          <div className="divider">
            <span>or</span>
          </div>
          
          <div className="input-group">
            <label htmlFor="gameId">Game ID</label>
            <input
              id="gameId"
              type="text"
              placeholder="Enter game ID to join"
              value={gameId}
              onChange={(e) => onGameIdChange(e.target.value)}
              className="input-field"
              maxLength={1000}
            />
          </div>
          
          <button onClick={onJoinGame} className="btn btn-secondary">
            <span className="btn-icon">🚪</span>
            Join Game
          </button>
        </div>
      </div>
      
      <div className="game-info">
        <h3>How to Play</h3>
        <ul>
          <li>3+ players needed to start</li>
          <li>Deduce the three conspirators</li>
          <li>Use investigation cards to gather clues</li>
          <li>Be the first to solve the mystery!</li>
        </ul>
      </div>
    </div>
  );
};

export default Menu;