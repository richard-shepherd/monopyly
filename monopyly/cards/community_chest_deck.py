from ..squares import Square
from .deck import Deck
from .reward_card import RewardCard
from .fine_card import FineCard
from .get_out_of_jail_free import GetOutOfJailFree
from .advance_to import AdvanceTo
from .go_back import GoBack
import random


class CommunityChestDeck(Deck):
    '''
    Manages the deck of Community Chest cards.
    '''

    def __init__(self):
        '''
        The 'constructor'
        '''
        super().__init__()

        # Income Tax refund Collect £20...
        self.cards.append(RewardCard(20))

        # From Sale of Stock you get £50...
        self.cards.append(RewardCard(50))

        # TODO: 3) It is YourBirthday Collect $10 from each Player
        # Receive Interest on 7% Preference Shares £25...
        self.cards.append(RewardCard(25))

        # Get out of Jail Free...
        self.cards.append(GetOutOfJailFree())

        # Advance to "Go"...
        self.cards.append(AdvanceTo(Square.Name.GO))

        # Pay Hospital £100...
        self.cards.append(FineCard(100))

        # You have Won Second Prize in a Beauty Contest Collect £10...
        self.cards.append(RewardCard(10))

        # Bank Error in your Favour Collect £200...
        self.cards.append(RewardCard(200))

        # You Inherit £100...
        self.cards.append(RewardCard(100))

        # TODO: 11) Go to Jail. Move Directly to Jail. Do not Pass "Go". Do not Collect $200
        # Pay your Insurance Premium £50...
        self.cards.append(FineCard(50))

        # TODO: 13) Pay a $10 Fine or Take a "Chance"
        # Doctor's Fee Pay £50...
        self.cards.append(FineCard(50))

        # Go Back to Old Kent Road...
        self.cards.append(GoBack(Square.Name.OLD_KENT_ROAD))

        # Annuity Matures Collect £100...
        self.cards.append(RewardCard(100))

        random.shuffle(self.cards)


