from copy import deepcopy
import numpy as np

from rlcard.games.kadi import Dealer
from rlcard.games.kadi import Player
from rlcard.games.kadi import Round


class KadiGame:

    def __init__(self, allow_step_back=False, num_players=2):
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = num_players
        self.payoffs = [0 for _ in range(self.num_players)]

    def configure(self, game_config):
        ''' 
        Specifiy some game specific parameters, such as number of players
        Kadi typically supports 2-5 players.
        '''
        self.num_players = game_config.get('game_num_players', self.num_players)

    def init_game(self):
        ''' Initialize players, dealer, round and starting state.

        Returns:
            (dict): The first state for the current player
            (int): Current player's id
        '''
        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize a dealer that can deal cards
        self.dealer = Dealer(self.np_random)

        # Initialize four players to play the game
        self.players = [Player(i, self.np_random) for i in range(self.num_players)]


        # Initialize the round (KadiRound handles Kadi-specific rules: chaining, Niko Kadi, etc.)
        self.round = Round(self.dealer, self.num_players, self.np_random)

        # Deal initial cards
        # Common Kadi starting hand sizes: 4 cards for 2–3 players, 3 for 4–5 players
        cards_per_player = 4 if self.num_players <= 3 else 3
        for player in self.players:
            self.dealer.deal_cards(player, cards_per_player, self.round)

        # flip and perfrom top card
        top_card = self.round.flip_top_card()
        # self.round.perform_top_card(self.players, top_card)

        # Save the hisory for stepping back to the last state.
        self.history = []

        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step(self, action):
        """
        Execute one action and advance the game.

        Args:
            action (str): Action string (e.g. 'h-A', 's-J', 'JOK', 'draw')

        Returns:
            (dict): Next player's state
            (int): Next player's id
        """

        if self.allow_step_back:
            # First snapshot the current state
            his_dealer = deepcopy(self.dealer)
            his_round = deepcopy(self.round)
            his_players = deepcopy(self.players)
            self.history.append((his_dealer, his_players, his_round))

        # Let the round handle the action (may include chaining/sub-turns)
        self.round.proceed_round(self.players, action)
        
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        state = self.round.get_state(self.players, player_id)
        state['num_players'] = self.get_num_players()
        state['current_player'] = self.round.current_player
        return state

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        winner = self.round.winner
        if winner is not None:
            # In most Kadi variants, only one winner (first to empty hand correctly)
            for i in range(self.num_players):
                self.payoffs[i] = 1 if i in winner else -1
        return self.payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_num_players(self):
        ''' Return the number of players in Limit Texas Hold'em

        Returns:
            (int): The number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions():
        ''' Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 56 actions
        '''
        return 56

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            (int): current player's id
        '''
        return self.round.current_player

    def is_over(self):
        ''' Check if the game is over

        Returns:
            (boolean): True if the game is over
        '''
        return self.round.is_over
