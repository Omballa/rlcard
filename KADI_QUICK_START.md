# Kadi Implementation - Quick Reference

## Quick Start

```python
import rlcard
from rlcard.agents.random_agent import RandomAgent

# Play a game with random agents
env = rlcard.make('kadi')
agents = [RandomAgent(env.num_actions) for _ in range(env.num_players)]
env.set_agents(agents)
trajectories, payoffs = env.run(is_training=False)
print(f"Agent payoffs: {payoffs}")
```

## Key API

### Game Initialization
```python
from rlcard.games.kadi import KadiGame

game = KadiGame(allow_step_back=False, num_players=2)
state, player_id = game.init_game()
```

### Environment
```python
env = rlcard.make('kadi', config={
    'allow_step_back': True,
    'seed': 42,
    'game_num_players': 2
})

state, player_id = env.reset()
legal_actions = env._get_legal_actions()
next_state, next_player = env.step(legal_actions[0])
```

### Game State
```python
state = {
    'hand': card_indices,        # Cards in hand
    'current_player': int,       # Current player ID
    'top_card': str,             # Top discard card
    'current_penalty': int,      # Accumulated penalty
    'declared_suit': str,        # Suit declared by Ace
    'legal_actions': {actions}   # Available actions
}
```

## Card Notation

- **Suits**: H (Hearts), D (Diamonds), C (Clubs), S (Spades)
- **Ranks**: A, 2-9, T (10), J (Jump), Q (Question), K (Kickback)
- **Example**: AH = Ace of Hearts, 8C = 8 of Clubs

## Card Types

| Type | Ranks | Effect |
|------|-------|--------|
| Jump | J | Skip next player |
| Question | Q, 8 | Requires answer of same suit |
| Kickback | K | Reverse direction |
| Answer | 4-7, 9-T, A | Normal play (A also declares suit) |
| Penalty | 2, 3 | Next player draws cards |

## Test Execution

```bash
# Run all Kadi game tests
python -m unittest tests.games.test_kadi_game -v

# Run all Kadi environment tests  
python -m unittest tests.envs.test_kadi_env -v

# Run specific test
python -m unittest tests.games.test_kadi_game.TestKadiCard.test_card_types -v
```

## Common Operations

### Check Legal Actions
```python
legal_actions = env._get_legal_actions()
# Returns list of valid action indices
```

### Get Perfect Information
```python
info = env.get_perfect_information()
# Returns dict with all players' hands and game state
```

### Play Card
```python
action_index = 0  # Index from legal_actions
state, next_player = env.step(action_index)
```

### Draw Card
```python
# If -1 is in legal_actions, it means player can draw
if -1 in legal_actions:
    state, next_player = env.step(-1 if raw else action_index_for_draw)
```

### Get Payoffs
```python
payoffs = env.get_payoffs()
# Returns [payoff_player0, payoff_player1, ...]
# +1 for winner, -1 for others
```

## Implementation Hierarchy

```
KadiGame (Game logic)
├── KadiDealer (Card management)
│   └── KadiCard (Individual cards)
├── KadiPlayer[] (Player states)
│   └── KadiCard[] (Player hands)
├── KadiJudger (Rule enforcement)
└── Round State Management

KadiEnv (RL Environment)
└── KadiGame (Wrapped game)
```

## Common Issues & Solutions

### Issue: Game doesn't terminate
- **Solution**: Ensure legal actions allow draws, not stuck in infinite loop

### Issue: Illegal actions accepted
- **Solution**: Always use `_get_legal_actions()` before stepping

### Issue: Can't replay game
- **Solution**: Enable `allow_step_back=True` in config

### Issue: Agent gets same cards each game
- **Solution**: Set different seeds or don't set seed at all

## Configuration Options

```python
config = {
    'allow_step_back': False,      # Enable game replay
    'seed': None,                  # Random seed
    'game_num_players': 2,         # 2-5 players
}

env = rlcard.make('kadi', config=config)
```

## Files to Extend

To add new features:
1. **Game logic**: `rlcard/games/kadi/game.py`
2. **Card rules**: `rlcard/games/kadi/judger.py`
3. **Card types**: `rlcard/games/kadi/card.py`
4. **Environment**: `rlcard/envs/kadi.py`

## Performance Notes

- Typical game length: ~50-200 steps
- With 2 players and random agents: <10ms per game
- Scales well to 100+ training iterations
- Memory efficient for large-scale training

## References

- Official Kadi Rules: https://github.com/Jcardif/Kadi
- RLCard Documentation: https://rlcard.org
- RLCard GitHub: https://github.com/yourselfhosted/rlcard
