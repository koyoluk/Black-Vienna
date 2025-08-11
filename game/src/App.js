import React, { useState, useEffect } from 'react';
import Menu from './components/Menu';
import Lobby from './components/Lobby';
import GameBoard from './components/GameBoard';
import { useSocket } from './hooks/useSocket.js';
import './styles/App.css';

function App() {
  const [gameState, setGameState] = useState('menu'); // menu, lobby, playing
  const [playerName, setPlayerName] = useState('');
  const [gameId, setGameId] = useState('');
  const [game, setGame] = useState(null);
  const [playerId, setPlayerId] = useState('');

  const { socket, isConnected } = useSocket();

  useEffect(() => {
    if (!socket) return;

    socket.on('game_created', (data) => {
      setGameId(data.game_id);
      setPlayerId(data.player_id);
      setGameState('lobby');
    });

    socket.on('player_joined', (data) => {
      console.log('Players:', data.players);
    });

    socket.on('game_started', (data) => {
      setGame(data);
      setGameState('playing');
    });

    socket.on('error', (data) => {
      alert(data.message);
    });

    return () => {
      socket.off('game_created');
      socket.off('player_joined');
      socket.off('game_started');
      socket.off('error');
    };
  }, [socket]);

  const handleCreateGame = () => {
    if (!playerName.trim()) {
      alert('Please enter your name');
      return;
    }
    socket?.emit('create_game', { player_name: playerName });
  };

  const handleJoinGame = () => {
    if (!playerName.trim() || !gameId.trim()) {
      alert('Please enter your name and game ID');
      return;
    }
    socket?.emit('join_game', { game_id: gameId, player_name: playerName });
    setGameState('lobby');
  };

  const handleStartGame = () => {
    socket?.emit('start_game', { game_id: gameId });
  };

  const handleBackToMenu = () => {
    setGameState('menu');
    setGameId('');
    setGame(null);
    setPlayerId('');
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
            onStartGame={handleStartGame}
            onBackToMenu={handleBackToMenu}
          />
        )}
        
        {gameState === 'playing' && game && (
          <GameBoard
            game={game}
            playerId={playerId}
            onBackToMenu={handleBackToMenu}
          />
        )}
      </div>
    </div>
  );
}

export default App;