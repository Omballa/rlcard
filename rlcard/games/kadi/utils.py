import os
import json
import numpy as np
from collections import OrderedDict

import rlcard

from rlcard.games.kadi.card import KadiCard as Card

# Kadi suits and ranks
SUITS = ['H', 'D', 'C', 'S']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

# a map of abstract action to its index and a list of abstract action
# Load action space from provided json so indexes match environment
ROOT_PATH = rlcard.__path__[0]
with open(os.path.join(ROOT_PATH, 'games/kadi/jsondata/action_space.json'), 'r') as f:
    ACTION_SPACE = json.load(f, object_pairs_hook=OrderedDict)
ACTION_LIST = list(ACTION_SPACE.keys())

# a map of suit to its index
SUIT_MAP = {s: i for i, s in enumerate(SUITS)}

# a map of rank to its index
VALUE_MAP = {r: i for i, r in enumerate(RANKS)}

WILD = []


def get_action_space():
    """Return the action space mapping (string -> index)."""
    return ACTION_SPACE


def get_action_list():
    """Return the ordered list of action keys."""
    return ACTION_LIST


def card_str_to_index(card_str):
    """Map a card string like 'H4' or special string to global index.

    Returns None if not found.
    """
    if card_str is None:
        return None
    # Accept 'DRAW'/'PASS' and suit letters
    if isinstance(card_str, str):
        if card_str in ACTION_SPACE:
            return ACTION_SPACE[card_str]
        # Support friendly names
        if card_str == 'DRAW':
            return ACTION_SPACE.get('-1')
        if card_str == 'PASS':
            return ACTION_SPACE.get('-2')
        if card_str in SUIT_MAP:
            # map 'H' -> '-3'.. etc
            suit_to_neg = {'H': '-3', 'D': '-4', 'C': '-5', 'S': '-6'}
            return ACTION_SPACE.get(suit_to_neg[card_str])
    return None


def negative_code_to_index(code):
    """Map a negative game code (-1..-6) to global action index."""
    return ACTION_SPACE.get(str(code))


def index_to_action(index):
    """Map a global action index to a readable action.

    Returns card string like 'H4' or 'DRAW'/'PASS' or suit letter for declarations.
    """
    if index is None:
        return None
    try:
        key = ACTION_LIST[index]
    except Exception:
        return None
    # negative keys like '-1' map to friendly names
    if key.startswith('-'):
        if key == '-1':
            return 'DRAW'
        if key == '-2':
            return 'PASS'
        if key == '-3':
            return 'H'
        if key == '-4':
            return 'D'
        if key == '-5':
            return 'C'
        if key == '-6':
            return 'S'
    return key


def global_index_to_card(index):
    """Return card string for a 0..51 index, or None for special indices."""
    if index is None:
        return None
    try:
        key = ACTION_LIST[index]
    except Exception:
        return None
    if key.startswith('-'):
        return None
    return key



def init_deck():
    ''' Generate kadi deck of 52 cards
    '''
    deck = []
    for s in SUITS:
        for r in RANKS:
            deck.append(Card(s, r))
    return deck


def cards2list(cards):
    ''' Get the corresponding string representation of cards

    Args:
        cards (list): list of KadiCard objects or strings

    Returns:
        (list): list of string representations like 'H4' or 'D10'
    '''
    cards_list = []
    for card in cards:
        if hasattr(card, 'get_index'):
            cards_list.append(card.get_index())
        else:
            cards_list.append(str(card))
    return cards_list

def hand2dict(hand):
    ''' Get the corresponding dict representation of hand

    Args:
        hand (list): list of string of hand's card

    Returns:
        (dict): dict of hand
    '''
    hand_dict = {}
    for card in hand:
        # accept Card objects or string representations
        if hasattr(card, 'get_index'):
            key = card.get_index()
        else:
            key = card
        if key not in hand_dict:
            hand_dict[key] = 1
        else:
            hand_dict[key] += 1
    return hand_dict

def encode_hand(plane, hand):
    ''' Encode hand and represerve it into plane

    Args:
        plane (array): 3*4*13 numpy array
        hand (list): list of string of hand's card

    Returns:
        (array): 3*4*13 numpy array
    '''
    # plane expected shape (3, 4, 13)
    plane[0] = np.ones((4, 13), dtype=int)
    hand = hand2dict(hand)
    for card, count in hand.items():
        # card string like 'H4' or 'D10'
        if len(card) < 2:
            continue
        suit = card[0]
        rank = card[1:]
        if suit not in SUIT_MAP or rank not in VALUE_MAP:
            continue
        color = SUIT_MAP[suit]
        trait = VALUE_MAP[rank]
        plane[0][color][trait] = 0
        # cap counts to plane available indices (0,1,2)
        count_index = min(count, 2)
        plane[count_index][color][trait] = 1
    return plane

def encode_target(plane, target):
    ''' Encode target and represerve it into plane

    Args:
        plane (array): 1*4*13 numpy array
        target(str): string of target card

    Returns:
        (array): 1*4*13 numpy array
    '''
    if target is None:
        return plane
    suit = target[0]
    rank = target[1:]
    if suit not in SUIT_MAP or rank not in VALUE_MAP:
        return plane
    color = SUIT_MAP[suit]
    trait = VALUE_MAP[rank]
    plane[color][trait] = 1
    return plane
