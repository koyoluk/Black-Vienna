import React from 'react';

const GameBoard = ({ game, playerId, onBackToMenu }) => {
  const currentPlayer = game.players[game.current_investigator];
  const isMyTurn = currentPlayer?.id === playerId;

  return (
    <div className="game-container">
      <div className="game-header">
        <h1>Black Vienna</h1>
        <button onClick={onBackToMenu} className="btn btn-ghost btn-sm">
          ← Leave Game
        </button>
      </div>
      
      <div className="game-status">
        <div className="status-item">
          <span className="status-label">Central Coins</span>
          <span className="status-value">{game.central_coins}/40</span>
        </div>
        <div className="status-item current-investigator">
          <span className="status-label">Current Investigator</span>
          <span className="status-value">
            {currentPlayer?.name} {isMyTurn && '(You)'}
          </span>
        </div>
      </div>
      
      <div className="my-cards-section">
        <h3>Your Suspect Cards</h3>
        <div className="cards-container">
          {game.my_cards?.map((card, index) => (
            <div key={index} className="suspect-card">
              {card}
            </div>
          ))}
        </div>
        <p className="cards-hint">
          These suspects are NOT part of the Black Vienna conspiracy
        </p>
      </div>
      
      <div className="investigation-section">
        <h3>Investigation Cards</h3>
        <div className="investigation-cards">
          {game.face_up_cards?.map((card, index) => (
            <div key={card.id} className="investigation-card">
              <div className="card-header">Deck {index + 1}</div>
              <div className="card-letters">
                {card.letters.join(' • ')}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="players-section">
        <h3>Players</h3>
        <div className="players-list">
          {game.players?.map((player, index) => (
            <div 
              key={player.id} 
              className={`player-card ${
                index === game.current_investigator ? 'current' : ''
              } ${player.eliminated ? 'eliminated' : ''}`}
            >
              <div className="player-name">
                {player.name}
                {player.id === playerId && ' (You)'}
              </div>
              <div className="player-status">
                {player.eliminated && <span className="eliminated-tag">Eliminated</span>}
                {index === game.current_investigator && !player.eliminated && (
                  <span className="current-tag">🔍 Investigating</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GameBoard;