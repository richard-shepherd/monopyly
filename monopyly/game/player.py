from .player_state import PlayerState


class Player(object):
    '''
    Holds the PlayerState and a player AI (an object
    derived from PlayerAIBase).
    '''

    def __init__(self):
        self.player_state = PlayerState()
