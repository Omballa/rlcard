import unittest

from rlcard.agents.kadi_agent import KadiAgent


class TestKadiAgent(unittest.TestCase):

    def test_draw_is_not_selected_when_play_is_available(self):
        state = {
            'legal_actions': {10: None, 20: None},
            'raw_legal_actions': ['H4', 'DRAW'],
        }

        self.assertEqual(KadiAgent.step(state), 10)

    def test_draw_is_selected_when_it_is_the_only_action(self):
        state = {
            'legal_actions': {20: None},
            'raw_legal_actions': ['DRAW'],
        }

        self.assertEqual(KadiAgent.step(state), 20)


if __name__ == '__main__':
    unittest.main()