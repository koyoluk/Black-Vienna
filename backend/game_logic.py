import random
from typing import List, Dict, Optional

class Player:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.suspect_cards = []
        self.has_been_investigator = False
        self.is_eliminated = False

class InvestigationCard:
    def __init__(self, card_id: str, letters: List[str]):
        self.card_id = card_id
        self.letters = letters

class Game:
    def __init__(self):
        self.game_id = None
        self.players = []
        self.hidden_suspects = []
        self.investigation_decks = [[], [], []]
        self.face_up_cards = []
        self.central_coins = 40
        self.investigation_history = []
        self.current_investigator = 0
        self.round_count = 0
        self.double_investigation_enabled = False
        self.game_status = "waiting"  # waiting, active, ended

def create_suspects():
    """Create all 27 suspect cards"""
    return [chr(i) for i in range(65, 91)] + ["O:"]  # A-Z + O:

def create_investigation_cards():
    """Create 36 investigation cards - simplified version for now"""
    suspects = create_suspects()
    cards = []
    
    # For now, create cards manually or randomly
    # This needs proper algorithm later but let's get game working first
    card_combinations = [
        ["A", "C", "L"], ["A", "J", "M"], ["A", "O", "S"],
        ["A", "P", "Q"], ["B", "C", "Y"], ["B", "H", "V"],
        ["B", "L", "M"], ["B", "Q", "T"], ["C", "F", "I"],
        ["C", "S", "X"], ["D", "H", "R"], ["D", "J", "Z"],
        ["D", "L", "S"], ["D", "V", "Y"], ["E", "G", "W"],
        ["E", "N", "Q"], ["E", "O:", "R"], ["E", "U", "V"],
        ["F", "O:", "Y"], ["F", "R", "X"], ["F", "S", "Z"],
        ["G", "K", "O"], ["G", "P", "X"], ["H", "N", "O:"],
        ["H", "U", "Z"], ["I", "O:", "W"], ["I", "P", "R"],
        ["I", "T", "Z"], ["J", "M", "O"], ["J", "Q", "X"],
        ["J", "T", "Y"], ["K", "M", "U"], ["K", "N", "T"],
        ["K", "P", "W"], ["L", "N", "V"], ["O", "U", "W"]
    ]
    
    for i, combo in enumerate(card_combinations[:36]):
        cards.append(InvestigationCard(f"card_{i}", combo))
    
    return cards

def setup_game(num_players: int) -> Game:
    game = Game()
    
    # Create suspects and pick 3 hidden
    all_suspects = create_suspects()
    game.hidden_suspects = random.sample(all_suspects, 3)
    
    # Distribute remaining suspects to players
    remaining_suspects = [s for s in all_suspects if s not in game.hidden_suspects]
    random.shuffle(remaining_suspects)
    cards_per_player = len(remaining_suspects) // num_players
    
    for i in range(num_players):
        start_idx = i * cards_per_player
        end_idx = start_idx + cards_per_player
        player = Player(f"player_{i}", f"Player {i+1}")
        player.suspect_cards = remaining_suspects[start_idx:end_idx]
        game.players.append(player)
    
    # Create investigation decks
    investigation_cards = create_investigation_cards()
    random.shuffle(investigation_cards)
    
    # Split into 3 decks of 12
    for i in range(3):
        deck = investigation_cards[i*12:(i+1)*12]
        game.investigation_decks[i] = deck
        game.face_up_cards.append(deck[0])  # Top card face up
    
    game.game_status = "active"
    return game