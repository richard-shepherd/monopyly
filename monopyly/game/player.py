from .player_state import PlayerState


class Player(object):
    '''
    Holds the PlayerState and a player AI (an object
    derived from PlayerAIBase).
    '''

    def __init__(self, player_ai):
        '''
        The 'constructor'.
        '''
        self.player_state = PlayerState()
        self.player_ai = player_ai
