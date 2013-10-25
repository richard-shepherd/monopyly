
class Card(object):
    '''
    A base class for cards.
    '''

    def play(self, game, current_player):
        '''
        Must be overridden in derived classes.
        '''
        raise Exception("play() not implemented")


