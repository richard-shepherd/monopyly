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

        # We play the card...
        if(type(card) == GetOutOfJailFree):
            # The card is Get Out Of Jail Free.
            # We give it to the player...
            player.state.number_of_get_out_of_jail_free_cards += 1
            player.ai.got_get_out_of_jail_free_card()

            # And remove it from the deck...
            del self.cards[self.index]
        else:
            # The card is not Get Out Of Jail Free, so we can play it now...
            card.play(game, player)

            # We 'put the card to the bottom of the deck'...
            self.index += 1
            if(self.index >= number_of_cards):
                self.index = 0
