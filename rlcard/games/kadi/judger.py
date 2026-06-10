"""
Judger module for Kadi game - handles rules and legal actions
"""


class KadiJudger:
    """
    Judges valid moves and determines game state in Kadi
    """
    
    def __init__(self, np_random):
        """
        Initialize the judger
        
        Args:
            np_random: NumPy random state
        """
        self.np_random = np_random
    
    def get_legal_actions(self, player, top_card, declared_suit=None, current_penalty=0):
        """
        Get legal actions for a player
        
        Args:
            player (KadiPlayer): Player whose actions to evaluate
            top_card (KadiCard): Current top card on discard pile
            declared_suit (str): Suit declared by Ace playing (if any)
            current_penalty (int): Current accumulated penalty value
            
        Returns:
            list: List of legal card indices in player's hand
        """
        legal_actions = []
        
        suit_to_match = declared_suit or top_card.suit
        top_rank = top_card.rank
        top_suit = top_card.suit
        
        # If there's a penalty, only specific cards can be played to counter it
        if current_penalty > 0:
            # Can play penalty cards to forward the penalty
            for i, card in enumerate(player.hand):
                if card.rank in ['2', '3']:
                    legal_actions.append(i)
            
            # Can play Ace to escape penalty (continues with its suit)
            for i, card in enumerate(player.hand):
                if card.rank == 'A':
                    legal_actions.append(i)
            
            # If no penalty cards or Aces, must draw
            # if not legal_actions:
            #     legal_actions.append(-1)  # Special code for "draw"
            
            # Always append draw as a legal action. Player can choose to draw even if they have legal plays (strategic choice).
            legal_actions.append(-1)  # Special code for "draw"
            
            return legal_actions
        
        # Normal play: match suit or rank
        for i, card in enumerate(player.hand):
            if card.rank == top_rank or card.suit == suit_to_match:
                legal_actions.append(i)
        
        # If playing a Question card, must have an answer card available
        if top_rank in ['Q', '8']:
            filtered_actions = []
            for action in legal_actions:
                card = player.hand[action]
                if card.rank in ['Q', '8']:
                    # Check if player has answer card of same suit
                    has_answer = any(
                        c.rank in ['4', '5', '6', '7', '9', '10', 'A'] and c.suit == card.suit
                        for c in player.hand
                    )
                    if has_answer:
                        filtered_actions.append(action)
                else:
                    filtered_actions.append(action)
            legal_actions = filtered_actions
        
        # # If no legal play, player must draw
        # if not legal_actions:
        #     legal_actions.append(-1)  # Special code for "draw"

        # Always append draw as a legal action. Player can choose to draw even if they have legal plays (strategic choice).
        legal_actions.append(-1)  # Special code for "draw"
        
        return legal_actions
    
    def is_valid_play(self, card, top_card, declared_suit=None, current_penalty=0):
        """
        Check if a card play is valid
        
        Args:
            card (KadiCard): Card being played
            top_card (KadiCard): Top card on discard pile
            declared_suit (str): Suit declared by Ace (if any)
            current_penalty (int): Current penalty value
            
        Returns:
            bool: True if play is valid
        """
        suit_to_match = declared_suit or top_card.suit
        
        # If there's penalty, can only play penalty cards or Ace
        if current_penalty > 0:
            return card.rank in ['2', '3'] or card.rank == 'A'
        
        # Otherwise, must match suit or rank
        return card.rank == top_card.rank or card.suit == suit_to_match
    
    def can_win_with_cards(self, player):
        """
        Check if player can win in current state
        
        Winning cards are answer cards and questions with matching answers
        
        Args:
            player (KadiPlayer): Player to check
            
        Returns:
            bool: True if player has only winning cards left
        """
        if len(player.hand) == 0:
            return False
        
        winning_cards = player.get_winning_cards()
        
        # Check if all remaining cards are winning cards
        return len(winning_cards) == len(player.hand)
    
    def get_playable_cards_for_question(self, player, question_card):
        """
        Get valid answer cards for a question card
        
        Args:
            player (KadiPlayer): Player who played the question
            question_card (KadiCard): The question card played
            
        Returns:
            list: Indices of valid answer cards in player's hand
        """
        valid_answers = []
        answer_ranks = ['4', '5', '6', '7', '9', '10', 'A']
        
        for i, card in enumerate(player.hand):
            if card.rank in answer_ranks and card.suit == question_card.suit:
                valid_answers.append(i)
        
        return valid_answers
    
    @staticmethod
    def get_payoffs(players):
        """
        Calculate payoffs for all players
        
        Args:
            players (list): List of all players
            
        Returns:
            list: Payoff for each player (1 for winner, -1 for others)
        """
        payoffs = []
        
        # Find winner (player with kadi_announced and can_win_next_round who wins)
        for player in players:
            if player.status == 'cardless':
                payoffs.append(1)
            else:
                payoffs.append(-1)
        
        return payoffs
