"""
Main game module for Kadi game
"""

from copy import deepcopy
import numpy as np

from rlcard.games.kadi.card import KadiCard
from rlcard.games.kadi.player import KadiPlayer
from rlcard.games.kadi.dealer import KadiDealer
from rlcard.games.kadi.judger import KadiJudger


class KadiGame:
    """
    Main Kadi game logic
    """
    
    def __init__(self, allow_step_back=False, num_players=2):
        """
        Initialize Kadi game
        
        Args:
            allow_step_back (bool): Allow stepping back to previous state
            num_players (int): Number of players (2-5)
        """
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = max(2, min(5, num_players))  # Limit to 2-5 players
        self.payoffs = [0] * self.num_players
        self.history = []
    
    def configure(self, game_config):
        """
        Configure game parameters
        
        Args:
            game_config (dict): Configuration with 'game_num_players' key
        """
        self.num_players = game_config.get('game_num_players', 2)
        self.num_players = max(2, min(5, self.num_players))
    
    def init_game(self):
        """
        Initialize a new game
        
        Returns:
            (dict): Initial game state
            (int): Starting player ID
        """
        # Initialize dealer and players
        self.dealer = KadiDealer(self.np_random)
        self.judger = KadiJudger(self.np_random)
        
        self.players = [KadiPlayer(i, self.np_random) for i in range(self.num_players)]
        
        # Deal 3 or 4 cards depending on number of players
        if self.num_players <= 3:
            cards_per_player = 4
        else:
            cards_per_player = 3
        
        for player in self.players:
            self.dealer.deal_cards(player, cards_per_player)
        
        # Flip initial top card (must be valid start card)
        top_card = self.dealer.draw_from_deck()
        while top_card and not top_card.is_valid_start_card():
            self.dealer.add_to_discard_pile(top_card)
            top_card = self.dealer.draw_from_deck()
        
        self.dealer.add_to_discard_pile(top_card)
        
        # Game state variables
        self.current_player = 0
        self.direction = 1  # 1 for clockwise, -1 for counter-clockwise
        self.declared_suit = None  # When Ace is played
        self.current_penalty = 0  # Accumulated penalty
        self.penalty_suit = None  # Suit associated with penalty
        self.last_played_card = None
        self.game_is_over = False  # Renamed from is_over to avoid method conflict
        self.winner = None
        self.previous_player = None
        self.waiting_for_suit_call = False
        
        # Track if players have announced "Niko Kadi"
        for player in self.players:
            player.kadi_announced = False
            player.can_win_next_round = False
        
        self.history = []
        
        return self.get_state(self.current_player), self.current_player
    
    def step(self, action):
        """
        Take a game action
        
        Args:
            action (int): Action index (-1 for draw, otherwise card index)
            
        Returns:
            (dict): Next game state
            (int): Next player ID
        """
        if self.allow_step_back:
            self._save_history()
        

        # Handle phase transitions
        if action == -1:
            self._handle_draw()
        elif action == -2:
            # Handle pass action (only allowed if chaining moves)
            self.previous_player = self.current_player
            self._next_player()
        else:
            self._handle_play(action)


        # Check win condition
        if self.game_is_over:
            return self.get_state(self.current_player), self.current_player
        
        
        return self.get_state(self.current_player), self.current_player
    
    def _save_history(self):
        """Save current game state for step_back"""
        state = {
            'dealer': deepcopy(self.dealer),
            'players': deepcopy(self.players),
            'current_player': self.current_player,
            'direction': self.direction,
            'declared_suit': self.declared_suit,
            'current_penalty': self.current_penalty,
            'penalty_suit': self.penalty_suit,
            'last_played_card': self.last_played_card,
            'game_is_over': self.game_is_over,
            'winner': self.winner,
        }
        self.history.append(state)
    
    def _handle_draw(self):
        """Handle player drawing a card"""
        if self.current_penalty > 0:
            # If there's a penalty, player must draw penalty cards
            for _ in range(self.current_penalty):
                card = self.dealer.draw_from_deck()
                if card:
                    self.players[self.current_player].add_card(card)
            # Reset penalty after drawing
            self.current_penalty = 0
            self.declared_suit = None
        else:
            card = self.dealer.draw_from_deck()
            if card:
                self.players[self.current_player].add_card(card)
                # Reset declared suit after drawing
                self.declared_suit = None
            
        # Move to next player
        self.previous_player = self.current_player
        self._next_player()
    
    def _handle_play(self, action):
        """
        Handle playing a card
        
        Args:
            action (int): Index of card to play
        """
        player = self.players[self.current_player]

        if self.waiting_for_suit_call:
            if action == -3:
                self.declared_suit = 'H'
            elif action == -4:
                self.declared_suit = 'D'
            elif action == -5:
                self.declared_suit = 'C'
            elif action == -6:
                self.declared_suit = 'S'
            else:
                print("Invalid action. Selecting default suit")
                self.declared_suit = 'H'
           
            self.previous_player = self.current_player
            self._next_player()
            self.waiting_for_suit_call = False

        else:

            card = player.hand[action]
            
            # Verify play is legal
            top_card = self.dealer.get_top_card()
            legal_actions = self.judger.get_legal_actions(
                player, top_card, self.declared_suit, self.current_penalty, self.previous_player
            )
            
            if action not in legal_actions:
                # Invalid play - draw penalty card
                print(f"Invalid action: {action}, Legal actions: {legal_actions}")
                self._handle_draw()
                return
            
            # Remove card from hand
            player.remove_card(card)
            self.dealer.add_to_discard_pile(card)
            self.last_played_card = card
            
            # Handle special card effects
            card_type = card.get_type()
            
            if card_type == 'jump':
                self._handle_jump()
            elif card_type == 'kickback':
                self._handle_kickback()
            elif card_type == 'question':
                self._handle_question()
            elif card_type == 'penalty':
                self._handle_penalty(card)
            elif card_type == 'answer':
                if card.rank == 'A':
                    self._handle_ace()
                else:
                    self.current_penalty = 0
                    # self.declared_suit = None
                    self.previous_player = self.current_player
                    # Check if there is a card in hand with the same rank
                    if not any(c.rank == card.rank for c in player.hand):
                        print("Cannot chain. Next player")
                        self._next_player()
        
            # Check if player can win next round
            if player.get_hand_size() == 0 and card.rank in ["4","5","6","7","9","10"]:
                self.game_is_over = True
                player.status = 'cardless'
                if player.kadi_announced:
                    self.winner = [player.player_id]
                else:
                    # Player won but didn't announce Niko Kadi - invalid win
                    self.game_is_over = False
            elif self.judger.can_win_with_cards(player) and not player.kadi_announced:
                player.can_win_next_round = True
                player.kadi_announced = True
            else:
                player.can_win_next_round = False

    
    def _handle_jump(self):
        """Handle Jump card (J) - skip next player"""
        # Next player will be skipped, so we'll move twice
        self._next_player()
        self._next_player()
    
    def _handle_kickback(self):
        """Handle Kickback card (K) - reverse direction"""
        self.direction *= -1
        self.previous_player = self.current_player
        if not any(c.rank == "K" for c in self.players[self.current_player].hand):
            print("Cannot chain. Next player")
            self._next_player()

    
    def _handle_question(self):
        """Handle Question card (Q or 8) - requires answer card"""
        # Question effect is automatic - next player must follow
        pass
    
    def _handle_penalty(self, card):
        """Handle Penalty card (2 or 3)"""
        penalty_value = card.get_penalty_value()
        print(f"Applying penalty of {penalty_value} Current penalty: {self.current_penalty}")
        self.current_penalty += penalty_value
        self.penalty_suit = card.suit

        self.previous_player = self.current_player

        if not any(c.rank == card.rank for c in self.players[self.current_player].hand):
            print("Cannot chain. Next player")
            self._next_player()

        # self._next_player()
    
    def _handle_ace(self):
        """Handle Ace card - declare suit"""
        if self.current_penalty > 0:
            self.current_penalty = 0
            self.declared_suit = None
            self.waiting_for_suit_call = False
            self.previous_player = self.current_player
            self._next_player()
        else:
            self.waiting_for_suit_call = True
    
    def _next_player(self):
        """Move to next player"""
        self.current_player = (self.current_player + self.direction) % self.num_players
    
    def get_state(self, player_id):
        """
        Get current game state for a player
        
        Args:
            player_id (int): Player ID
            
        Returns:
            (dict): Game state for the player
        """
        state = {
            'hand': [card.get_index() for card in self.players[player_id].hand],
            'num_players': self.num_players,
            'current_player': self.current_player,
            'direction': self.direction,
            'top_card': self.dealer.get_top_card().get_index() if self.dealer.get_top_card() else None,
            'discard_pile_size': self.dealer.get_discard_pile_size(),
            'deck_size': self.dealer.get_deck_size(),
            'other_players_hands': [
                len(self.players[i].hand) for i in range(self.num_players) if i != player_id
            ],
            'declared_suit': self.declared_suit,
            'current_penalty': self.current_penalty,
            'kadi_announced': self.players[player_id].kadi_announced,
            'can_win_next_round': self.players[player_id].can_win_next_round,
        }
        
        return state
    
    def get_legal_actions(self):
        """
        Get legal actions for current player
        
        Returns:
            (list): List of legal action indices
        """
        player = self.players[self.current_player]
        top_card = self.dealer.get_top_card()

        actions = []

        if self.waiting_for_suit_call:
            # If waiting for suit call, only legal actions are to declare a suit
            actions = [-3, -4, -5, -6]
        else:
            actions = self.judger.get_legal_actions(
                player, top_card, self.declared_suit, self.current_penalty, self.previous_player
            )
        
        return actions
    
    def get_num_players(self):
        """Get number of players"""
        return self.num_players
    
    @staticmethod
    def get_num_actions():
        """Get total number of possible actions"""
        # 52 cards + 1 draw action = 53
        return 53
    
    def get_payoffs(self):
        """
        Get game payoffs
        
        Returns:
            (list): Payoff for each player
        """
        payoffs = [0] * self.num_players
        
        if self.winner:
            payoffs[self.winner[0]] = 1
            for i in range(self.num_players):
                if i != self.winner[0]:
                    payoffs[i] = -1
        
        return payoffs
    
    def step_back(self):
        """
        Step back to previous game state
        
        Returns:
            (bool): True if successful
        """
        if not self.history:
            return False
        
        state = self.history.pop()
        self.dealer = state['dealer']
        self.players = state['players']
        self.current_player = state['current_player']
        self.direction = state['direction']
        self.declared_suit = state['declared_suit']
        self.current_penalty = state['current_penalty']
        self.penalty_suit = state['penalty_suit']
        self.last_played_card = state['last_played_card']
        self.game_is_over = state['game_is_over']
        self.winner = state['winner']
        
        return True
    
    def is_game_over(self):
        """Check if game is over"""
        return self.game_is_over or any(p.status == 'cardless' for p in self.players)
    
    def get_player_id(self):
        """
        Get current player ID
        
        Returns:
            int: Current player ID
        """
        return self.current_player
    
    def is_over(self):
        """
        Check if game is over (method called by environment)
        
        Returns:
            bool: True if game is over
        """
        return self.game_is_over or any(p.status == 'cardless' for p in self.players)
