"""
Player module for Kadi game
"""


class KadiPlayer:
    """
    Represents a player in Kadi game
    """
    
    def __init__(self, player_id, np_random):
        """
        Initialize a Kadi player
        
        Args:
            player_id (int): Player's ID
            np_random: NumPy random state for reproducibility
        """
        self.player_id = player_id
        self.np_random = np_random
        self.hand = []
        self.status = 'alive'  # 'alive' or 'cardless' (if hand is empty)
        self.kadi_announced = False  # Whether player announced "Niko Kadi"
        self.can_win_next_round = False
    
    def get_player_id(self):
        """Get player's ID"""
        return self.player_id
    
    def add_card(self, card):
        """
        Add a card to player's hand
        
        Args:
            card (KadiCard): Card to add
        """
        self.hand.append(card)
    
    def remove_card(self, card):
        """
        Remove a card from player's hand
        
        Args:
            card (KadiCard): Card to remove
            
        Returns:
            bool: True if card was removed, False if not found
        """
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False
    
    def get_hand_size(self):
        """Get number of cards in hand"""
        return len(self.hand)
    
    def has_card(self, card):
        """Check if player has a specific card"""
        return card in self.hand
    
    def get_cards_of_rank(self, rank):
        """Get all cards of a specific rank"""
        return [card for card in self.hand if card.rank == rank]
    
    def get_cards_of_suit(self, suit):
        """Get all cards of a specific suit"""
        return [card for card in self.hand if card.suit == suit]
    
    def has_matching_card(self, top_card, declared_suit=None):
        """
        Check if player has a card matching the top card
        
        Args:
            top_card (KadiCard): Card on top of discard pile
            declared_suit (str): If Ace was played, the declared suit
            
        Returns:
            bool: True if player has matching card
        """
        suit_to_match = declared_suit or top_card.suit
        
        for card in self.hand:
            if card.rank == top_card.rank or card.suit == suit_to_match:
                return True
        return False
    
    def has_answer_card(self, rank=None):
        """
        Check if player has an answer card
        
        Args:
            rank (str): If specified, check for answer card matching this rank
            
        Returns:
            bool: True if player has an answer card
        """
        answer_ranks = ['4', '5', '6', '7', '9', 'T', 'A']
        
        for card in self.hand:
            if card.rank in answer_ranks:
                if rank is None or card.rank == rank:
                    return True
        return False
    
    def get_winning_cards(self):
        """
        Get winning cards from hand
        
        Returns:
            list: Cards that contribute to winning (answer cards and questions with answer pairs)
        """
        # Answer cards: 4, 5, 6, 7, 9, 10, A
        answer_ranks = ['4', '5', '6', '7', '9', 'T', 'A']
        question_ranks = ['Q', '8']
        
        winning_cards = []
        used_cards = set()
        
        # Only standalone answer cards and questions with matching answer cards count
        for card in self.hand:
            if card in used_cards:
                continue
                
            if card.rank in answer_ranks:
                # Answer cards count as winning
                winning_cards.append(card)
                used_cards.add(card)
            elif card.rank in question_ranks:
                # Question cards only count if they have a matching answer
                for answer_card in self.hand:
                    if (answer_card not in used_cards and 
                        answer_card.rank in answer_ranks and 
                        answer_card.suit == card.suit):
                        winning_cards.append(card)
                        winning_cards.append(answer_card)
                        used_cards.add(card)
                        used_cards.add(answer_card)
                        break
        
        return winning_cards
    
    def reset(self):
        """Reset player for a new game"""
        self.hand = []
        self.status = 'alive'
        self.kadi_announced = False
        self.can_win_next_round = False
