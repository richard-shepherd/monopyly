from .get_out_of_jail_free import GetOutOfJailFree

class Deck(object):
    '''
    A base class for decks of cards.

    There are derived classes for the Chance and Community Chest decks.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cards = []
        self.index = 0

    def take_card(self, game, player):
        '''
        Takes the top card and plays it.

        There is special treatment of the Get Out Of Jail Free card as it
        is taken from the deck and played later.
        '''

        # Are there any cards in the deck?
        number_of_cards = len(self.cards)
        if(number_of_cards == 0):
            return

        # We find the card for the current index...
        card = self.cards[self.index]
        self.index += 1

        # We play the card...
        if(type(card) == GetOutOfJailFree):
            # The card is not Get Out Of Jail Free...
            pass
        else:
            # The card is not Get Out Of Jail Free, so we
            # can play it now...
            pass
