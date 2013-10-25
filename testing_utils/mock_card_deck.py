from monopyly import Deck


class MockCardDeck(Deck):
    '''
    Mocks the Chance or CommunityChest deck, letting you
    control which card is taken next.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__()

    def set_next_card(self, card):
        '''
        Sets the card which will be taken next.
        '''
        self.cards = [card]
        self.index = 0
