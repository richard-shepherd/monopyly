from ..squares import Square
from .deck import Deck
from .reward_card import RewardCard
from .fine_card import FineCard
from .get_out_of_jail_free import GetOutOfJailFree
from .advance_to import AdvanceTo
import random


class ChanceDeck(Deck):
    '''
    Manages the set of Chance cards.
    '''

    def __init__(self):
        '''
        The 'constructor'
        '''
        super().__init__()

        # Advance to Mayfair...
        self.cards.append(AdvanceTo(Square.Name.MAYFAIR))

        # Advance to Go...
        self.cards.append(AdvanceTo(Square.Name.GO))

        # TODO: 3) You are Assessed for Street Repairs $40 per House $115 per Hotel
        # TODO: 4) Go to Jail. Move Directly to Jail. Do not pass "Go" Do not Collect $200.

        # Bank pays you Dividend of £50...
        self.cards.append(RewardCard(50))

        # TODO: 6) Go back 3 Spaces

        # Pay School Fees of £150...
        self.cards.append(FineCard(150))

        # TODO: 8) Make General Repairs on all of Your Houses
        #For each House pay $25
        #For each Hotel pay $100

        # Speeding Fine £15...
        self.cards.append(FineCard(15))

        # You have won a Crossword Competition Collect £100...
        self.cards.append(RewardCard(100))

        # Your Building and Loan Matures Collect £150...
        self.cards.append(RewardCard(150))

        # Get out of Jail Free...
        self.cards.append(GetOutOfJailFree())

        # Advance to Trafalgar Square If you Pass "Go" Collect £200...
        self.cards.append(AdvanceTo(Square.Name.TRAFALGAR_SQUARE))

        # Take a Trip to Marylebone Station and if you Pass "Go" Collect £200...
        self.cards.append(AdvanceTo(Square.Name.MARYLEBONE_STATION))

        # Advance to Pall Mall If you Pass "Go" Collect £200...
        self.cards.append(AdvanceTo(Square.Name.PALL_MALL))

        # "Drunk in Charge" Fine £20...
        self.cards.append(FineCard(20))

        random.shuffle(self.cards)

