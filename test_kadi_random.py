import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_seed

print("Script started")
# Optional: set seed for reproducibility
set_seed(42)

# Create environment
env = rlcard.make('kadi', config={
    'game_num_players': 2,
    'allow_step_back': False,   # usually False for random play
    'seed': 42,
})

print("Environment created successfully")
print("Num actions:", env.num_actions)  # should be 54

# Create two random agents
agent1 = RandomAgent(num_actions=env.num_actions)
agent2 = RandomAgent(num_actions=env.num_actions)

# Set agents (index 0 = first player, index 1 = second)
env.set_agents([agent1, agent2])

print("Agents set. Starting episode...")

# Run multiple episodes with logging
num_episodes = 20

for episode in range(1, num_episodes + 1):
    print(f"Starting episode {episode}")
    trajectories, payoffs = env.run(is_training=False)
    print(f"Episode {episode} finished | Payoffs: {payoffs}")
    
    # Optional: show final hands and winner
    winner_ids = [i for i, p in enumerate(payoffs) if p > 0]
    if winner_ids:
        print(f"Winner(s): Player {winner_ids}")
    else:
        print("Draw / no winner")
    
    # Print final hands (very useful for debugging)
    for i in range(env.num_players):
        try:
            # Try to get the last transition for this player
            last_trans = trajectories[i][-1] if isinstance(trajectories[i], list) and trajectories[i] else None
            
            if isinstance(last_trans, dict) and 'raw_obs' in last_trans:
                hand_list = last_trans['raw_obs'].get('hand', [])
            else:
                hand_list = []  # fallback
                
            hand_str = ", ".join(hand_list) if hand_list else "empty"
            count = len(hand_list)
            print(f"  Player {i} final hand ({count} cards): {hand_str}")
            
        except (IndexError, TypeError, KeyError) as e:
            print(f"  Player {i} final hand: (could not extract - {str(e)})")

print("All episodes completed")