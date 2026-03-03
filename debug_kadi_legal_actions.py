import argparse
import numpy as np

from rlcard.games.kadi.card import KadiCard
from rlcard.games.kadi.dealer import KadiDealer
from rlcard.games.kadi.player import KadiPlayer
from rlcard.games.kadi.round import KadiRound
from rlcard.games.kadi.utils import cards2list


def str_to_kadi_card(card_str: str) -> KadiCard:
    """Convert 'h-A' style string into a KadiCard."""
    if card_str.upper() == "JOK":
        # For tests, require explicit suit, e.g. 'h-JOK' or 's-JOK'
        raise ValueError(
            "Use explicit suit for Joker, e.g. 'h-JOK' or 's-JOK', not bare 'JOK'"
        )
    suit, rank = card_str.split("-")
    return KadiCard(suit, rank)


def run_scenario(
    target: str,
    hand: list[str],
    pending_penalty: int = 0,
    pending_question_suit: str | None = None,
    requested_suit: str | None = None,
    chain_counter: int = 1,
    player_id: int = 0,
) -> list[str]:
    """
    Build a minimal KadiRound + players with a chosen top card and hand,
    then return the generated legal actions for inspection.
    """
    np_random = np.random.RandomState(42)

    dealer = KadiDealer(np_random)
    num_players = 2
    round_ = KadiRound(dealer, num_players, np_random)

    # Set top card / target
    top_card = str_to_kadi_card(target)
    round_.target = top_card
    round_.played_cards = [top_card]

    # Create players and assign hand to the tested player
    players = [KadiPlayer(i, np_random) for i in range(num_players)]
    players[player_id].hand = [str_to_kadi_card(c) for c in hand]

    # Configure round state
    round_.current_player = player_id
    round_.pending_penalty = pending_penalty
    round_.pending_question_suit = pending_question_suit
    round_.requested_suit = requested_suit
    round_.chain_counter = chain_counter

    legal = round_.get_legal_actions(players, player_id)

    print("==========================================")
    print(f"Top card: {target}")
    print(f"Player {player_id} hand: {cards2list(players[player_id].hand)}")
    print(
        f"State: pending_penalty={pending_penalty}, "
        f"pending_question_suit={pending_question_suit}, "
        f"requested_suit={requested_suit}, chain_counter={chain_counter}"
    )
    print("Legal actions:")
    for i, action in enumerate(legal):
        print(f"  {i}: {action}")

    return legal


def main():
    parser = argparse.ArgumentParser(
        description="Debug helper for Kadi legal_actions generation."
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Top card, e.g. 'h-A', 'd-3', 's-JOK'",
    )
    parser.add_argument(
        "--hand",
        type=str,
        nargs="+",
        required=True,
        help="Player hand cards, e.g. 'h-2 d-3 c-A'",
    )
    parser.add_argument(
        "--pending_penalty",
        type=int,
        default=0,
        help="Current pending penalty (0 if none).",
    )
    parser.add_argument(
        "--pending_question_suit",
        type=str,
        default=None,
        help="Pending question suit (e.g. 'h', 'd', 's', 'c') or None.",
    )
    parser.add_argument(
        "--requested_suit",
        type=str,
        default=None,
        help="Requested suit after Ace (e.g. 'h', 'd', 's', 'c') or None.",
    )
    parser.add_argument(
        "--chain_counter",
        type=int,
        default=1,
        help="Current chain counter (1 for normal play).",
    )
    parser.add_argument(
        "--player_id",
        type=int,
        default=0,
        help="Player index to test (default: 0).",
    )

    args = parser.parse_args()

    # Normalize string "None" to actual None for convenience
    pqs = None if args.pending_question_suit in (None, "None") else args.pending_question_suit
    rs = None if args.requested_suit in (None, "None") else args.requested_suit

    run_scenario(
        target=args.target,
        hand=args.hand,
        pending_penalty=args.pending_penalty,
        pending_question_suit=pqs,
        requested_suit=rs,
        chain_counter=args.chain_counter,
        player_id=args.player_id,
    )


if __name__ == "__main__":
    main()

