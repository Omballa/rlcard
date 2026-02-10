class KadiPlayer:
    """
    A player in the Kadi card game.
    
    In Kadi:
    - Players have a hand of cards.
    - No 'stack' is typically used (unlike Uno's discard pile per player).
    - Additional state may be needed for game-specific mechanics:
      - Whether the player has announced "Niko Kadi" (last turn declaration)
      - Sometimes tracking pending penalties or chaining status (but usually handled in Round)
    """

    def __init__(self, player_id, np_random=None):
        """
        Initialize a Kadi player.

        Args:
            player_id (int): Unique identifier for this player (0, 1, 2, ...)
            np_random (numpy.random.RandomState, optional): Random generator
        """
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []                    # List of KadiCard objects

        # Kadi-specific attributes (optional / depending on variant)
        self.niko_kadi_declared = False   # Whether player announced "Niko Kadi" last turn
        self.has_won = False              # Set when player legally empties hand

        # If your variant tracks per-player discard or played cards separately:
        # self.played_this_turn = []      # (usually handled in Round instead)

    def get_player_id(self):
        """
        Return the player's ID.

        Returns:
            int: The player's unique identifier
        """
        return self.player_id

    def get_hand_size(self):
        """
        Convenience method: number of cards currently in hand.

        Returns:
            int: len(self.hand)
        """
        return len(self.hand)

    def has_announced_niko_kadi(self):
        """
        Check if the player has declared "Niko Kadi" (ready to win next turn).

        Returns:
            bool: True if declared in the previous turn
        """
        return self.niko_kadi_declared

    def reset(self):
        """
        Reset player state for a new game.
        """
        self.hand = []
        self.niko_kadi_declared = False
        self.has_won = False

    def __str__(self):
        """
        String representation (useful for debugging).
        """
        cards_str = ", ".join(card.str for card in self.hand) if self.hand else "empty"
        status = "Niko Kadi declared" if self.niko_kadi_declared else ""
        return f"Player {self.player_id} ({len(self.hand)} cards): {cards_str} {status}"

    def __repr__(self):
        return self.__str__()