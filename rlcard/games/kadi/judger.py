
class KadiJudger:

    @staticmethod
    def judge_winner(players, np_random):
        ''' Judge the winner of the game

        Args:
            players (list): The list of players who play the game

        Returns:
            (list): The player id of the winner
        '''

        for i, player in enumerate(players):
            if len(player.hand) == 0:
                return i
                
