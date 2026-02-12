import os
import json
import numpy as np
from collections import OrderedDict

import rlcard

from rlcard.games.kadi.card import KadiCard as Card

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of abstract action to its index and a list of abstract action
with open(os.path.join(ROOT_PATH, 'games/kadi/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())

# a map of color to its index
SUIT_MAP = {'h': 0, 'd': 1, 's': 2, 'c': 3}

# Rank to column index (0-13; pad 14 if needed)
RANK_MAP = {
    'A': 0,
    '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8, '10': 9,
    'J': 10,   # Jump
    'Q': 11,   # Question
    'K': 12,   # Kickback
    'JOK': 13  # Joker (penalty)
}

# Special rank groups (used in Round/Game logic)
PENALTY_RANKS = {'2', '3', 'JOK'}          # 2→draw 2, 3→draw 3, JOK→draw 5
QUESTION_RANKS = {'Q', '8'}                # Force same-suit Answer
ANSWER_RANKS = {'A', '4', '5', '6', '7', '9', '10'}  # Allowed for winning / answering
KICKBACK_RANK = 'K'
JUMP_RANK = 'J'

def init_deck():
    ''' Generate a standard Kadi deck: 52 suited cards + 2 identical Jokers
    '''
    deck = []
    suits = ['h', 'd', 's', 'c']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    for suit in suits:
        for rank in ranks:
            deck.append(Card(suit, rank))

    # Add two identical Jokers 
    deck.append(Card('h', 'JOK'))
    deck.append(Card('s', 'JOK'))

    return deck


def cards2list(cards):
    ''' Get the corresponding string representation of cards

    Args:
        cards (list): list of UnoCards objects

    Returns:
        (string): string representation of cards
    '''
    return [card.str for card in cards]

def hand2dict(hand):
    ''' Get the corresponding dict representation of hand

    Args:
        hand (list): list of string of hand's card

    Returns:
        (dict): dict of hand
    '''
    hand_dict = {}
    for card in hand:
        hand_dict[card] = hand_dict.get(card, 0) + 1
    
    return hand_dict

def encode_hand(plane, hand):
    ''' Encode hand and represerve it into plane

    Args:
        plane (array): 3*4*15 numpy array
        hand (list): list of string of hand's card

    Returns:
        (array): 3*4*15 numpy array
    '''
    # plane = np.zeros((3, 4, 15), dtype=int)
    plane[0] = np.ones((4, 15), dtype=int)
    hand_dict = hand2dict(hand)

    for card_str, count in hand_dict.items():
        if card_str == 'JOK':
            # Joker: no suit → set across all suits in plane[1]
            if plane[1][0][13] == 0:  # Only set once
                for s in range(4):
                    plane[0][s][13] = 0
                    plane[1][s][13] = 1  # At least one Joker
                    if count >= 2:
                        plane[2][s][13] = 1
        else:
            suit, rank = card_str.split('-')
            if suit not in SUIT_MAP or rank not in RANK_MAP:
                continue
            s_idx = SUIT_MAP[suit]
            r_idx = RANK_MAP[rank]

            plane[0][s_idx][r_idx] = 0  # Clear presence
            plane[1][s_idx][r_idx] = 1  # At least 1
            if count >= 2:
                plane[2][s_idx][r_idx] = 1  # At least 2

    return plane

def encode_target(plane, target):
    ''' Encode target and represerve it into plane

    Args:
        plane (array): 1*4*15 numpy array
        target(str): string of target card

    Returns:
        (array): 1*4*15 numpy array
    '''
    if target == 'JOK':
        # Joker: mark all suits or use a convention (e.g. suit 0)
        plane[0][13] = 1
    else:
        suit, rank = target.split('-')
        if suit in SUIT_MAP and rank in RANK_MAP:
            plane[SUIT_MAP[suit]][RANK_MAP[rank]] = 1

    return plane