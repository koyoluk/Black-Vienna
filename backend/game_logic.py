import random
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

class GameStatus(Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    ENDED = "ended"

class PlayerStatus(Enum):
    ACTIVE = "active"
    ELIMINATED = "eliminated"
    WINNER = "winner"

@dataclass
class InvestigationResult:
    """Records the result of an investigation"""
    round_number: int
    investigator_id: str
    questioned_player_id: str
    card_letters: List[str]
    coins_taken: int
    is_double_investigation: bool = False

@dataclass
class Player:
    player_id: str
    name: str
    suspect_cards: List[str] = field(default_factory=list)
    has_been_investigator: bool = False
    status: PlayerStatus = PlayerStatus.ACTIVE
    notes: Dict = field(default_factory=dict)  # For future frontend note-taking feature

@dataclass
class InvestigationCard:
    card_id: str
    letters: List[str]
    deck_index: int
    has_been_used: bool = False
    coins_when_used: Optional[int] = None
    used_by_player_id: Optional[str] = None
    questioned_player_id: Optional[str] = None

class Game:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: List[Player] = []
        self.hidden_suspects: List[str] = []
        self.all_suspects: List[str] = self.create_suspects()
        
        # Investigation cards and decks
        self.investigation_cards: List[InvestigationCard] = []
        self.investigation_decks: List[List[InvestigationCard]] = [[], [], []]
        self.face_up_cards: List[Optional[InvestigationCard]] = [None, None, None]
        self.used_investigation_cards: List[InvestigationCard] = []
        
        # Game state
        self.central_coins: int = 40
        self.investigation_history: List[InvestigationResult] = []
        self.current_investigator_index: int = 0
        self.round_count: int = 0
        self.total_investigations: int = 0
        self.double_investigation_enabled: bool = False
        self.game_status: GameStatus = GameStatus.WAITING
        
        # Track if each player has been investigator
        self.players_been_investigator: Set[str] = set()
        
    @staticmethod
    def create_suspects() -> List[str]:
        """Create all 27 suspect cards"""
        return [chr(i) for i in range(65, 91)] + ["Ω"]  # A-Z + Omega (using Ω instead of O:)
    
    def create_investigation_cards(self) -> List[InvestigationCard]:
        """Create 36 investigation cards with proper constraints"""
        # Proper investigation card combinations for Black Vienna
        # Each card has 3 letters, no two cards share more than 1 letter
        card_combinations = [
            ["A", "B", "C"], ["A", "D", "E"], ["A", "F", "G"],
            ["A", "H", "I"], ["A", "J", "K"], ["A", "L", "M"],
            ["B", "D", "F"], ["B", "H", "J"], ["B", "L", "N"],
            ["B", "O", "P"], ["B", "Q", "R"], ["B", "S", "T"],
            ["C", "D", "H"], ["C", "E", "J"], ["C", "F", "L"],
            ["C", "G", "N"], ["C", "I", "O"], ["C", "K", "Q"],
            ["D", "G", "J"], ["D", "I", "L"], ["D", "K", "N"],
            ["D", "M", "O"], ["D", "P", "Q"], ["D", "R", "S"],
            ["E", "F", "H"], ["E", "G", "L"], ["E", "I", "N"],
            ["E", "K", "O"], ["E", "M", "Q"], ["E", "P", "S"],
            ["F", "I", "J"], ["F", "K", "M"], ["F", "N", "P"],
            ["F", "O", "R"], ["F", "Q", "T"], ["F", "S", "Ω"]
        ]
        
        # Add remaining cards with letters U, V, W, X, Y, Z
        additional_combinations = [
            ["G", "H", "K"], ["G", "I", "M"], ["G", "O", "Q"],
            ["H", "L", "O"], ["H", "M", "N"], ["H", "P", "R"],
            ["I", "P", "Q"], ["I", "R", "T"], ["I", "S", "U"],
            ["J", "L", "P"], ["J", "M", "R"], ["J", "N", "S"],
            ["K", "L", "R"], ["K", "P", "S"], ["K", "T", "U"],
            ["L", "Q", "S"], ["L", "T", "Ω"], ["M", "P", "T"],
            ["M", "S", "U"], ["N", "O", "T"], ["N", "Q", "U"],
            ["O", "S", "V"], ["P", "U", "V"], ["Q", "V", "W"],
            ["R", "U", "W"], ["S", "W", "X"], ["T", "V", "X"],
            ["U", "X", "Y"], ["V", "Y", "Z"], ["W", "Y", "Ω"],
            ["X", "Z", "Ω"], ["Y", "A", "T"], ["Z", "B", "U"]
        ]
        
        # Combine and limit to 36 cards
        all_combinations = card_combinations[:36]
        
        cards = []
        for i, combo in enumerate(all_combinations):
            card = InvestigationCard(
                card_id=f"inv_card_{i:02d}",
                letters=combo,
                deck_index=-1,  # Will be set when distributed to decks
                has_been_used=False
            )
            cards.append(card)
        
        return cards
    
    def setup_game(self, players_data: List[Dict]) -> None:
        """Set up the game with players"""
        # Create players
        for player_data in players_data:
            player = Player(
                player_id=player_data['id'],
                name=player_data['name']
            )
            self.players.append(player)
        
        # Pick 3 hidden suspects
        self.hidden_suspects = random.sample(self.all_suspects, 3)
        
        # Distribute remaining suspects to players
        remaining_suspects = [s for s in self.all_suspects if s not in self.hidden_suspects]
        random.shuffle(remaining_suspects)
        
        # Calculate cards per player
        num_players = len(self.players)
        cards_per_player = len(remaining_suspects) // num_players
        extra_cards = len(remaining_suspects) % num_players
        
        card_index = 0
        for i, player in enumerate(self.players):
            num_cards = cards_per_player + (1 if i < extra_cards else 0)
            player.suspect_cards = remaining_suspects[card_index:card_index + num_cards]
            card_index += num_cards
        
        # Create and distribute investigation cards
        self.investigation_cards = self.create_investigation_cards()
        random.shuffle(self.investigation_cards)
        
        # Split into 3 decks of 12 cards each
        for deck_idx in range(3):
            deck_cards = self.investigation_cards[deck_idx * 12:(deck_idx + 1) * 12]
            for card in deck_cards:
                card.deck_index = deck_idx
            self.investigation_decks[deck_idx] = deck_cards
            # Set top card as face-up
            if deck_cards:
                self.face_up_cards[deck_idx] = deck_cards[0]
        
        # Set initial investigator randomly
        self.current_investigator_index = random.randint(0, num_players - 1)
        
        self.game_status = GameStatus.ACTIVE
    
    def get_current_investigator(self) -> Optional[Player]:
        """Get the current investigator player"""
        if 0 <= self.current_investigator_index < len(self.players):
            return self.players[self.current_investigator_index]
        return None
    
    def get_active_players(self) -> List[Player]:
        """Get list of active (non-eliminated) players"""
        return [p for p in self.players if p.status == PlayerStatus.ACTIVE]
    
    def can_use_double_investigation(self) -> bool:
        """Check if double investigation is available"""
        # After 6 total investigations and each player has been investigator at least once
        all_players_investigated = len(self.players_been_investigator) >= len(self.get_active_players())
        return self.total_investigations >= 6 and all_players_investigated
    
    def get_zero_coin_cards(self) -> List[InvestigationCard]:
        """Get all previously used investigation cards that resulted in 0 coins"""
        return [
            card for card in self.used_investigation_cards
            if card.coins_when_used == 0
        ]
    
    def investigate(self, investigator_id: str, questioned_player_id: str, 
                   card_index: int, double_card_id: Optional[str] = None) -> Dict:
        """Perform an investigation"""
        # Validate investigator
        investigator = next((p for p in self.players if p.player_id == investigator_id), None)
        if not investigator or investigator.status != PlayerStatus.ACTIVE:
            return {"error": "Invalid investigator"}
        
        if self.players[self.current_investigator_index].player_id != investigator_id:
            return {"error": "Not your turn"}
        
        # Validate questioned player
        questioned = next((p for p in self.players if p.player_id == questioned_player_id), None)
        if not questioned or questioned.status != PlayerStatus.ACTIVE:
            return {"error": "Invalid player to question"}
        
        if questioned.player_id == investigator_id:
            return {"error": "Cannot question yourself"}
        
        # Get the investigation card
        if card_index < 0 or card_index >= 3 or not self.face_up_cards[card_index]:
            return {"error": "Invalid card selection"}
        
        investigation_card = self.face_up_cards[card_index]
        
        # Count matching letters
        matching_count = sum(
            1 for letter in investigation_card.letters 
            if letter in questioned.suspect_cards
        )
        
        # Take coins from central pool
        if self.central_coins < matching_count:
            matching_count = self.central_coins  # Take remaining coins
        self.central_coins -= matching_count
        
        # Record the investigation
        result = InvestigationResult(
            round_number=self.round_count,
            investigator_id=investigator_id,
            questioned_player_id=questioned_player_id,
            card_letters=investigation_card.letters.copy(),
            coins_taken=matching_count,
            is_double_investigation=False
        )
        self.investigation_history.append(result)
        
        # Mark card as used
        investigation_card.has_been_used = True
        investigation_card.coins_when_used = matching_count
        investigation_card.used_by_player_id = investigator_id
        investigation_card.questioned_player_id = questioned_player_id
        self.used_investigation_cards.append(investigation_card)
        
        # Draw next card from deck
        deck_idx = investigation_card.deck_index
        current_deck = self.investigation_decks[deck_idx]
        if current_deck:
            next_card_idx = current_deck.index(investigation_card) + 1
            if next_card_idx < len(current_deck):
                self.face_up_cards[deck_idx] = current_deck[next_card_idx]
            else:
                self.face_up_cards[deck_idx] = None
        
        # Handle double investigation if requested
        double_result = None
        if double_card_id and self.can_use_double_investigation():
            double_card = next(
                (c for c in self.used_investigation_cards if c.card_id == double_card_id),
                None
            )
            if double_card and double_card.coins_when_used == 0:
                # Count matching letters for double investigation
                double_matching = sum(
                    1 for letter in double_card.letters 
                    if letter in questioned.suspect_cards
                )
                
                # Take coins
                if self.central_coins < double_matching:
                    double_matching = self.central_coins
                self.central_coins -= double_matching
                
                double_result = InvestigationResult(
                    round_number=self.round_count,
                    investigator_id=investigator_id,
                    questioned_player_id=questioned_player_id,
                    card_letters=double_card.letters.copy(),
                    coins_taken=double_matching,
                    is_double_investigation=True
                )
                self.investigation_history.append(double_result)
        
        # Update game state
        self.total_investigations += 1
        investigator.has_been_investigator = True
        self.players_been_investigator.add(investigator_id)
        
        # Check if double investigation should be enabled
        if not self.double_investigation_enabled:
            self.double_investigation_enabled = self.can_use_double_investigation()
        
        # Move to next investigator
        self.next_turn()
        
        # Check end game conditions
        if self.check_end_conditions():
            self.game_status = GameStatus.ENDED
        
        return {
            "success": True,
            "result": result,
            "double_result": double_result,
            "game_ended": self.game_status == GameStatus.ENDED
        }
    
    def next_turn(self) -> None:
        """Move to the next active player's turn"""
        active_players = self.get_active_players()
        if not active_players:
            self.game_status = GameStatus.ENDED
            return
        
        # Find next active player
        attempts = 0
        while attempts < len(self.players):
            self.current_investigator_index = (self.current_investigator_index + 1) % len(self.players)
            if self.players[self.current_investigator_index].status == PlayerStatus.ACTIVE:
                self.round_count += 1
                break
            attempts += 1
    
    def make_guess(self, player_id: str, guessed_suspects: List[str]) -> Dict:
        """Player makes a guess at the hidden suspects"""
        player = next((p for p in self.players if p.player_id == player_id), None)
        if not player or player.status != PlayerStatus.ACTIVE:
            return {"error": "Invalid player or already eliminated"}
        
        # Check if it's player's turn
        if self.players[self.current_investigator_index].player_id != player_id:
            return {"error": "Can only guess during your turn"}
        
        # Validate guess format
        if len(guessed_suspects) != 3:
            return {"error": "Must guess exactly 3 suspects"}
        
        # Check if guess is correct
        if set(guessed_suspects) == set(self.hidden_suspects):
            player.status = PlayerStatus.WINNER
            self.game_status = GameStatus.ENDED
            return {
                "success": True,
                "correct": True,
                "winner": player.name,
                "solution": self.hidden_suspects
            }
        else:
            player.status = PlayerStatus.ELIMINATED
            
            # Check if all players are eliminated
            if not self.get_active_players():
                self.game_status = GameStatus.ENDED
            else:
                # Move to next turn if game continues
                self.next_turn()
            
            return {
                "success": True,
                "correct": False,
                "eliminated": True
            }
    
    def check_end_conditions(self) -> bool:
        """Check if game should end"""
        # Coin limit: 37 or more coins removed
        coins_removed = 40 - self.central_coins
        if coins_removed >= 37:
            return True
        
        # Card limit: All investigation cards used
        all_cards_used = all(
            card is None for card in self.face_up_cards
        )
        if all_cards_used:
            return True
        
        # No active players left
        if not self.get_active_players():
            return True
        
        return False
    
    def get_game_state(self) -> Dict:
        """Get the current game state"""
        return {
            "game_id": self.game_id,
            "status": self.game_status.value,
            "players": [
                {
                    "id": p.player_id,
                    "name": p.name,
                    "status": p.status.value,
                    "has_been_investigator": p.has_been_investigator,
                    "card_count": len(p.suspect_cards)
                }
                for p in self.players
            ],
            "current_investigator_index": self.current_investigator_index,
            "current_investigator": self.get_current_investigator().name if self.get_current_investigator() else None,
            "central_coins": self.central_coins,
            "coins_used": 40 - self.central_coins,
            "face_up_cards": [
                {
                    "deck_index": i,
                    "card": {
                        "id": card.card_id,
                        "letters": card.letters
                    } if card else None
                }
                for i, card in enumerate(self.face_up_cards)
            ],
            "investigation_history": [
                {
                    "round": r.round_number,
                    "investigator": next(p.name for p in self.players if p.player_id == r.investigator_id),
                    "questioned": next(p.name for p in self.players if p.player_id == r.questioned_player_id),
                    "letters": r.card_letters,
                    "coins": r.coins_taken,
                    "is_double": r.is_double_investigation
                }
                for r in self.investigation_history
            ],
            "double_investigation_enabled": self.double_investigation_enabled,
            "zero_coin_cards": [
                {
                    "id": card.card_id,
                    "letters": card.letters,
                    "used_by": next((p.name for p in self.players if p.player_id == card.used_by_player_id), "Unknown"),
                    "questioned": next((p.name for p in self.players if p.player_id == card.questioned_player_id), "Unknown")
                }
                for card in self.get_zero_coin_cards()
            ],
            "total_investigations": self.total_investigations,
            "round_count": self.round_count
        }
    
    def get_player_view(self, player_id: str) -> Dict:
        """Get game state from a specific player's perspective"""
        player = next((p for p in self.players if p.player_id == player_id), None)
        if not player:
            return {"error": "Player not found"}
        
        state = self.get_game_state()
        state["my_cards"] = player.suspect_cards
        state["my_status"] = player.status.value
        state["is_my_turn"] = (
            self.get_current_investigator() and 
            self.get_current_investigator().player_id == player_id
        )
        
        # Add questionable players (for investigation)
        if state["is_my_turn"]:
            state["can_question"] = [
                {"id": p.player_id, "name": p.name}
                for p in self.players
                if p.player_id != player_id and p.status == PlayerStatus.ACTIVE
            ]
        
        return state