"""
Kadi environment for RLCard
"""

import numpy as np
from rlcard.envs.env import Env
from rlcard.games.kadi import KadiGame, KadiCard
from rlcard.games.kadi.utils import ACTION_SPACE, ACTION_LIST, index_to_action


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
        # Define a fixed observation vector size for function approximation
        # - Hand one-hot: 52
        # - Top card one-hot: 52
        # - Declared suit one-hot: 4
        # - Direction: 1
        # - Current penalty: 1
        # Total obs length = 110
        return {'obs_shape': (110,), 'obs_type': 'float'}
    
    def _extract_state(self, state):
        """
        Extract state representation suitable for agents
        
        Args:
            state (dict): Raw state from game
            
        Returns:
            (dict): Processed state with legal actions
        """
        # Build a fixed-size observation vector and unified action space
        # Use ACTION_SPACE mapping from games/kadi/jsondata/action_space.json
        def card_to_global_index(card_str):
            if card_str is None:
                return None
            return ACTION_SPACE.get(card_str)

        # Build obs
        obs = []
        # Hand one-hot
        hand_onehot = [0] * 52
        for c in state.get('hand', []):
            gi = card_to_global_index(c)
            if gi is not None:
                hand_onehot[gi] = 1
        obs.extend(hand_onehot)

        # Top card one-hot
        top_onehot = [0] * 52
        top_card = state.get('top_card')
        if top_card is not None:
            gi = card_to_global_index(top_card)
            if gi is not None:
                top_onehot[gi] = 1
        obs.extend(top_onehot)
        # Declared suit one-hot
        suits = ['H', 'D', 'C', 'S']
        declared = state.get('declared_suit')
        decl_onehot = [0] * 4
        if declared in suits:
            decl_onehot[suits.index(declared)] = 1
        obs.extend(decl_onehot)

        # Direction
        obs.append(state.get('direction', 1))
        # Current penalty
        obs.append(state.get('current_penalty', 0))

        state['obs'] = np.array(obs, dtype=np.float32)

        # Map legal actions from game (hand indices or negative codes) to global action indices
        legal = self._get_legal_actions()
        # special_map handled via ACTION_SPACE entries keyed by their string form (e.g. '-1')

        legal_global = []
        raw_legal = []
        # Use the player id from the provided state when mapping legal actions
        player = state.get('current_player', self.game.current_player)
        for a in legal:
            if isinstance(a, int) and a >= 0:
                # a is index in player's hand
                try:
                    card_str = self.game.players[player].hand[a].get_index()
                except Exception:
                    # stale index -> skip
                    continue
                gi = card_to_global_index(card_str)
                if gi is not None:
                    legal_global.append(gi)
                    raw_legal.append(card_str)
            else:
                gi = ACTION_SPACE.get(str(a))
                if gi is not None:
                    legal_global.append(gi)
                    if a == -1:
                        raw_legal.append('DRAW')
                    elif a == -2:
                        raw_legal.append('PASS')
                    elif a == -3:
                        raw_legal.append('H')
                    elif a == -4:
                        raw_legal.append('D')
                    elif a == -5:
                        raw_legal.append('C')
                    elif a == -6:
                        raw_legal.append('S')

        state['legal_actions'] = {int(a): None for a in legal_global}
        state['raw_legal_actions'] = raw_legal

        return state
    
    def _decode_action(self, action):
        """
        Decode action index to card or draw
        
        Args:
            action (int): Action index
            
        Returns:
            int: Card index or -1 for draw
        """
        # Action expected to be an integer in the fixed global space [0..57]
        # Use ACTION_LIST via index_to_action helper
        act = index_to_action(action)
        if act is None:
            return -1
        # Special actions
        if act == 'DRAW':
            return -1
        if act == 'PASS':
            return -2
        if act in ['H', 'D', 'C', 'S']:
            # map declared suit to corresponding negative code
            suit_to_code = {'H': -3, 'D': -4, 'C': -5, 'S': -6}
            return suit_to_code[act]

        # Otherwise act is a card string like 'H4': find it in player's hand
        player = self.game.current_player
        for i, c in enumerate(self.game.players[player].hand):
            if c.get_index() == act:
                return i
        return -1
    
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
        info['waiting_for_suit_call'] = self.game.waiting_for_suit_call
        info['previous_player'] = self.game.previous_player
        
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
            player.hand = [KadiCard(card_index[:1],card_index[1:]) for card_index in player_info.get('hand', [])]
            player.status = player_info.get('status', 'active')
            player.kadi_announced = player_info.get('kadi_announced', False)
        
        self.game.dealer.discard_pile = [KadiCard(card_index[:1],card_index[1:]) for card_index in info.get('discard_pile', [])]
        self.game.dealer.deck = [KadiCard(card_index[:1],card_index[1:]) for card_index in info.get('deck', [])]
        self.game.direction = info.get('direction', 1)
        self.game.declared_suit = info.get('declared_suit', None)
        self.game.current_penalty = info.get('current_penalty', 0)
        self.game.current_player = info.get('current_player', 0)
        self.game.dealer.top_card = KadiCard(info.get('top_card')[:1], info.get('top_card')[1:]) if info.get('top_card') is not None else None
        self.game.waiting_for_suit_call = info.get("waiting_for_suit_call", False)
        self.game.previous_player = info.get("previous_player")

    def game_over(self):
        return self.game.is_over()
