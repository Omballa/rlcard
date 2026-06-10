"""
Kadi environment for RLCard
"""

import numpy as np
from rlcard.envs.env import Env
from rlcard.games.kadi import KadiGame


class KadiEnv(Env):
    """
    Kadi environment for RLCard reinforcement learning
    """
    
    def __init__(self, config):
        """
        Initialize Kadi environment
        
        Args:
            config (dict): Configuration dictionary
        """
        self.name = 'kadi'
        self.game = KadiGame(allow_step_back=config.get('allow_step_back', False))
        self.default_game_config = {
            'game_num_players': 2,
        }
        
        super().__init__(config)
        
        self.state_space = self._get_state_space()
    
    def _get_state_space(self):
        """Get state space representation"""
        # State space includes:
        # - Hand: up to 54 cards (binary features)
        # - Top card: 54 options
        # - Other players' hand sizes: up to num_players-1 integers
        # - Game state: direction, penalty, etc.
        return None
    
    def _extract_state(self, state):
        """
        Extract state representation suitable for agents
        
        Args:
            state (dict): Raw state from game
            
        Returns:
            (dict): Processed state with legal actions
        """
        # Add legal actions to state
        legal_actions = self._get_legal_actions()
        state['legal_actions'] = {action: None for action in legal_actions}
        return state
    
    def _decode_action(self, action):
        """
        Decode action index to card or draw
        
        Args:
            action (int): Action index
            
        Returns:
            int: Card index or -1 for draw
        """
        legal_actions = self._get_legal_actions()
        
        if action >= len(legal_actions):
            # If action is out of bounds, return draw
            return -1
        
        return legal_actions[action]
    
    def _get_legal_actions(self):
        """Get legal actions for current player"""
        return self.game.get_legal_actions()
    
    def get_payoffs(self):
        """
        Get game payoffs
        
        Returns:
            (list): Payoff for each player
        """
        return self.game.get_payoffs()
    
    def get_perfect_information(self):
        """
        Get perfect information about the game
        
        Returns:
            (dict): Complete game information
        """
        info = {}
        
        for player in self.game.players:
            player_info = {
                'hand': [card.get_index() for card in player.hand],
                'hand_size': len(player.hand),
                'status': player.status,
                'kadi_announced': player.kadi_announced,
                'legal_moves': self.game.get_legal_actions() if player.player_id == self.game.current_player else [],
            }
            info[f'player_{player.player_id}'] = player_info
        
        info['top_card'] = self.game.dealer.get_top_card().get_index() if self.game.dealer.get_top_card() else None
        info['current_player'] = self.game.current_player
        info['direction'] = self.game.direction
        info['declared_suit'] = self.game.declared_suit
        info['current_penalty'] = self.game.current_penalty
        info['deck'] = self.game.dealer.deck
        info['discard_pile'] = self.game.dealer.discard_pile
        
        return info
    
    def set_from_perfect_information(self, info):
        """
        Set game state from perfect information
        
        Args:
            info (dict): Complete game information
        """
        # This method can be implemented to allow setting the game state from perfect information
        for player in self.game.players:
            player_info = info.get(f'player_{player.player_id}', {})
            player.hand = [self.game.cards[card_index] for card_index in player_info.get('hand', [])]
            player.status = player_info.get('status', 'active')
            player.kadi_announced = player_info.get('kadi_announced', False)
        
        self.game.dealer.discard_pile = info.get('discard_pile', [])
        self.game.dealer.deck = info.get('deck', [])
        self.game.direction = info.get('direction', 1)
        self.game.declared_suit = info.get('declared_suit', None)
        self.game.current_penalty = info.get('current_penalty', 0)
        self.game.current_player = info.get('current_player', 0)
        self.game.dealer.top_card = self.game.cards[info.get('top_card')] if info.get('top_card') is not None else None
