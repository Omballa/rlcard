"""
Unit tests for Kadi card game
"""

import unittest
import numpy as np

from rlcard.games.kadi import KadiGame, KadiPlayer, KadiDealer, KadiCard


class TestKadiCard(unittest.TestCase):
    """Test Kadi card functionality"""
    
    def test_card_creation(self):
        """Test creating cards"""
        card = KadiCard('H', 'A')
        self.assertEqual(card.suit, 'H')
        self.assertEqual(card.rank, 'A')
    
    def test_card_equality(self):
        """Test card equality"""
        card1 = KadiCard('H', 'A')
        card2 = KadiCard('H', 'A')
        card3 = KadiCard('D', 'A')
        
        self.assertEqual(card1, card2)
        self.assertNotEqual(card1, card3)
    
    def test_card_string_representation(self):
        """Test card string representation"""
        card = KadiCard('H', 'A')
        self.assertEqual(str(card), 'AH')
        self.assertEqual(card.get_index(), 'HA')
    
    def test_card_types(self):
        """Test card type classification"""
        tests = [
            (KadiCard('H', 'J'), 'jump'),
            (KadiCard('H', 'Q'), 'question'),
            (KadiCard('H', 'K'), 'kickback'),
            (KadiCard('H', 'A'), 'answer'),
            (KadiCard('H', '4'), 'answer'),
            (KadiCard('H', '2'), 'penalty'),
            (KadiCard('H', '3'), 'penalty'),
        ]
        
        for card, expected_type in tests:
            self.assertEqual(card.get_type(), expected_type, 
                           f"Card {card} should be type {expected_type}")
    
    def test_penalty_values(self):
        """Test penalty card values"""
        self.assertEqual(KadiCard('H', '2').get_penalty_value(), 2)
        self.assertEqual(KadiCard('H', '3').get_penalty_value(), 3)
    
    def test_valid_start_cards(self):
        """Test which cards can start discard pile"""
        valid_cards = [
            KadiCard('H', '4'), KadiCard('H', '5'), KadiCard('H', '6'),
            KadiCard('H', '7'), KadiCard('H', '9'), KadiCard('H', 'T'),
        ]
        
        invalid_cards = [
            KadiCard('H', '2'), KadiCard('H', '3'), KadiCard('H', 'J'),
            KadiCard('H', 'Q'), KadiCard('H', 'K'), KadiCard('H', 'A'),
            KadiCard('H', '8'),
        ]
        
        for card in valid_cards:
            self.assertTrue(card.is_valid_start_card(), 
                          f"Card {card} should be valid start card")
        
        for card in invalid_cards:
            self.assertFalse(card.is_valid_start_card(),
                           f"Card {card} should not be valid start card")


class TestKadiPlayer(unittest.TestCase):
    """Test Kadi player functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.player = KadiPlayer(0, np.random.RandomState(42))
    
    def test_player_initialization(self):
        """Test player initialization"""
        self.assertEqual(self.player.player_id, 0)
        self.assertEqual(len(self.player.hand), 0)
        self.assertEqual(self.player.status, 'alive')
    
    def test_add_remove_cards(self):
        """Test adding and removing cards"""
        card1 = KadiCard('H', 'A')
        card2 = KadiCard('D', 'K')
        
        self.player.add_card(card1)
        self.assertEqual(self.player.get_hand_size(), 1)
        self.assertTrue(self.player.has_card(card1))
        
        self.player.add_card(card2)
        self.assertEqual(self.player.get_hand_size(), 2)
        
        self.assertTrue(self.player.remove_card(card1))
        self.assertEqual(self.player.get_hand_size(), 1)
        self.assertFalse(self.player.has_card(card1))
    
    def test_get_cards_by_rank(self):
        """Test getting cards by rank"""
        self.player.add_card(KadiCard('H', 'A'))
        self.player.add_card(KadiCard('D', 'A'))
        self.player.add_card(KadiCard('C', 'K'))
        
        aces = self.player.get_cards_of_rank('A')
        self.assertEqual(len(aces), 2)
        
        kings = self.player.get_cards_of_rank('K')
        self.assertEqual(len(kings), 1)
    
    def test_has_matching_card(self):
        """Test matching card detection"""
        self.player.add_card(KadiCard('H', '5'))
        self.player.add_card(KadiCard('D', 'K'))
        
        top_card = KadiCard('H', '3')
        self.assertTrue(self.player.has_matching_card(top_card))
        
        top_card = KadiCard('C', '3')
        self.assertFalse(self.player.has_matching_card(top_card))
    
    def test_has_answer_card(self):
        """Test answer card detection"""
        self.player.add_card(KadiCard('H', 'Q'))
        self.assertFalse(self.player.has_answer_card())
        
        self.player.add_card(KadiCard('D', '5'))
        self.assertTrue(self.player.has_answer_card())
    
    def test_winning_cards(self):
        """Test winning card detection"""
        # Add only answer cards
        self.player.add_card(KadiCard('H', '4'))
        self.player.add_card(KadiCard('D', '5'))
        
        winning = self.player.get_winning_cards()
        self.assertEqual(len(winning), 2)
        
        # Add question without answer
        self.player.add_card(KadiCard('C', 'Q'))
        winning = self.player.get_winning_cards()
        self.assertEqual(len(winning), 2)  # Question without answer doesn't count
        
        # Add matching answer
        self.player.add_card(KadiCard('C', '6'))
        winning = self.player.get_winning_cards()
        self.assertEqual(len(winning), 4)  # All cards now


class TestKadiDealer(unittest.TestCase):
    """Test Kadi dealer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dealer = KadiDealer(np.random.RandomState(42))
    
    def test_deck_creation(self):
        """Test deck is created with correct cards"""
        self.assertEqual(len(self.dealer.deck), 52)
    
    def test_deal_cards(self):
        """Test dealing cards"""
        player = KadiPlayer(0, np.random.RandomState(42))
        
        self.dealer.deal_card(player)
        self.assertEqual(player.get_hand_size(), 1)
        
        self.dealer.deal_cards(player, 3)
        self.assertEqual(player.get_hand_size(), 4)
    
    def test_discard_pile(self):
        """Test discard pile operations"""
        card = KadiCard('H', '5')
        self.dealer.add_to_discard_pile(card)
        
        self.assertEqual(self.dealer.get_discard_pile_size(), 1)
        self.assertEqual(self.dealer.get_top_card(), card)
    
    def test_replenish_deck(self):
        """Test deck replenishment"""
        # Empty deck and add cards to discard pile
        self.dealer.deck = []
        
        top_card = KadiCard('H', '5')
        other_card = KadiCard('D', 'K')
        
        self.dealer.discard_pile = [other_card, top_card]
        
        self.dealer.replenish_deck()
        
        # Top card should still be on discard pile
        self.assertEqual(self.dealer.get_top_card(), top_card)
        # Other card should be back in deck
        self.assertIn(other_card, self.dealer.deck)
    
    def test_draw_from_deck(self):
        """Test drawing from deck"""
        initial_size = len(self.dealer.deck)
        card = self.dealer.draw_from_deck()
        
        self.assertIsNotNone(card)
        self.assertEqual(len(self.dealer.deck), initial_size - 1)


class TestKadiGame(unittest.TestCase):
    """Test Kadi game logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = KadiGame(num_players=2)
    
    def test_game_initialization(self):
        """Test game initialization"""
        state, player_id = self.game.init_game()
        
        self.assertEqual(self.game.num_players, 2)
        self.assertEqual(len(self.game.players), 2)
        self.assertIn('hand', state)
        self.assertIn('current_player', state)
        self.assertGreaterEqual(len(self.game.players[0].hand), 3)
    
    def test_num_players_configuration(self):
        """Test player count limits"""
        game = KadiGame(num_players=1)
        self.assertEqual(game.num_players, 2)  # Minimum 2
        
        game = KadiGame(num_players=6)
        self.assertEqual(game.num_players, 5)  # Maximum 5
        
        game = KadiGame(num_players=3)
        self.assertEqual(game.num_players, 3)
    
    def test_valid_start_card(self):
        """Test that discard pile starts with valid card"""
        self.game.init_game()
        top_card = self.game.dealer.get_top_card()
        
        self.assertTrue(top_card.is_valid_start_card(),
                       f"Top card {top_card} should be valid start card")
    
    def test_get_legal_actions(self):
        """Test getting legal actions"""
        self.game.init_game()
        legal_actions = self.game.get_legal_actions()
        
        # Should be a list
        self.assertIsInstance(legal_actions, list)
        # Should have at least draw option
        self.assertGreater(len(legal_actions), 0)
    
    def test_get_num_players(self):
        """Test getting number of players"""
        self.assertEqual(self.game.get_num_players(), 2)
    
    def test_get_num_actions(self):
        """Test getting total number of actions"""
        # 52 cards + 1 draw
        self.assertEqual(self.game.get_num_actions(), 53)
    
    def test_step_draw(self):
        """Test drawing a card"""
        self.game.init_game()
        player_id = self.game.current_player
        initial_hand_size = self.game.players[player_id].get_hand_size()
        
        # Draw a card
        state, next_player = self.game.step(-1)
        
        # Hand should have one more card
        self.assertEqual(self.game.players[player_id].get_hand_size(), 
                        initial_hand_size + 1)
    
    def test_game_state_format(self):
        """Test game state has correct format"""
        self.game.init_game()
        state = self.game.get_state(0)
        
        required_keys = ['hand', 'num_players', 'current_player', 'top_card', 
                        'deck_size', 'other_players_hands', 'kadi_announced']
        
        for key in required_keys:
            self.assertIn(key, state, f"State missing key: {key}")
    
    def test_payoffs(self):
        """Test payoff calculation"""
        self.game.init_game()
        payoffs = self.game.get_payoffs()
        
        self.assertEqual(len(payoffs), self.game.num_players)
        for payoff in payoffs:
            self.assertEqual(payoff, 0)  # No one has won yet
    
    def test_step_back(self):
        """Test stepping back in game"""
        self.game.init_game()
        initial_state = self.game.get_state(self.game.current_player)
        
        # Can't step back if allow_step_back is False
        game = KadiGame(allow_step_back=False)
        game.init_game()
        game.step(-1)
        self.assertFalse(game.step_back())
        
        # Can step back if allow_step_back is True
        game = KadiGame(allow_step_back=True)
        game.init_game()
        current_player = game.current_player
        game.step(-1)
        game.step_back()
        self.assertEqual(game.current_player, current_player)
    
    def test_multiple_steps(self):
        """Test multiple game steps"""
        self.game.init_game()
        
        for _ in range(10):
            legal_actions = self.game.get_legal_actions()
            if legal_actions:
                action = legal_actions[0]
                state, player_id = self.game.step(action)
                
                self.assertIn('current_player', state)
                self.assertGreaterEqual(player_id, 0)
                self.assertLess(player_id, self.game.num_players)


class TestKadiIntegration(unittest.TestCase):
    """Integration tests for Kadi game"""
    
    def test_full_game_with_random_moves(self):
        """Test a full game with random valid moves"""
        game = KadiGame(num_players=2, allow_step_back=False)
        game.init_game()
        
        steps = 0
        max_steps = 2000  # Increased to allow for longer games
        
        while not game.is_over and steps < max_steps:
            legal_actions = game.get_legal_actions()
            if not legal_actions:
                break
            
            action = legal_actions[np.random.randint(0, len(legal_actions))]
            state, player_id = game.step(action)
            steps += 1
        
        # Game should terminate (either win or timeout)
        self.assertLessEqual(steps, max_steps)
    
    def test_game_with_3_players(self):
        """Test game with 3 players"""
        game = KadiGame(num_players=3)
        state, player_id = game.init_game()
        
        self.assertEqual(game.num_players, 3)
        self.assertIn(player_id, range(3))
    
    def test_deck_consistency(self):
        """Test that deck is properly managed"""
        game = KadiGame(num_players=2)
        game.init_game()
        
        initial_total = (len(game.dealer.deck) + 
                        len(game.dealer.discard_pile) +
                        sum(len(p.hand) for p in game.players))
        
        # Should be 52 cards total
        self.assertEqual(initial_total, 52)


if __name__ == '__main__':
    unittest.main()
