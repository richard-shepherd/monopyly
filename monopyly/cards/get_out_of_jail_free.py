from .card import Card


class GetOutOfJailFree(Card):
    '''
    Get Out Of Jail Free.
    '''
    def __init__(self, deck=None):
        '''
        The constructor.
        '''
        # The deck that the card belongs to.
        # We hold this so that we can put the card back in the deck
        # after it has been played.
        self.deck = deck

    def put_back_in_deck(self):
        '''
        Puts the card back in the deck.

        The mechanics of getting out of jail are handled by other code
        (in the Game class), so all we need to do here is to put the card
        back in the deck.
        '''
        if(self.deck):
            self.deck.cards.append(self)


