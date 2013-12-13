from monopyly import Deck


class MockCardDeck(Deck):
    '''
    A mock for card decks.
    '''

    def __init__(self, next_card=None):
        '''
        The 'constructor'.
        '''
        super().__init__()
        self.index = 0
        if next_card:
            self.set_next_card(next_card)

    def set_next_card(self, card):
        '''
        Sets the card which will be taken next.
        '''
        self.cards = [card]
        self.index = 0

    def set_next_cards(self, cards):
        '''
        Sets a list of the next cards to play.
        '''
        self.cards = cards
        self.index = 0

    def _get_next_index(self):
        '''
        Returns the index of the next card to use.
        '''
        if self.index >= self.number_of_cards:
            self.index = 0
        index = self.index
        self.index += 1
        return index

