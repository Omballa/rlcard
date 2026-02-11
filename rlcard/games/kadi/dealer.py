
from rlcard.games.kadi.utils import init_deck


class KadiDealer:
    """
    Initialize a Kadi dealer class.
    Manages the deck, shuffling, dealing, and initial top card setup.
    """
    def __init__(self, np_random):
        self.np_random = np_random
        self.deck = init_deck()
        self.shuffle()

    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, player, num, round):
        ''' Deal some cards from deck to one player

        Args:
            player (object): The object of DoudizhuPlayer
            num (int): The number of cards to be dealed
        '''
        for _ in range(num):
            if self.deck:  # Safety check
                player.hand.append(self.deck.pop())
            else:
                round.replace_deck()


    def flip_top_card(self):
        """
        Flip the top card to start the discard pile when a new game begins.
        In Kadi, certain cards are invalid as starting card (especially penalties/specials).

        Returns:
            KadiCard: The valid top card object placed face up
        """
        if not self.deck:
            raise ValueError("Deck is empty - cannot flip top card")

        top_card = self.deck.pop()
        
        # Common Kadi rule: Do NOT start with a penalty/special card that affects play immediately
        # Invalid starting cards typically include:
        #   - 2 or 3 (penalty/draw cards)
        #   - Joker (draw/penalty)
        #   - J (Jump/Skip)
        #   - K (Kickback/Reverse)
        #   - Sometimes Q or 8 (Question) — varies by house rules

        invalid_ranks = {'2', '3', 'J', 'K', 'JOK'}  # Adjust based on your exact ruleset

        while top_card.rank in invalid_ranks:
            # Put it back, reshuffle, try again
            self.deck.append(top_card)
            self.shuffle()
            top_card = self.deck.pop()

        return top_card
