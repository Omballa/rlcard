import os

import torch

import rlcard

from rlcard.utils import get_device, set_seed
from rlcard.agents import KadiHumanAgent as HumanAgent
from rlcard.agents import NFSPAgent
from rlcard.games.kadi.card import KadiCard


MODEL_DIR = "experiments/kadi_nfsp_result"
CHECKPOINT_PATH = os.path.join(MODEL_DIR, "checkpoint_nfsp.pt")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pth")



def load_trained_agent(device):
    """Load the trained NFSP agent from experiments/kadi_nfsp_result."""
    if os.path.exists(CHECKPOINT_PATH):
        from rlcard.agents import NFSPAgent

        # PyTorch 2.6 defaults to weights_only=True, but this checkpoint
        # contains a full object graph (including custom classes), so we
        # must explicitly set weights_only=False to load it.
        checkpoint = torch.load(
            CHECKPOINT_PATH,
            map_location=device,
            weights_only=False,
        )
        agent = NFSPAgent.from_checkpoint(checkpoint)
    elif os.path.exists(MODEL_PATH):
        # Fallback to full model object
        agent = torch.load(
            MODEL_PATH,
            map_location=device,
            weights_only=False,
        )
    else:
        raise FileNotFoundError(
            f"Could not find trained model in {MODEL_DIR} "
            f"(expected {CHECKPOINT_PATH} or {MODEL_PATH})"
        )

    # Ensure the agent runs on the chosen device
    if hasattr(agent, "set_device"):
        agent.set_device(device)

    return agent


def play_one_game(env):
    """Play one full Kadi game with step-by-step logging, including AI turns."""
    # Start a fresh game
    state, player_id = env.reset()

    # Loop until the game is over
    while not env.is_over():
        agent = env.agents[player_id]

        # Human turn
        if isinstance(agent, HumanAgent):
            action, _ = agent.eval_step(state)
        else:
            # AI turn – choose action and show it (with full hand for debugging)
            raw = state.get('raw_obs', {})
            ai_hand = raw.get('hand', [])
            ai_choices = raw.get('legal_actions', [])
            print(f"\nAI Player {player_id} hand before action: ", end="")
            if ai_hand:
                KadiCard.print_cards(ai_hand, show_suit_for_special=True)
                print(f"AI Player {player_id} choices: ", end="")
                KadiCard.print_cards(ai_choices, show_suit_for_special=True)
            else:
                print("(empty)")

            action, _ = agent.eval_step(state)

        # Step environment (handles raw vs encoded by agent.use_raw)
        next_state, next_player_id = env.step(action, agent.use_raw)

        # Log what just happened using the recorded raw action
        last_player, last_action = env.action_recorder[-1]
        if isinstance(agent, HumanAgent):
            # Human actions are already shown in HumanAgent UI; skip duplicate log
            pass
        else:
            print(f"\nAI Player {last_player} plays: ", end="")
            KadiCard.print_cards(last_action)

        state, player_id = next_state, next_player_id

    # Game finished
    payoffs = env.get_payoffs()
    print("Game over. Payoffs:", payoffs)


def main():
    device = get_device()
    set_seed(42)

    env = rlcard.make(
        "kadi",
        config={
            "game_num_players": 2,
            "allow_step_back": False,
            "seed": 42,
        },
    )

    nfsp_agent = load_trained_agent(device)
    human = HumanAgent(env.num_actions)

    # Seat human as player 0, NFSP as opponent
    env.set_agents([human, nfsp_agent])

    print("You are player 0. Type action indices when prompted.")

    while True:
        play_one_game(env)

        again = input("Play another game? (y/n): ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    main()
