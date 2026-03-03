from rlcard.games.kadi.card import KadiCard


class HumanAgent(object):
    ''' A human agent for Kadi. It can be used to play against trained models
    '''

    def __init__(self, num_actions):
        ''' Initialize the human agent

        Args:
            num_actions (int): the size of the output action space
        '''
        self.use_raw = True
        self.num_actions = num_actions

    @staticmethod
    def step(state):
        ''' Human agent will display the state and make decisions through interfaces

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human (raw action string)
        '''
        _print_state(state['raw_obs'], state['action_record'])
        action = int(input('>> You choose action (integer): '))
        while action < 0 or action >= len(state['legal_actions']):
            print('Action illegal...')
            action = int(input('>> Re-choose action (integer): '))
        return state['raw_legal_actions'][action]

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation. The same as step here.

        Args:
            state (dict): a dictionary that represents the current state

        Returns:
            action (int): the action predicted by the human agent
        '''
        return self.step(state), {}


def _print_state(state, action_record):
    ''' Print out the state of the current player in a readable way

    Args:
        state (dict): raw state from the environment
        action_record (list): list of historical (player_id, action) pairs
    '''
    _action_list = []
    for i in range(1, len(action_record) + 1):
        if action_record[-i][0] == state['current_player']:
            break
        _action_list.insert(0, action_record[-i])

    for pair in _action_list:
        print('>> Player', pair[0], 'chooses ', end='')
        KadiCard.print_cards(pair[1])
        print('')

    print('\n=============== Your Hand ===============')
    KadiCard.print_cards(state['hand'], show_suit_for_special=True)
    print('')

    print('=============== Top Card ===============')
    KadiCard.print_cards(state['target'])
    print('')

    print('========== Players Card Number ==========')
    for i in range(state['num_players']):
        if i != state['current_player']:
            print('Player {} has {} cards.'.format(i, state['num_cards'][i]))

    # Optional: show some Kadi-specific status info
    if state.get('pending_penalty', 0) > 0:
        print('Pending penalty to resolve:', state['pending_penalty'])
    if state.get('pending_question_suit', None):
        print('Pending question suit:', state['pending_question_suit'])

    print('======== Actions You Can Choose =========')
    for i, action in enumerate(state['legal_actions']):
        print(str(i) + ': ', end='')
        KadiCard.print_cards(action)
        if i < len(state['legal_actions']) - 1:
            print(', ', end='')
    print('\n')
