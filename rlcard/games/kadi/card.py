"""
Card module for Kadi game
"""

class KadiCard:
    """
    Represents a single card in Kadi game
    
    Card ranks: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
    Card suits: H (Hearts), D (Diamonds), C (Clubs), S (Spades)
    """
    
    def __init__(self, suit, rank):
        """
        Initialize a card
        
        Args:
            suit (str): Card suit (H, D, C, S)
            rank (str): Card rank (A, 2-9, 10, J, Q, K)
        """
        self.suit = suit
        self.rank = rank
    
    def __eq__(self, other):
        if isinstance(other, KadiCard):
            return self.rank == other.rank and self.suit == other.suit
        return NotImplemented
    
    def __hash__(self):
        suits = {'H': 0, 'D': 1, 'C': 2, 'S': 3}
        ranks = {'A': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6,
                 '8': 7, '9': 8, '10': 9, 'J': 10, 'Q': 11, 'K': 12}
        return ranks.get(self.rank, 0) + 100 * suits.get(self.suit, 0)
    
    def __str__(self):
        """Get string representation of card"""
        return f"{self.rank}{self.suit}"
    
    def __repr__(self):
        return self.__str__()
    
    def get_index(self):
        """Get index representation (suit+rank)"""
        return f"{self.suit}{self.rank}"
    
    def get_type(self):
        """
        Get the type of card according to Kadi rules
        
        Returns:
            str: Type of card (jump, question, kickback, answer, penalty)
        """
        # Only ranks determine types
        if self.rank == 'J':
            return 'jump'
        elif self.rank in ['Q', '8']:
            return 'question'
        elif self.rank == 'K':
            return 'kickback'
        elif self.rank in ['2', '3']:
            return 'penalty'
        elif self.rank in ['4', '5', '6', '7', '9', 'A']:
            return 'answer'
        return 'normal'
    
    def get_penalty_value(self):
        """
        Get penalty value for penalty cards
        
        Returns:
            int: Number of cards to draw (2 for '2', 3 for '3')
        """
        if self.rank == '2':
            return 2
        elif self.rank == '3':
            return 3
        
        return 0
    
    def is_valid_start_card(self):
        """
        Check if card can start the discard pile
        
        Returns:
            bool: True if valid start card, False otherwise
        """
        invalid_ranks = ['2', '3', 'J', 'Q', 'K', 'A']
        return self.rank not in invalid_ranks and self.rank != '8'
