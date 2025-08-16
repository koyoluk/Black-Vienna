import React, { useState } from 'react';
import InvestigationPanel from './InvestigationPanel';

const GameBoard = ({ 
  gameState, 
  socket, 
  gameId, 
  playerId, 
  onBackToMenu 
}) => {
  const [showHistory, setShowHistory] = useState(false);
  
  const handleInvestigate = (investigationData) => {
    socket.emit('investigate', {
      game_id: gameId,
      ...investigationData
    });
  };

  const handleMakeGuess = (suspects) => {
    socket.emit('make_guess', {
      game_id: gameId,
      suspects: suspects
    });
  };

  const isMyTurn = gameState.is_my_turn;
  const myStatus = gameState.my_status;

  // Group investigation history by round
  const historyByRound = {};
  gameState.investigation_history?.forEach(inv => {
    if (!historyByRound[inv.round]) {
      historyByRound[inv.round] = [];
    }
    historyByRound[inv.round].push(inv);
  });

  return (
    <div className="game-container">
      {/* Header */}
      <div className="game-header">
        <h1>Black Vienna</h1>
        <div className="header-actions">
          <button 
            onClick={() => setShowHistory(!showHistory)} 
            className="btn btn-ghost btn-sm"
          >
            {showHistory ? 'Hide' : 'Show'} History
          </button>
          <button onClick={onBackToMenu} className="btn btn-ghost btn-sm">
            ← Leave Game
          </button>
        </div>
      </div>
      
      {/* Game Status Bar */}
      <div className="game-status">
        <div className="status-item">
          <span className="status-label">Central Coins</span>
          <span className="status-value">{gameState.central_coins}/40</span>
        </div>
        <div className="status-item">
          <span className="status-label">Coins Used</span>
          <span className="status-value">{gameState.coins_used}/40</span>
        </div>
        <div className={`status-item ${isMyTurn ? 'current-investigator' : ''}`}>
          <span className="status-label">Current Investigator</span>
          <span className="status-value">
            {gameState.current_investigator} {isMyTurn && '(You)'}
          </span>
        </div>
        <div className="status-item">
          <span className="status-label">Round</span>
          <span className="status-value">{gameState.round_count}</span>
        </div>
      </div>

      {/* Game End Warning */}
      {gameState.coins_used >= 35 && (
        <div className="warning-banner">
          ⚠️ Warning: {37 - gameState.coins_used} coins until game ends!
        </div>
      )}
      
      {/* Main Game Area */}
      <div className="game-main">
        <div className="game-left">
          {/* My Cards */}
          <div className="my-cards-section">
            <h3>Your Suspect Cards</h3>
            <div className="cards-container">
              {gameState.my_cards?.map((card, index) => (
                <div key={index} className="suspect-card">
                  {card}
                </div>
              ))}
            </div>
            <p className="cards-hint">
              These suspects are NOT part of the conspiracy
            </p>
          </div>

          {/* Investigation Panel or Status */}
          {myStatus === 'active' ? (
            <InvestigationPanel
              gameState={gameState}
              onInvestigate={handleInvestigate}
              onMakeGuess={handleMakeGuess}
              isMyTurn={isMyTurn}
            />
          ) : (
            <div className="elimination-notice">
              <h3>You have been eliminated</h3>
              <p>Your guess was incorrect. Watch as others continue the investigation.</p>
            </div>
          )}
        </div>

        <div className="game-right">
          {/* Players */}
          <div className="players-section">
            <h3>Players</h3>
            <div className="players-list">
              {gameState.players?.map((player, index) => (
                <div 
                  key={player.id} 
                  className={`player-card ${
                    index === gameState.current_investigator_index ? 'current' : ''
                  } ${player.status === 'eliminated' ? 'eliminated' : ''}
                  ${player.status === 'winner' ? 'winner' : ''}`}
                >
                  <div className="player-name">
                    {player.name}
                    {player.id === playerId && ' (You)'}
                  </div>
                  <div className="player-info">
                    <span className="card-count">{player.card_count} cards</span>
                    {player.status === 'eliminated' && (
                      <span className="eliminated-tag">Eliminated</span>
                    )}
                    {player.status === 'winner' && (
                      <span className="winner-tag">🏆 Winner!</span>
                    )}
                    {index === gameState.current_investigator_index && player.status === 'active' && (
                      <span className="current-tag">🔍 Investigating</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Double Investigation Status */}
          {gameState.double_investigation_enabled ? (
            <div className="double-investigation-status active">
              <h4>✨ Double Investigation Unlocked!</h4>
              <p>Can use 0-coin cards for bonus questions</p>
            </div>
          ) : (
            <div className="double-investigation-status">
              <h4>Double Investigation</h4>
              <p>Unlocks after {Math.max(0, 6 - gameState.total_investigations)} more investigations</p>
              <p className="small">All players must investigate at least once</p>
            </div>
          )}
        </div>
      </div>

      {/* Investigation History Modal */}
      {showHistory && (
        <div className="history-modal">
          <div className="history-content">
            <div className="history-header">
              <h3>Investigation History</h3>
              <button 
                onClick={() => setShowHistory(false)}
                className="btn btn-ghost btn-sm"
              >
                ✕
              </button>
            </div>
            <div className="history-body">
              {Object.keys(historyByRound).length === 0 ? (
                <p>No investigations yet</p>
              ) : (
                Object.entries(historyByRound)
                  .sort(([a], [b]) => Number(b) - Number(a))
                  .map(([round, investigations]) => (
                    <div key={round} className="history-round">
                      <h4>Round {round}</h4>
                      {investigations.map((inv, idx) => (
                        <div key={idx} className="history-item">
                          <div className="history-players">
                            <span className="investigator">{inv.investigator}</span>
                            <span className="arrow">→</span>
                            <span className="questioned">{inv.questioned}</span>
                          </div>
                          <div className="history-details">
                            <span className="history-letters">
                              {inv.letters.join(' • ')}
                            </span>
                            <span className={`history-coins ${inv.coins === 0 ? 'zero' : ''}`}>
                              {inv.coins} coin{inv.coins !== 1 ? 's' : ''}
                            </span>
                            {inv.is_double && (
                              <span className="double-badge">Double</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameBoard;