from .player_state import PlayerState


class Player(object):
    '''
    Holds the PlayerState and a player AI (an object
    derived from PlayerAIBase).
    '''

    def __init__(self, ai, number):
        '''
        The 'constructor'.
        '''
        self.state = PlayerState()
        self.ai = ai
        self.number = number
