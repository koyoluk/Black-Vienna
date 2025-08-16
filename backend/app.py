from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import uuid
import logging
from game_logic import Game, GameStatus, PlayerStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Store active games and player sessions
games = {}
player_sessions = {}  # Maps session_id to {game_id, player_id}

@app.route('/')
def index():
    return "Black Vienna Game Server Running"

@app.route('/health')
def health():
    return {"status": "healthy", "games_active": len(games)}

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'session_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    
    # Handle player leaving
    if request.sid in player_sessions:
        session_data = player_sessions[request.sid]
        game_id = session_data['game_id']
        
        # Notify other players in the game
        if game_id in games:
            emit('player_disconnected', {
                'player_id': session_data['player_id'],
                'message': 'A player has disconnected'
            }, room=game_id)
        
        # Clean up session
        del player_sessions[request.sid]

@socketio.on('create_game')
def handle_create_game(data):
    try:
        player_name = data.get('player_name', '').strip()
        
        if not player_name:
            emit('error', {'message': 'Player name is required'})
            return
        
        # Generate unique game ID (6 characters for easier sharing)
        game_id = str(uuid.uuid4())[:8].upper()
        
        # Create new game
        game = Game(game_id)
        
        # Store game
        games[game_id] = {
            'game': game,
            'players': [{
                'id': request.sid,
                'name': player_name
            }],
            'host': request.sid
        }
        
        # Join room
        join_room(game_id)
        
        # Track player session
        player_sessions[request.sid] = {
            'game_id': game_id,
            'player_id': request.sid,
            'player_name': player_name
        }
        
        logger.info(f"Game created: {game_id} by {player_name}")
        
        emit('game_created', {
            'game_id': game_id,
            'player_id': request.sid,
            'is_host': True
        })
        
        # Send initial lobby state
        emit('lobby_update', {
            'players': games[game_id]['players'],
            'min_players': 3,
            'max_players': 8,
            'can_start': len(games[game_id]['players']) >= 3,
            'host_id': games[game_id]['host']
        }, room=game_id)
        
    except Exception as e:
        logger.error(f"Error creating game: {e}")
        emit('error', {'message': 'Failed to create game'})

@socketio.on('join_game')
def handle_join_game(data):
    try:
        game_id = data.get('game_id', '').strip().upper()
        player_name = data.get('player_name', '').strip()
        
        if not game_id or not player_name:
            emit('error', {'message': 'Game ID and player name are required'})
            return
        
        if game_id not in games:
            emit('error', {'message': 'Game not found'})
            return
        
        game_data = games[game_id]
        
        # Check if game has started
        if game_data['game'].game_status != GameStatus.WAITING:
            emit('error', {'message': 'Game has already started'})
            return
        
        # Check player limit
        if len(game_data['players']) >= 8:
            emit('error', {'message': 'Game is full (max 8 players)'})
            return
        
        # Add player
        join_room(game_id)
        game_data['players'].append({
            'id': request.sid,
            'name': player_name
        })
        
        # Track player session
        player_sessions[request.sid] = {
            'game_id': game_id,
            'player_id': request.sid,
            'player_name': player_name
        }
        
        logger.info(f"Player {player_name} joined game {game_id}")
        
        emit('game_joined', {
            'game_id': game_id,
            'player_id': request.sid,
            'is_host': False
        })
        
        # Update all players in lobby
        emit('lobby_update', {
            'players': game_data['players'],
            'min_players': 3,
            'max_players': 8,
            'can_start': len(game_data['players']) >= 3,
            'host_id': game_data['host']
        }, room=game_id)
        
    except Exception as e:
        logger.error(f"Error joining game: {e}")
        emit('error', {'message': 'Failed to join game'})

@socketio.on('start_game')
def handle_start_game(data):
    try:
        game_id = data.get('game_id')
        
        if game_id not in games:
            emit('error', {'message': 'Game not found'})
            return
        
        game_data = games[game_id]
        
        # Verify requester is host
        if request.sid != game_data['host']:
            emit('error', {'message': 'Only the host can start the game'})
            return
        
        # Check player count
        num_players = len(game_data['players'])
        if num_players < 3:
            emit('error', {'message': 'Need at least 3 players to start'})
            return
        
        # Setup and start the game
        game = game_data['game']
        game.setup_game(game_data['players'])
        
        logger.info(f"Game {game_id} started with {num_players} players")
        
        # Send personalized game state to each player
        for player_data in game_data['players']:
            player_state = game.get_player_view(player_data['id'])
            emit('game_started', player_state, room=player_data['id'])
        
        # Broadcast game update to all
        emit('game_update', game.get_game_state(), room=game_id)
        
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        emit('error', {'message': 'Failed to start game'})

@socketio.on('investigate')
def handle_investigate(data):
    try:
        game_id = data.get('game_id')
        questioned_player_id = data.get('questioned_player_id')
        card_index = data.get('card_index')
        double_card_id = data.get('double_card_id', None)
        
        if game_id not in games:
            emit('error', {'message': 'Game not found'})
            return
        
        game = games[game_id]['game']
        
        # Perform investigation
        result = game.investigate(
            investigator_id=request.sid,
            questioned_player_id=questioned_player_id,
            card_index=card_index,
            double_card_id=double_card_id
        )
        
        if 'error' in result:
            emit('error', {'message': result['error']})
            return
        
        logger.info(f"Investigation in game {game_id}: {result['result'].coins_taken} coins taken")
        
        # Send investigation result to all players
        emit('investigation_result', {
            'result': {
                'investigator_id': result['result'].investigator_id,
                'investigator_name': next(p['name'] for p in games[game_id]['players'] if p['id'] == result['result'].investigator_id),
                'questioned_player_id': result['result'].questioned_player_id,
                'questioned_player_name': next(p['name'] for p in games[game_id]['players'] if p['id'] == result['result'].questioned_player_id),
                'card_letters': result['result'].card_letters,
                'coins_taken': result['result'].coins_taken
            },
            'double_result': {
                'card_letters': result['double_result'].card_letters,
                'coins_taken': result['double_result'].coins_taken
            } if result.get('double_result') else None
        }, room=game_id)
        
        # Send updated game state to all players
        for player_data in games[game_id]['players']:
            player_state = game.get_player_view(player_data['id'])
            emit('game_state_update', player_state, room=player_data['id'])
        
        # Check if game ended
        if result.get('game_ended'):
            emit('game_ended', {
                'reason': 'conditions_met',
                'solution': game.hidden_suspects,
                'final_state': game.get_game_state()
            }, room=game_id)
            
    except Exception as e:
        logger.error(f"Error during investigation: {e}")
        emit('error', {'message': 'Investigation failed'})

@socketio.on('make_guess')
def handle_make_guess(data):
    try:
        game_id = data.get('game_id')
        guessed_suspects = data.get('suspects', [])
        
        if game_id not in games:
            emit('error', {'message': 'Game not found'})
            return
        
        game = games[game_id]['game']
        
        # Make the guess
        result = game.make_guess(request.sid, guessed_suspects)
        
        if 'error' in result:
            emit('error', {'message': result['error']})
            return
        
        player_name = next(p['name'] for p in games[game_id]['players'] if p['id'] == request.sid)
        
        if result['correct']:
            # Player won!
            logger.info(f"Player {player_name} won game {game_id}")
            emit('game_won', {
                'winner_id': request.sid,
                'winner_name': player_name,
                'solution': result['solution'],
                'final_state': game.get_game_state()
            }, room=game_id)
        else:
            # Player eliminated
            logger.info(f"Player {player_name} eliminated in game {game_id}")
            emit('player_eliminated', {
                'player_id': request.sid,
                'player_name': player_name,
                'wrong_guess': guessed_suspects
            }, room=game_id)
            
            # Update all players
            for player_data in games[game_id]['players']:
                player_state = game.get_player_view(player_data['id'])
                emit('game_state_update', player_state, room=player_data['id'])
            
            # Check if game ended (all eliminated)
            if game.game_status == GameStatus.ENDED:
                emit('game_ended', {
                    'reason': 'all_eliminated',
                    'solution': game.hidden_suspects,
                    'final_state': game.get_game_state()
                }, room=game_id)
                
    except Exception as e:
        logger.error(f"Error making guess: {e}")
        emit('error', {'message': 'Guess failed'})

@socketio.on('request_game_state')
def handle_request_game_state(data):
    """Allow players to request current game state"""
    try:
        game_id = data.get('game_id')
        
        if game_id not in games:
            emit('error', {'message': 'Game not found'})
            return
        
        game = games[game_id]['game']
        player_state = game.get_player_view(request.sid)
        emit('game_state_update', player_state)
        
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        emit('error', {'message': 'Failed to get game state'})

@socketio.on('leave_game')
def handle_leave_game(data):
    """Handle player leaving a game"""
    try:
        if request.sid in player_sessions:
            session_data = player_sessions[request.sid]
            game_id = session_data['game_id']
            
            leave_room(game_id)
            
            # Remove from game if still in lobby
            if game_id in games:
                game_data = games[game_id]
                if game_data['game'].game_status == GameStatus.WAITING:
                    game_data['players'] = [
                        p for p in game_data['players'] 
                        if p['id'] != request.sid
                    ]
                    
                    # Update lobby
                    emit('lobby_update', {
                        'players': game_data['players'],
                        'min_players': 3,
                        'max_players': 8,
                        'can_start': len(game_data['players']) >= 3,
                        'host_id': game_data['host']
                    }, room=game_id)
            
            del player_sessions[request.sid]
            
        emit('left_game', {'success': True})
        
    except Exception as e:
        logger.error(f"Error leaving game: {e}")
        emit('error', {'message': 'Failed to leave game'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)