from rlcard.games.kadi.card import KadiCard
from rlcard.games.kadi.utils import cards2list


class KadiRound:

    def __init__(self, dealer, num_players, np_random):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        self.np_random = np_random
        self.dealer = dealer
        self.target = None
        self.current_player = 0
        self.num_players = num_players
        self.direction = 1
        self.played_cards = []
        self.is_over = False
        self.winner = None
        self.pending_penalty = 0            # Accumulates draw cards from chain (2/3/Joker)
        self.pending_question_suit = None   # If Question (Q/8) active, forces same-suit Answer

    def flip_top_card(self):
        ''' Flip the top card of the card pile

        Returns:
            (object of KadiCard): the top card in game

        '''
        top = self.dealer.flip_top_card()
        self.target = top
        self.played_cards.append(top)
        return top

    def perform_top_card(self, players, top_card):
        ''' Perform the top card

        Args:
            players (list): list of KadiPlayer objects
            top_card (object): object of KadiCard
        '''

        rank = top_card.rank
        next_player_idx = (self.current_player + self.direction) % self.num_players
        
        if rank in ['2', '3', 'JOK']:
            penalty = {'2': 2, '3': 3, 'JOK': 5}.get(rank, 0)
            self.dealer.deal_cards(players[next_player_idx], penalty)
            self.current_player = next_player_idx  # Skip penalized player? Variants differ

        elif rank == 'J':
            self.current_player = (next_player_idx + self.direction) % self.num_players  # Skip next

        elif rank == 'K':
            self.direction *= -1
            self.current_player = (self.current_player + self.direction) % self.num_players

        elif rank in ['Q', '8']:
            self.pending_question_suit = top_card.suit  # Next must match suit or draw

        # No effect for number/A

    def proceed_round(self, players, action):
        ''' Call other Classes' functions to keep one round running

        Args:
            player (object): object of UnoPlayer
            action (str): string of legal action
        '''

        
        if action == 'draw':
            self._perform_draw_action(players)
            return None
        
        if action == "pass":
            return None
        
        player = players[self.current_player]
        card = self._find_and_remove_card(player, action)

        if not card:
            raise ValueError(f"Illegal action: {action}")

        self.played_cards.append(card)
        self.target = card

        # Check win (after full chain/turn)
        if len(player.hand) == 0:
            if not player.niko_kadi_declared:  # Must have announced previous turn
                # Optional: check final card was Answer (4-7,9,10,A) — variant-dependent
                self.is_over = True
                self.winner = [self.current_player]
            else:
                # Penalty for invalid win attempt (e.g. draw 2–4 cards)
                self.dealer.deal_cards(player, 4, self)
                player.niko_kadi_declared = False

        # Reset pending if countered
        self.pending_penalty = 0
        self.pending_question_suit = None

        # Apply effects
        self._apply_card_effect(players, card)

    
    def _find_and_remove_card(self, player, action_str):
        """Find card in hand by str ('h-A', 'JOK') and remove it."""
        for i, card in enumerate(player.hand):
            if card.str == action_str:
                return player.hand.pop(i)
        return None
    
    def _apply_card_effect(self, players, card):
        """Apply special card effects; may allow chaining (re-call proceed_round)."""
        rank = card.rank
        next_idx = (self.current_player + self.direction) % self.num_players

        if rank in ['2', '3', 'JOK']:
            penalty = {'2': 2, '3': 3, 'JOK': 5}.get(rank, 0)
            self.pending_penalty += penalty
            # Chain: next player can counter with same-rank penalty or draw
            self.current_player = next_idx  # Stay on next for possible counter

        elif rank == 'J':
            # Jump: skip next
            self.current_player = (next_idx + self.direction) % self.num_players

        elif rank == 'K':
            self.direction *= -1
            self.current_player = (self.current_player + self.direction) % self.num_players

        elif rank in ['Q', '8']:
            self.pending_question_suit = card.suit
            # self.current_player = next_idx  # Next must answer same suit

        elif rank == 'A':
            # Ace: player declares new suit (handled in action? or sub-action)
            # For simplicity: assume action includes suit, or keep current
            self.current_player = next_idx

        else:
            # Normal number card
            self.current_player = next_idx

    def get_legal_actions(self, players, player_id):
        """
        Return list of playable action strings for player_id.
        """
        player = players[player_id]
        hand = player.hand
        legal = []

        target_suit = self.target.suit if self.target else None
        target_rank = self.target.rank if self.target else None
        
        # Case 1: There is an active penalty → can only counter or draw
        if self.pending_penalty > 0:
            for card in hand:
                if card.rank in ['2', '3', 'JOK'] and card.rank == target_rank:
                    legal.append(card.str)
                    

            if not legal:
                legal = ['draw']

        # Case 2: Question is pending → must play same-suit Answer or draw
        elif self.pending_question_suit:
            answer_ranks = {'4', '5', '6', '7', '9', '10'}  # adjust per your rules
            for card in hand:
                if card.suit == self.pending_question_suit and card.rank in answer_ranks:
                    legal.append(card.str)

            if not legal:
                legal = ['draw']

        # Case 3: Normal turn → match suit/rank or play Joker
        else:
            for card in hand:
                if (card.suit == target_suit or
                    card.rank == target_rank or
                    card.rank == 'JOK' or
                    target_rank == 'JOK'):

                    legal.append(card.str)

            if not legal:
                legal = ['draw']

        # ─────────────── Add this block here ───────────────
        # (initialize on first call)
        self.last_logged_player = getattr(self, 'last_logged_player', -1)
        self.last_logged_state_hash = getattr(self, 'last_logged_state_hash', '')

        # unique key for current state
        state_key = f"{player_id}-{self.pending_penalty}-{self.pending_question_suit}-{self.target.str if self.target else 'None'}"

        # Only print if player or state changed
        if state_key != self.last_logged_state_hash or player_id != self.last_logged_player:
            if(len(hand) < 10):
                print(f"[LEGAL] Player {player_id} | hand: {cards2list(hand)} cards | top: {self.target.str if self.target else 'None'}")
                print(f"[LEGAL] pending_penalty={self.pending_penalty}, question_suit={self.pending_question_suit}")
                print(f"[LEGAL] Final legal actions: {legal}")

            # remember for next time
            self.last_logged_player = player_id
            self.last_logged_state_hash = state_key

        # ─────────────── always return the list ───────────────z
        return legal
    
    def get_state(self, players, player_id):
        ''' Get player's state

        Args:
            players (list): The list of UnoPlayer
            player_id (int): The id of the player
        '''
        state = {}
        player = players[player_id]
        state['hand'] = cards2list(player.hand)
        state['target'] = self.target.str
        state['played_cards'] = cards2list(self.played_cards)
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        state['num_cards'] = [len(p.hand) for p in players]
        state['pending_penalty'] = self.pending_penalty
        state['pending_question_suit'] = self.pending_question_suit
        state['niko_kadi_status'] = [p.niko_kadi_declared for p in players]
        
        return state

    def replace_deck(self):
        ''' Add cards have been played to deck
        '''

        if not self.played_cards:
            # print("[RESHUFFLE] No played cards available → cannot reshuffle")
            return

        if len(self.played_cards) == 1:
            # print("[RESHUFFLE] Only top card left — cannot reshuffle")
            return

        # print(f"[RESHUFFLE] Deck empty. Moving {len(self.played_cards)-1} cards back to deck (keeping top)")
        
        # Keep the current top card
        current_top = self.played_cards[-1]

        # Move all other played cards to deck
        self.dealer.deck.extend(self.played_cards[:-1])
        self.dealer.shuffle()

        # Restore only the top card
        self.played_cards = [current_top]

        # print(f"[RESHUFFLE] New deck size: {len(self.dealer.deck)} | top remains: {current_top.str}")

    def _perform_draw_action(self, players):
        # replace deck if there is no card in draw pile
        if not self.dealer.deck:
            self.replace_deck()
            # if not self.dealer.deck:
                # print("[DRAW] Still no cards after reshuffle — game may be stuck")
            #self.is_over = True
            #self.winner = UnoJudger.judge_winner(players)
            #return None

        draw_count = max(1, self.pending_penalty)
        for _ in range(draw_count):
            if self.dealer.deck:
                card = self.dealer.deck.pop()
                players[self.current_player].hand.append(card)

        self.pending_penalty = 0
        self.pending_question_suit = None
        self.current_player = (self.current_player + self.direction) % self.num_players
