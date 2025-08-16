import React, { useState, useEffect } from 'react';
import Menu from './components/Menu';
import Lobby from './components/Lobby';
import GameBoard from './components/GameBoard';
import { useSocket } from './hooks/useSocket';
import './styles/App.css';

function App() {
  const [gameState, setGameState] = useState('menu'); // menu, lobby, playing, ended
  const [playerName, setPlayerName] = useState('');
  const [gameId, setGameId] = useState('');
  const [playerId, setPlayerId] = useState('');
  const [isHost, setIsHost] = useState(false);
  const [lobbyData, setLobbyData] = useState(null);
  const [currentGameState, setCurrentGameState] = useState(null);
  const [gameEndData, setGameEndData] = useState(null);
  const [notifications, setNotifications] = useState([]);

  const { socket, isConnected } = useSocket();

  // Add notification
  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  useEffect(() => {
    if (!socket) return;

    // Connection events
    socket.on('connected', (data) => {
      console.log('Connected with session ID:', data.session_id);
    });

    // Game creation
    socket.on('game_created', (data) => {
      setGameId(data.game_id);
      setPlayerId(data.player_id);
      setIsHost(data.is_host);
      setGameState('lobby');
      addNotification(`Game created! ID: ${data.game_id}`, 'success');
    });

    // Game joining
    socket.on('game_joined', (data) => {
      setGameId(data.game_id);
      setPlayerId(data.player_id);
      setIsHost(data.is_host);
      setGameState('lobby');
      addNotification('Successfully joined game!', 'success');
    });

    // Lobby updates
    socket.on('lobby_update', (data) => {
      setLobbyData(data);
    });

    // Game started
    socket.on('game_started', (data) => {
      setCurrentGameState(data);
      setGameState('playing');
      addNotification('Game has started!', 'success');
    });

    // Game state updates
    socket.on('game_state_update', (data) => {
      setCurrentGameState(data);
    });

    // Investigation results
    socket.on('investigation_result', (data) => {
      const result = data.result;
      const message = `${result.investigator_name} questioned ${result.questioned_player_name} about ${result.card_letters.join(', ')} → ${result.coins_taken} coin${result.coins_taken !== 1 ? 's' : ''}`;
      addNotification(message, 'info');
      
      if (data.double_result) {
        const double = data.double_result;
        const doubleMessage = `Double Investigation: ${double.card_letters.join(', ')} → ${double.coins_taken} coin${double.coins_taken !== 1 ? 's' : ''}`;
        addNotification(doubleMessage, 'info');
      }
    });

    // Player eliminated
    socket.on('player_eliminated', (data) => {
      addNotification(`${data.player_name} has been eliminated!`, 'warning');
    });

    // Game won
    socket.on('game_won', (data) => {
      setGameEndData({
        type: 'won',
        winner: data.winner_name,
        solution: data.solution
      });
      setGameState('ended');
      addNotification(`🏆 ${data.winner_name} has won the game!`, 'success');
    });

    // Game ended
    socket.on('game_ended', (data) => {
      setGameEndData({
        type: 'ended',
        reason: data.reason,
        solution: data.solution
      });
      setGameState('ended');
      
      if (data.reason === 'conditions_met') {
        addNotification('Game ended - conditions met!', 'info');
      } else if (data.reason === 'all_eliminated') {
        addNotification('Game ended - all players eliminated!', 'warning');
      }
    });

    // Player disconnected
    socket.on('player_disconnected', (data) => {
      addNotification(data.message, 'warning');
    });

    // Errors
    socket.on('error', (data) => {
      addNotification(data.message, 'error');
    });

    // Clean up
    return () => {
      socket.off('connected');
      socket.off('game_created');
      socket.off('game_joined');
      socket.off('lobby_update');
      socket.off('game_started');
      socket.off('game_state_update');
      socket.off('investigation_result');
      socket.off('player_eliminated');
      socket.off('game_won');
      socket.off('game_ended');
      socket.off('player_disconnected');
      socket.off('error');
    };
  }, [socket]);

  const handleCreateGame = () => {
    if (!playerName.trim()) {
      addNotification('Please enter your name', 'error');
      return;
    }
    socket?.emit('create_game', { player_name: playerName });
  };

  const handleJoinGame = () => {
    if (!playerName.trim() || !gameId.trim()) {
      addNotification('Please enter your name and game ID', 'error');
      return;
    }
    socket?.emit('join_game', { 
      game_id: gameId.toUpperCase(), 
      player_name: playerName 
    });
  };

  const handleStartGame = () => {
    if (!isHost) {
      addNotification('Only the host can start the game', 'error');
      return;
    }
    
    if (!lobbyData?.can_start) {
      addNotification('Need at least 3 players to start', 'error');
      return;
    }
    
    socket?.emit('start_game', { game_id: gameId });
  };

  const handleBackToMenu = () => {
    if (gameState === 'playing' || gameState === 'lobby') {
      socket?.emit('leave_game', { game_id: gameId });
    }
    
    setGameState('menu');
    setGameId('');
    setCurrentGameState(null);
    setLobbyData(null);
    setPlayerId('');
    setIsHost(false);
    setGameEndData(null);
  };

  if (!isConnected) {
    return (
      <div className="app loading">
        <div className="loading-spinner"></div>
        <p>Connecting to game server...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Notifications */}
      <div className="notifications">
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            className={`notification ${notification.type}`}
          >
            {notification.message}
          </div>
        ))}
      </div>

      <div className="app-container">
        {gameState === 'menu' && (
          <Menu
            playerName={playerName}
            gameId={gameId}
            onPlayerNameChange={setPlayerName}
            onGameIdChange={setGameId}
            onCreateGame={handleCreateGame}
            onJoinGame={handleJoinGame}
          />
        )}
        
        {gameState === 'lobby' && (
          <Lobby
            gameId={gameId}
            lobbyData={lobbyData}
            isHost={isHost}
            onStartGame={handleStartGame}
            onBackToMenu={handleBackToMenu}
          />
        )}
        
        {gameState === 'playing' && currentGameState && (
          <GameBoard
            gameState={currentGameState}
            socket={socket}
            gameId={gameId}
            playerId={playerId}
            onBackToMenu={handleBackToMenu}
          />
        )}
        
        {gameState === 'ended' && gameEndData && (
          <div className="game-ended-container">
            <div className="game-ended-card">
              {gameEndData.type === 'won' ? (
                <>
                  <h1>🏆 Game Over!</h1>
                  <h2>{gameEndData.winner} Wins!</h2>
                </>
              ) : (
                <>
                  <h1>Game Ended</h1>
                  <p>{gameEndData.reason === 'all_eliminated' 
                    ? 'All players were eliminated!' 
                    : 'Game conditions were met!'}</p>
                </>
              )}
              
              <div className="solution-reveal">
                <h3>The Hidden Suspects Were:</h3>
                <div className="solution-cards">
                  {gameEndData.solution.map((suspect, idx) => (
                    <div key={idx} className="solution-card">
                      {suspect}
                    </div>
                  ))}
                </div>
              </div>
              
              <button onClick={handleBackToMenu} className="btn btn-primary btn-lg">
                Back to Menu
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;