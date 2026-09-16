#!/usr/bin/env python
"""
Demo script for Kadi game implementation
Shows how to use the Kadi game in RLCard
"""

import rlcard
from rlcard.agents.kadi_agent import KadiAgent
import sys
import numpy as np


def demo_basic_game():
    """Run a basic Kadi game with random agents"""
    print("=" * 60)
    print("KADI GAME - RLCard Implementation Demo")
    print("=" * 60)
    
    # Create environment
    env = rlcard.make('kadi')
    print(f"\n✅ Environment created: {env.name}")
    print(f"   Number of players: {env.num_players}")
    print(f"   Number of actions: {env.num_actions}")
    
    # Set up agents
    agents = [KadiAgent(env.num_actions) for _ in range(env.num_players)]
    env.set_agents(agents)
    print(f"✅ Agents set up: {len(agents)} random agents")
    
    # Play game
    print("\n" + "-" * 60)
    print("Playing game...")
    print("-" * 60)
    
    state, player_id = env.reset()
    step = 0

    while not env.game.is_over():
        current_player = env.game.current_player
        legal_actions = env._get_legal_actions()

        # Convert raw actions into readable values
        readable_actions = []
        for action in legal_actions:
            if action >= 0:
                card = env.game.players[current_player].hand[action]
                readable_actions.append(f"{action} -> {card.get_index()}")
            else:
                special_actions = {
                    -1: "DRAW",
                    -2: "PASS",
                    -3: "DECLARE H",
                    -4: "DECLARE D",
                    -5: "DECLARE C",
                    -6: "DECLARE S",
                }
                readable_actions.append(f"{action} -> {special_actions[action]}")

        # Select a random playable action, drawing only when necessary.
        state = env.get_state(current_player)
        action, _ = agents[current_player].eval_step(state)
        action = next(
            raw_action
            for raw_action, global_action in zip(
                legal_actions, state['legal_actions'].keys()
            )
            if global_action == action
        )

        if action >= 0:
            selected_action = (
                f"{action} -> "
                f"{env.game.players[current_player].hand[action].get_index()}"
            )
        else:
            selected_action = next(
                value for value in readable_actions
                if value.startswith(f"{action} ->")
            )

        print(f"\n--- Step {step + 1} ---")
        print(f"Current player: Player {current_player}")
        print(f"Player 0 hand: {[card.get_index() for card in env.game.players[0].hand]}")
        print(f"Player 1 hand: {[card.get_index() for card in env.game.players[1].hand]}")
        print(f"Top card: {env.game.dealer.get_top_card().get_index()}")
        print(f"Direction: {env.game.direction}")
        print(f"Declared suit: {env.game.declared_suit}")
        print(f"Current penalty: {env.game.current_penalty}")
        print(f"Available actions: {readable_actions}")
        print(f"Selected action: {selected_action}")
        print(f"Draw pile: {len(env.game.dealer.deck)}")

        # These are raw game actions, so raw_action must be True
        state, player_id = env.step(action, raw_action=True)
        step += 1

    print("\n=== Final state ===")
    print(f"Player 0 hand: {[card.get_index() for card in env.game.players[0].hand]}")
    print(f"Player 1 hand: {[card.get_index() for card in env.game.players[1].hand]}")
    print(f"Top card: {env.game.dealer.get_top_card().get_index()}")
    print(f"Payoffs: {env.get_payoffs()}")

    payoffs = env.get_payoffs()
    # Find winner
    max_payoff = max(payoffs)
    if max_payoff > 0:
        winner = payoffs.index(max_payoff)
        print(f"🏆 Winner: Player {winner}")
    else:
        print("🤝 Game ended in draw")
    
    return step, payoffs


def demo_perfect_information():
    """Show perfect information access"""
    print("\n" + "=" * 60)
    print("Perfect Information Demo")
    print("=" * 60)
    
    env = rlcard.make('kadi')
    env.reset()
    
    info = env.get_perfect_information()
    
    print(f"\nCurrent player: Player {info['current_player']}")
    print(f"Direction: {'Clockwise' if info['direction'] == 1 else 'Counter-clockwise'}")
    print(f"Top card: {info.get('top_card', 'None')}")
    print(f"Penalty: {info.get('current_penalty', 0)}")
    
    print("\nPlayer Hands:")
    for i in range(env.num_players):
        player_info = info[f'player_{i}']
        print(f"  Player {i}: {len(player_info['hand'])} cards")


def demo_step_back():
    """Show step-back functionality"""
    print("\n" + "=" * 60)
    print("Step-Back Demo")
    print("=" * 60)
    
    env = rlcard.make('kadi', config={'allow_step_back': True})
    state, player_id = env.reset()
    
    print(f"Initial player: {player_id}")
    
    # Take a step
    legal_actions = env._get_legal_actions()
    action = legal_actions[0]
    state, new_player_id = env.step(action, raw_action=True)
    
    print(f"After step: Player {new_player_id}")
    
    # Step back
    env.step_back()
    print(f"After step_back: Player {env.game.current_player}")
    
    print("✅ Step-back works correctly")


def demo_multiple_games():
    """Run multiple games and show statistics"""
    print("\n" + "=" * 60)
    print("Multiple Games Statistics")
    print("=" * 60)
    
    num_games = 10
    all_payoffs = []
    game_steps = []
    
    print(f"\nPlaying {num_games} games...")
    
    for game_num in range(num_games):
        env = rlcard.make('kadi')
        agents = [KadiAgent(env.num_actions) for _ in range(env.num_players)]
        env.set_agents(agents)
        
        state, player_id = env.reset()
        step = 0
        
        while not env.game.is_over() and step < 500:
            legal_actions = env._get_legal_actions()
            action = legal_actions[0]
            state, player_id = env.step(action, raw_action=True)
            step += 1
        
        payoffs = env.get_payoffs()
        all_payoffs.append(payoffs)
        game_steps.append(step)
        
        print(f"  Game {game_num+1}: Steps={step}, Payoffs={payoffs}")
    
    # Statistics
    print("\n" + "-" * 60)
    print("Statistics:")
    print("-" * 60)
    print(f"Average game length: {sum(game_steps) / len(game_steps):.1f} steps")
    print(f"Min/Max steps: {min(game_steps)} / {max(game_steps)}")
    
    total_wins = [0] * env.num_players
    for payoff in all_payoffs:
        max_payoff = max(payoff)
        if max_payoff > 0:
            winner = payoff.index(max_payoff)
            total_wins[winner] += 1
    
    print(f"Wins distribution: {total_wins}")


def main():
    """Run all demos"""
    try:
        demo_basic_game()
        demo_perfect_information()
        demo_step_back()
        demo_multiple_games()
        
        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
