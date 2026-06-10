#!/usr/bin/env python3
"""Human vs Random runner for Kadi

Place this in `examples/human/kadi_human.py` and run it to play as Player 0.
"""
import rlcard
import numpy as np


def print_state(state):
    print('\nTop card:', state.get('top_card'))
    print('Your hand:')
    for i, c in enumerate(state['hand']):
        print(f"  [{i}] {c}")
    print("Other players' hand sizes:", state.get('other_players_hands'))
    print('Current penalty:', state.get('current_penalty'))


def main():
    env = rlcard.make('kadi', config={'game_num_players': 2})
    print('Kadi human vs random (you are Player 0)')
    state, player = env.reset()

    while not env.game.is_over():
        if player == 0:
            # Human turn
            
            state = env.get_state(0)
            legal = env._get_legal_actions()
            print_state(state)

            # Show legal choices
            print('\nLegal choices:')
            for i, a in enumerate(legal):
                if a == -1:
                    print(f"  [{i}] DRAW")
                else:
                    # protect against stale indices
                    card_str = state['hand'][a] if a < len(state['hand']) and a >= 0 else str(a)
                    print(f"  [{i}] Play card index {a} -> {card_str}")

            choice = input('Choose option index (q to quit): ')
            if choice.lower().startswith('q'):
                break
            try:
                choice = int(choice)
            except Exception:
                print('Invalid input, try again.')
                continue
            if choice < 0 or choice >= len(legal):
                print('Choice out of range, try again.')
                continue
            raw_action = legal[choice]
            state, player = env.step(raw_action, raw_action=True)
        
        else:
            # Random opponent
            # get current state for the opponent so we can show the played card
            state_before = env.get_state(player)
            legal = env._get_legal_actions()
            raw_action = int(np.random.choice(legal))
            state, player = env.step(raw_action, raw_action=True)
        

    print('\nGame over. Payoffs:', env.get_payoffs())


if __name__ == '__main__':
    main()
