"""
Environment tests for Kadi game
"""

import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent


class TestKadiEnv(unittest.TestCase):
    """Test Kadi environment"""
    
    def test_environment_creation(self):
        """Test environment can be created"""
        env = rlcard.make('kadi')
        self.assertIsNotNone(env)
    
    def test_reset(self):
        """Test environment reset"""
        env = rlcard.make('kadi')
        state, player_id = env.reset()
        
        self.assertIsNotNone(state)
        self.assertGreaterEqual(player_id, 0)
        self.assertLess(player_id, env.num_players)
    
    def test_state_structure(self):
        """Test state has correct structure"""
        env = rlcard.make('kadi')
        state, _ = env.reset()
        
        required_keys = ['hand', 'num_players', 'current_player', 'top_card']
        for key in required_keys:
            self.assertIn(key, state, f"State missing key: {key}")
    
    def test_step(self):
        """Test environment step"""
        env = rlcard.make('kadi')
        env.reset()
        
        legal_actions = env._get_legal_actions()
        self.assertGreater(len(legal_actions), 0)
        
        action = legal_actions[0]
        state, player_id = env.step(action)
        
        self.assertIsNotNone(state)
        self.assertGreaterEqual(player_id, 0)
        self.assertLess(player_id, env.num_players)
    
    def test_get_legal_actions(self):
        """Test getting legal actions"""
        env = rlcard.make('kadi')
        env.reset()
        
        legal_actions = env._get_legal_actions()
        self.assertIsInstance(legal_actions, list)
        self.assertGreater(len(legal_actions), 0)
    
    def test_multiple_steps(self):
        """Test multiple sequential steps"""
        env = rlcard.make('kadi')
        env.reset()
        
        for _ in range(20):
            legal_actions = env._get_legal_actions()
            if not legal_actions:
                break
            
            action = legal_actions[np.random.randint(0, len(legal_actions))]
            state, player_id = env.step(action)
            
            self.assertGreaterEqual(player_id, 0)
            self.assertLess(player_id, env.num_players)
    
    def test_get_perfect_information(self):
        """Test getting perfect information"""
        env = rlcard.make('kadi')
        env.reset()
        
        info = env.get_perfect_information()
        
        # Should have info for all players
        for i in range(env.num_players):
            self.assertIn(f'player_{i}', info)
        
        # Should have top card
        self.assertIn('top_card', info)
    
    def test_with_random_agents(self):
        """Test environment with random agents - basic check"""
        env = rlcard.make('kadi')
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        
        # Just verify we can call it without errors
        self.assertIsNotNone(env.agents)
    
    def test_step_back_enabled(self):
        """Test step_back when enabled"""
        env = rlcard.make('kadi', config={'allow_step_back': True})
        env.reset()
        
        legal_actions = env._get_legal_actions()
        action = legal_actions[0]
        
        player_before = env.game.current_player
        env.step(action)
        
        # Step back should work
        self.assertTrue(env.step_back())
        self.assertEqual(env.game.current_player, player_before)
    
    def test_step_back_disabled(self):
        """Test step_back when disabled"""
        env = rlcard.make('kadi', config={'allow_step_back': False})
        env.reset()
        
        legal_actions = env._get_legal_actions()
        action = legal_actions[0]
        env.step(action)
        
        # Step back should raise an exception
        with self.assertRaises(Exception):
            env.step_back()
    
    def test_num_players_configuration(self):
        """Test configuring different number of players"""
        # Test default 2 players
        env = rlcard.make('kadi')
        self.assertEqual(env.num_players, 2)
    
    def test_seed_reproducibility(self):
        """Test that seeds work for reproducibility"""
        # Just verify seed method exists and doesn't crash
        env = rlcard.make('kadi')
        env.seed(42)
        state, _ = env.reset()
        self.assertIsNotNone(state)


class TestKadiEnvIntegration(unittest.TestCase):
    """Integration tests for Kadi environment"""
    
    def test_game_not_broken(self):
        """Test that basic game flow works"""
        env = rlcard.make('kadi')
        state, player_id = env.reset()
        
        # Do a few steps
        for _ in range(5):
            legal_actions = env._get_legal_actions()
            if not legal_actions:
                break
            
            action = legal_actions[0]
            state, player_id = env.step(action)
        
        # Verify we can get payoffs
        payoffs = env.get_payoffs()
        self.assertEqual(len(payoffs), env.num_players)


if __name__ == '__main__':
    unittest.main()
