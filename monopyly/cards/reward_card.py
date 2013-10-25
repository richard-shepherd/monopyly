from .card import Card


class RewardCard(Card):
    '''
    Manages cards that reward the player who picks them up.
    For example: Bank pays you a dividend of £50.
    '''
    def __init__(self, reward):
        '''
        The 'constructor'
        '''
        self.reward = reward

    def play(self, game, current_player):
        '''
        Gives the reward to the player.
        '''
        game.give_money_to_player(current_player, self.reward)


