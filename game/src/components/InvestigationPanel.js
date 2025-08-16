import React, { useState } from 'react';

const InvestigationPanel = ({ 
  gameState, 
  onInvestigate, 
  onMakeGuess,
  isMyTurn 
}) => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [selectedDoubleCard, setSelectedDoubleCard] = useState(null);
  const [guessMode, setGuessMode] = useState(false);
  const [guessedSuspects, setGuessedSuspects] = useState(['', '', '']);
  const [showConfirmGuess, setShowConfirmGuess] = useState(false);

  const handleInvestigate = () => {
    if (selectedCard !== null && selectedPlayer) {
      onInvestigate({
        card_index: selectedCard,
        questioned_player_id: selectedPlayer,
        double_card_id: selectedDoubleCard
      });
      
      // Reset selections
      setSelectedCard(null);
      setSelectedPlayer('');
      setSelectedDoubleCard(null);
    }
  };

  const handleGuessSubmit = () => {
    // Validate guess
    const validGuess = guessedSuspects.every(s => s && s.length === 1);
    if (!validGuess) {
      alert('Please select exactly 3 suspects (single letters)');
      return;
    }
    
    setShowConfirmGuess(true);
  };

  const confirmGuess = () => {
    onMakeGuess(guessedSuspects);
    setShowConfirmGuess(false);
    setGuessMode(false);
    setGuessedSuspects(['', '', '']);
  };

  const allSuspects = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ω'
  ];

  if (!isMyTurn) {
    return (
      <div className="investigation-panel disabled">
        <h3>Investigation Panel</h3>
        <p className="wait-message">
          Waiting for {gameState.current_investigator}'s turn...
        </p>
      </div>
    );
  }

  if (guessMode) {
    return (
      <div className="investigation-panel guess-mode">
        <h3>Make Your Final Guess</h3>
        <p className="guess-warning">
          ⚠️ Warning: An incorrect guess will eliminate you from the game!
        </p>
        
        <div className="guess-inputs">
          <label>Select the 3 hidden suspects:</label>
          <div className="suspect-selectors">
            {[0, 1, 2].map(index => (
              <select
                key={index}
                value={guessedSuspects[index]}
                onChange={(e) => {
                  const newGuess = [...guessedSuspects];
                  newGuess[index] = e.target.value;
                  setGuessedSuspects(newGuess);
                }}
                className="suspect-select"
              >
                <option value="">Select...</option>
                {allSuspects.map(suspect => (
                  <option key={suspect} value={suspect}>{suspect}</option>
                ))}
              </select>
            ))}
          </div>
        </div>

        <div className="guess-actions">
          <button 
            onClick={handleGuessSubmit}
            className="btn btn-secondary"
            disabled={!guessedSuspects.every(s => s)}
          >
            Submit Guess
          </button>
          <button 
            onClick={() => {
              setGuessMode(false);
              setGuessedSuspects(['', '', '']);
            }}
            className="btn btn-ghost"
          >
            Cancel
          </button>
        </div>

        {showConfirmGuess && (
          <div className="confirm-dialog">
            <div className="confirm-content">
              <h4>Confirm Your Guess</h4>
              <p>You are guessing: <strong>{guessedSuspects.join(', ')}</strong></p>
              <p>Are you sure? This cannot be undone!</p>
              <div className="confirm-actions">
                <button onClick={confirmGuess} className="btn btn-secondary btn-sm">
                  Yes, I'm Sure
                </button>
                <button 
                  onClick={() => setShowConfirmGuess(false)} 
                  className="btn btn-ghost btn-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="investigation-panel">
      <h3>Your Investigation Turn</h3>
      
      {/* Card Selection */}
      <div className="investigation-section">
        <label>1. Choose an Investigation Card:</label>
        <div className="face-up-cards-selection">
          {gameState.face_up_cards?.map((cardData, index) => {
            const card = cardData.card;
            if (!card) return null;
            
            return (
              <div
                key={index}
                className={`investigation-card-select ${selectedCard === index ? 'selected' : ''}`}
                onClick={() => setSelectedCard(index)}
              >
                <div className="deck-label">Deck {index + 1}</div>
                <div className="card-letters">
                  {card.letters.join(' • ')}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Player Selection */}
      <div className="investigation-section">
        <label>2. Choose a Player to Question:</label>
        <div className="player-selection">
          {gameState.can_question?.map(player => (
            <button
              key={player.id}
              className={`player-select-btn ${selectedPlayer === player.id ? 'selected' : ''}`}
              onClick={() => setSelectedPlayer(player.id)}
            >
              {player.name}
            </button>
          ))}
        </div>
      </div>

      {/* Double Investigation (if available) */}
      {gameState.double_investigation_enabled && gameState.zero_coin_cards?.length > 0 && (
        <div className="investigation-section">
          <label>3. Optional: Double Investigation (0-coin card):</label>
          <div className="zero-coin-cards">
            {gameState.zero_coin_cards.map(card => (
              <div
                key={card.id}
                className={`zero-coin-card ${selectedDoubleCard === card.id ? 'selected' : ''}`}
                onClick={() => setSelectedDoubleCard(
                  selectedDoubleCard === card.id ? null : card.id
                )}
              >
                <div className="card-info">
                  <span className="card-letters">{card.letters.join(' • ')}</span>
                  <span className="card-history">
                    {card.used_by} → {card.questioned}: 0 coins
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="investigation-actions">
        <button
          onClick={handleInvestigate}
          className="btn btn-primary"
          disabled={selectedCard === null || !selectedPlayer}
        >
          <span className="btn-icon">🔍</span>
          Investigate
        </button>
        
        <button
          onClick={() => setGuessMode(true)}
          className="btn btn-secondary"
        >
          <span className="btn-icon">🎯</span>
          Make Final Guess
        </button>
      </div>

      {/* Game Info */}
      <div className="investigation-info">
        <div className="info-item">
          <span>Coins Remaining:</span>
          <strong>{gameState.central_coins}/40</strong>
        </div>
        <div className="info-item">
          <span>Coins Used:</span>
          <strong>{gameState.coins_used}</strong>
        </div>
        {gameState.double_investigation_enabled && (
          <div className="info-badge">
            Double Investigation Available!
          </div>
        )}
      </div>
    </div>
  );
};

export default InvestigationPanel;