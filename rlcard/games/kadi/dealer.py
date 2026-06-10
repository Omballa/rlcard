"""
Dealer module for Kadi game
"""

from rlcard.games.kadi.card import KadiCard


class KadiDealer:
    """
    Manages the deck and dealing cards for Kadi game
    """
    
    def __init__(self, np_random):
        """
        Initialize the dealer
        
        Args:
            np_random: NumPy random state
        """
        self.np_random = np_random
        self.deck = []
        self.discard_pile = []
        self.shuffle_deck()
    
    def shuffle_deck(self):
        """
        Create and shuffle a 52-card standard deck (no jokers)
        """
        self.deck = []
        
        suits = ['H', 'D', 'C', 'S']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        # Create standard 52 cards
        for suit in suits:
            for rank in ranks:
                self.deck.append(KadiCard(suit, rank))
        
        self.np_random.shuffle(self.deck)
    
    def deal_card(self, player):
        """
        Deal one card to a player
        
        Args:
            player (KadiPlayer): Player to deal to
            
        Returns:
            KadiCard: Card dealt
        """
        if len(self.deck) == 0:
            self.replenish_deck()
        
        card = self.deck.pop()
        player.add_card(card)
        return card
    
    def deal_cards(self, player, num):
        """
        Deal multiple cards to a player
        
        Args:
            player (KadiPlayer): Player to deal to
            num (int): Number of cards to deal
        """
        for _ in range(num):
            if len(self.deck) == 0:
                self.replenish_deck()
            self.deal_card(player)
    
    def replenish_deck(self):
        """
        Replenish the deck from discard pile when it runs out
        
        The top card of discard pile remains on the pile
        """
        if len(self.discard_pile) <= 1:
            # Can't replenish if there's only 1 or 0 cards in discard pile
            return
        
        # Keep the top card, shuffle the rest back into deck
        top_card = self.discard_pile[-1]
        self.deck = self.discard_pile[:-1]
        self.discard_pile = [top_card]
        self.np_random.shuffle(self.deck)
    
    def draw_from_deck(self):
        """
        Draw a card from the deck
        
        Returns:
            KadiCard: Card drawn, or None if deck is empty
        """
        if len(self.deck) == 0:
            self.replenish_deck()
        
        if len(self.deck) == 0:
            return None
        
        return self.deck.pop()
    
    def get_deck_size(self):
        """Get number of cards remaining in deck"""
        return len(self.deck)
    
    def add_to_discard_pile(self, card):
        """
        Add a card to the discard pile
        
        Args:
            card (KadiCard): Card to add
        """
        self.discard_pile.append(card)
    
    def get_top_card(self):
        """
        Get the top card of the discard pile
        
        Returns:
            KadiCard: Top card, or None if empty
        """
        return self.discard_pile[-1] if self.discard_pile else None
    
    def get_discard_pile_size(self):
        """Get number of cards in discard pile"""
        return len(self.discard_pile)
    
    def reset(self):
        """Reset dealer for a new game"""
        self.deck = []
        self.discard_pile = []
        self.shuffle_deck()
