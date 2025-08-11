from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from game_logic import Game, setup_game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active games
games = {}

@app.route('/')
def index():
    return "Black Vienna Game Server"

@socketio.on('create_game')
def handle_create_game(data):
    game_id = str(uuid.uuid4())
    player_name = data['player_name']
    
    # Create new game but don't start yet
    games[game_id] = {
        'game': None,
        'players': [],
        'status': 'lobby'
    }
    
    join_room(game_id)
    games[game_id]['players'].append({
        'id': request.sid,
        'name': player_name
    })
    
    emit('game_created', {
        'game_id': game_id,
        'player_id': request.sid
    })

@socketio.on('join_game')
def handle_join_game(data):
    game_id = data['game_id']
    player_name = data['player_name']
    
    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return
    
    join_room(game_id)
    games[game_id]['players'].append({
        'id': request.sid,
        'name': player_name
    })
    
    # Notify all players in room
    emit('player_joined', {
        'players': games[game_id]['players']
    }, room=game_id)

@socketio.on('start_game')
def handle_start_game(data):
    game_id = data['game_id']
    
    if game_id not in games:
        emit('error', {'message': 'Game not found'})
        return
    
    num_players = len(games[game_id]['players'])
    if num_players < 1:
        emit('error', {'message': 'Need at least 3 players'})
        return
    
    # Set up the actual game
    game = setup_game(num_players)
    game.game_id = game_id
    
    # Assign player IDs to game players
    for i, player in enumerate(game.players):
        player.player_id = games[game_id]['players'][i]['id']
        player.name = games[game_id]['players'][i]['name']
    
    games[game_id]['game'] = game
    games[game_id]['status'] = 'active'
    
    # Send game state to all players
    for player_info in games[game_id]['players']:
        player_game_state = get_game_state_for_player(game, player_info['id'])
        emit('game_started', player_game_state, room=player_info['id'])
        
def get_game_state_for_player(game, player_id):
    """Get game state customized for a specific player"""
    # Find this player's data
    player_data = None
    for player in game.players:
        if player.player_id == player_id:
            player_data = player
            break
    
    return {
        'game_id': game.game_id,
        'players': [{'name': p.name, 'id': p.player_id, 'eliminated': p.is_eliminated} for p in game.players],
        'face_up_cards': [{'id': card.card_id, 'letters': card.letters} for card in game.face_up_cards],
        'central_coins': game.central_coins,
        'current_investigator': game.current_investigator,
        'investigation_history': game.investigation_history,
        'double_investigation_enabled': game.double_investigation_enabled,
        'my_cards': player_data.suspect_cards if player_data else [],  # Player's own cards
        'my_player_id': player_id
    }

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)