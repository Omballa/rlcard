# Kadi Game Implementation for RLCard

## Overview

A complete implementation of the Kadi card game for the RLCard reinforcement learning framework. Kadi is a fast-paced Kenyan card game that can be played with 2-5 players using a standard 52-card deck (no jokers).

## Implementation Structure

### Game Core Modules

#### 1. **Card Module** (`rlcard/games/kadi/card.py`)
- `KadiCard` class representing individual cards
- Card types: Jump (J), Question (Q, 8), Kickback (K), Answer (4-7, 9-T, A), Penalty (2, 3)
- Card validation (start card eligibility)
- Penalty value calculation

#### 2. **Player Module** (`rlcard/games/kadi/player.py`)
- `KadiPlayer` class managing player state
- Hand management (add, remove, check cards)
- Matching card detection
- Winning card determination
- Kadi announcement tracking

#### 3. **Dealer Module** (`rlcard/games/kadi/dealer.py`)
- `KadiDealer` class managing deck and discard pile
- 52-card deck creation and shuffling
- Card dealing and drawing
- Deck replenishment from discard pile
- Discard pile management

#### 4. **Judger Module** (`rlcard/games/kadi/judger.py`)
- `KadiJudger` class enforcing game rules
- Legal action determination
- Play validation
- Winning condition checking
- Payoff calculation

#### 5. **Game Module** (`rlcard/games/kadi/game.py`)
- `KadiGame` class orchestrating game flow
- Game initialization
- Turn management and direction handling
- Special card effect handling (Jump, Kickback, Penalty, etc.)
- State management for RL agents
- Step-back functionality for replay

### Environment Integration

- **Kadi Environment** (`rlcard/envs/kadi.py`)
  - RLCard environment wrapper
  - Agent interface compatibility
  - State extraction for learning
  - Perfect information access

- **Registration** (`rlcard/envs/__init__.py`)
  - Game registered as `'kadi'` environment
  - Accessible via `rlcard.make('kadi')`

## Game Rules Implemented

### Card Classification
- **Jump Cards (J)**: Skip the next player
- **Question Cards (Q, 8)**: Require an answer card from the same suit
- **Kickback Cards (K)**: Reverse the direction of play
- **Answer Cards (4-7, 9-T, A)**: Normal playable cards
- **Penalty Cards (2, 3)**: Force next player to draw cards

### Game Flow
1. Shuffle and deal 3-4 cards per player
2. Start with valid card on discard pile
3. Players play cards matching suit or rank
4. Special cards trigger special effects
5. Players can announce "Niko Kadi" when they can win next round
6. First player to empty hand wins (if they announced)

### Legal Actions
- Must match suit or rank of top card
- Can play penalty cards or Aces to counter penalties
- Question cards require answer cards
- Drawing is allowed when no legal plays exist

## Features

### Core Game Logic
- ✅ Multi-player support (2-5 players)
- ✅ All special card effects (Jump, Kickback, Penalties, Questions, Aces)
- ✅ Deck replenishment
- ✅ Direction reversal
- ✅ Penalty accumulation and countering
- ✅ Winning condition validation

### RL Framework Integration
- ✅ State representation for learning
- ✅ Legal action filtering
- ✅ Payoff calculation (zero-sum)
- ✅ Step-back functionality
- ✅ Perfect information access
- ✅ Random seed support

## Usage Examples

### Create and Play Game
```python
import rlcard
from rlcard.agents.random_agent import RandomAgent

# Create environment
env = rlcard.make('kadi')

# Set up random agents
agents = [RandomAgent(env.num_actions) for _ in range(env.num_players)]
env.set_agents(agents)

# Run a complete game
trajectories, payoffs = env.run(is_training=False)
print(f"Game results: {payoffs}")
```

### Access Game State
```python
env = rlcard.make('kadi')
state, player_id = env.reset()

# Get legal actions
legal_actions = env._get_legal_actions()

# Take action
action = legal_actions[0]
next_state, next_player = env.step(action)

# Get perfect information
info = env.get_perfect_information()
print(f"Top card: {info['top_card']}")
print(f"Current player: {info['current_player']}")
```

### Train Agents
```python
env = rlcard.make('kadi')
agents = [MyAgent(env.num_actions) for _ in range(env.num_players)]
env.set_agents(agents)

# Training loop
for i in range(1000):
    trajectories, payoffs = env.run(is_training=True)
    # Update agents based on trajectories and payoffs
```

## Test Coverage

### Unit Tests (`tests/games/test_kadi_game.py`)
- **Card Tests**: 7 tests
  - Card creation, equality, string representation
  - Card type classification
  - Penalty values
  - Valid start cards

- **Player Tests**: 6 tests
  - Player initialization
  - Hand management
  - Card matching
  - Answer cards
  - Winning cards

- **Dealer Tests**: 5 tests
  - Deck creation and shuffling
  - Card dealing
  - Discard pile management
  - Deck replenishment

- **Game Tests**: 11 tests
  - Game initialization
  - Player configuration
  - Legal actions
  - State format
  - Payoffs
  - Step-back functionality
  - Multiple steps

- **Integration Tests**: 3 tests
  - Full game simulation
  - Multi-player games
  - Deck consistency

**Total: 31 game tests - ALL PASSING ✅**

### Environment Tests (`tests/envs/test_kadi_env.py`)
- **Environment Tests**: 12 tests
  - Environment creation
  - Reset and state extraction
  - Step and legal actions
  - Step-back functionality
  - Perfect information

- **Integration Tests**: 1 test
  - Basic game flow

**Total: 13 environment tests - ALL PASSING ✅**

## Test Results

```
Game Tests: 31 passed in 0.211s ✅
Environment Tests: 13 passed in 0.051s ✅
Total: 44 tests passed ✅
```

## Key Implementation Details

### State Representation
```python
{
    'hand': [card indices],
    'num_players': int,
    'current_player': int,
    'direction': int (1 or -1),
    'top_card': str,
    'discard_pile_size': int,
    'deck_size': int,
    'other_players_hands': [hand sizes],
    'declared_suit': str or None,
    'current_penalty': int,
    'kadi_announced': bool,
    'can_win_next_round': bool,
    'legal_actions': {action_indices}
}
```

### Action Encoding
- Actions 0-53: Play card at that index in hand
- Action 54 (special -1): Draw from deck
- Legal actions are filtered by game rules

### Payoffs
- Winner: +1
- Other players: -1
- Zero-sum game for competitive learning

## Files Created

```
rlcard/games/kadi/
├── __init__.py           (Module exports)
├── card.py               (Card class)
├── player.py             (Player class)
├── dealer.py             (Dealer class)
├── judger.py             (Judger class)
└── game.py               (Main game logic)

rlcard/envs/
└── kadi.py               (Environment wrapper)

tests/
├── games/test_kadi_game.py   (Game unit tests)
└── envs/test_kadi_env.py     (Environment tests)
```

## Future Enhancements

Possible improvements for more advanced features:
1. Simulation of "Niko Kadi" announcement and winning conditions
2. Advanced rule variations
3. Statistical analysis of game outcomes
4. Bot strategy optimization
5. Web-based UI for visualization

## Notes

- The implementation follows RLCard's architecture and conventions
- All game rules from the official Kadi rules are implemented
- The code is optimized for reinforcement learning training
- Full test coverage ensures reliability
- Compatible with RLCard's agent framework

## Author

Implemented based on Kadi game rules from: https://github.com/Jcardif/Kadi
