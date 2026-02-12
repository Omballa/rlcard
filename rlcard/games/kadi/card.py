from termcolor import colored

class KadiCard:

    info = {'type':  ['number', 'special', 'penalty', 'joker'],
            'color': ['h', 'd', 'c', 's'],
            'trait': ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10'
                      'J', 'Q', 'K', 'JOK']
            }

    def __init__(self, suit, rank):
        """
        Initialize a KadiCard.
        
        Args:
            suit (str): 'h', 'd', 's', or 'c'
            rank (str): 'A', '2', '10', 'J', 'Q', 'K', or 'JOK'
        """

        # if suit not in self.info['suit'] and rank != 'JOK':
        #     raise ValueError(f"Invalid suit: {suit}")
        # if rank not in self.info['rank']:
        #     raise ValueError(f"Invalid rank: {rank}")
        
        self.suit = suit
        self.rank = rank
        self.str = self.get_str()

    def get_str(self):
        """
        Get the string representation of the card.
        
        Returns:
            str: e.g. 'h-A', 'd-K', 'JOK', 'draw'
        """
        
        return f"{self.suit}-{self.rank}"


    @staticmethod
    def print_cards(cards, show_suit_for_special=False):
        """
        Print cards in a colorful, readable way (similar to Uno version).
        
        Args:
            cards (str or list[str]): Card string(s) like 'h-A', 's-J', 'JOK', 'draw'
            show_suit_for_special (bool): If True, colorize J/Q/K even if special
        """

        if isinstance(cards, str):
            cards = [cards]
        for i, card_str in enumerate(cards):
            if card_str == 'draw':
                display = colored('DRAW', 'white', attrs=['bold'])
            elif card_str == 'JOK':
                display = colored('JOKER', 'magenta', attrs=['bold'])
            else:
                suit, rank = card_str.split('-')
                
                # Map rank to display name
                if rank == 'J':
                    name = 'JUMP'
                elif rank == 'Q':
                    name = 'QUESTION'
                elif rank == 'K':
                    name = 'KICKBACK'
                elif rank == '8':
                    name = 'QUESTION'  # 8 is also a Question card
                elif rank == 'A':
                    name = 'ACE'
                elif rank == '10':
                    name = '10'
                else:
                    name = rank  # 2–9 as-is

                # Color based on suit (standard playing card colors)
                if suit == 'h':
                    color = 'red'
                elif suit == 'd':
                    color = 'red'      # Diamonds usually red
                elif suit == 's':
                    color = 'blue'     # or 'grey'/'black' — using blue for visibility
                elif suit == 'c':
                    color = 'green'    # or 'black' — using green for contrast
                
                # Special handling: always show suit color for these?
                if show_suit_for_special or rank in ['2','3','4','5','6','7','9','10','A']:
                    display = colored(name, color)
                else:
                    # For J/Q/K/8/JOK — neutral or bold without suit color
                    display = colored(name, 'white', attrs=['bold'])

            print(display, end='')
            if i < len(cards) - 1:
                print(', ', end='')
        print()  # New line at end