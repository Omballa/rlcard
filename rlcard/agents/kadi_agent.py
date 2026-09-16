import numpy as np


class KadiAgent(object):
    """Random Kadi agent that draws only when no other action is available."""

    def __init__(self, num_actions):
        self.use_raw = False
        self.num_actions = num_actions

    @staticmethod
    def _select_action(state):
        legal_actions = list(state['legal_actions'].keys())
        raw_actions = state.get('raw_legal_actions', [])

        non_draw_actions = [
            action
            for action, raw_action in zip(legal_actions, raw_actions)
            if raw_action != 'DRAW'
        ]
        if non_draw_actions:
            return np.random.choice(non_draw_actions)
        return np.random.choice(legal_actions)

    @staticmethod
    def step(state):
        return KadiAgent._select_action(state)

    def eval_step(self, state):
        action = self._select_action(state)
        legal_actions = list(state['legal_actions'].keys())
        raw_actions = state.get('raw_legal_actions', [])
        playable_actions = [
            legal_action
            for legal_action, raw_action in zip(legal_actions, raw_actions)
            if raw_action != 'DRAW'
        ]
        selected_actions = playable_actions or legal_actions
        probability = 1 / len(selected_actions)
        probs = {
            raw_action: probability if legal_action in selected_actions else 0
            for legal_action, raw_action in zip(legal_actions, raw_actions)
        }
        return action, {'probs': probs}