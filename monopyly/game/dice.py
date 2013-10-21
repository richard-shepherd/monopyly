import random


class Dice(object):
    '''
    Generates random numbers by rolling two 'dice'.

    The reason for this class existing is so that it can be
    mocked and replaced with a deterministic version for
    testing.
    '''

    def roll(self):
        '''
        Returns two value: the rolls of the two dice.
        '''
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        return roll1, roll2
