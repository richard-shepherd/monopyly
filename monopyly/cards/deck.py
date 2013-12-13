from .get_out_of_jail_free import GetOutOfJailFree
import random


class Deck(object):
    '''
    A base class for decks of cards.

    There are derived classes for the Chance and Community Chest decks.

    Note that cards are taken randomly from the decks, rather than by
    shuffling to begin with and then cycling through the cards. This helps
    prevent players from "peeking" at the cards.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cards = []

    def take_card(self, game, player):
        '''
        Takes a random card and plays it.

        There is special treatment of the Get Out Of Jail Free card as it
        is taken from the deck and played later.
        '''

        # Are there any cards in the deck?
        number_of_cards = len(self.cards)
        if number_of_cards == 0:
            return

        # We choose a random card...
        index = self._get_next_index()
        card = self.cards[index]

        # We play the card...
        if type(card) == GetOutOfJailFree:
            # The card is Get Out Of Jail Free.
            # We give it to the player...
            player.state.get_out_of_jail_free_cards.append(card)
            player.ai.got_get_out_of_jail_free_card()

            # And remove it from the deck...
            del self.cards[index]
        else:
            # The card is not Get Out Of Jail Free, so we can play it now...
            card.play(game, player)

    @property
    def number_of_cards(self):
        '''
        Returns the number of cards in the deck.
        '''
        return len(self.cards)

    def _get_next_index(self):
        '''
        Returns the index of the next card to take.
        '''
        return random.randint(0, self.number_of_cards-1)

