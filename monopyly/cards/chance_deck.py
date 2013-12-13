from ..squares import Square
from .deck import Deck
from .reward_card import RewardCard
from .fine_card import FineCard
from .get_out_of_jail_free import GetOutOfJailFree
from .advance_to import AdvanceTo
from .go_back_three_spaces import GoBackThreeSpaces
from .go_to_jail_card import GoToJailCard
from .repairs import Repairs


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

        # You are Assessed for Street Repairs £40 per House £115 per Hotel...
        self.cards.append(Repairs(40, 115))

        # Go to Jail. Move Directly to Jail. Do not pass "Go" Do not Collect £200...
        self.cards.append(GoToJailCard())

        # Bank pays you Dividend of £50...
        self.cards.append(RewardCard(50))

        # Go back 3 Spaces...
        self.cards.append(GoBackThreeSpaces())

        # Pay School Fees of £150...
        self.cards.append(FineCard(150))

        # Make General Repairs on all of Your Houses. For each House pay £25. For each Hotel pay £100...
        self.cards.append(Repairs(25, 100))

        # Speeding Fine £15...
        self.cards.append(FineCard(15))

        # You have won a Crossword Competition Collect £100...
        self.cards.append(RewardCard(100))

        # Your Building and Loan Matures Collect £150...
        self.cards.append(RewardCard(150))

        # Get out of Jail Free...
        self.cards.append(GetOutOfJailFree(self))

        # Advance to Trafalgar Square If you Pass "Go" Collect £200...
        self.cards.append(AdvanceTo(Square.Name.TRAFALGAR_SQUARE))

        # Take a Trip to Marylebone Station and if you Pass "Go" Collect £200...
        self.cards.append(AdvanceTo(Square.Name.MARYLEBONE_STATION))

        # Advance to Pall Mall If you Pass "Go" Collect £200...
        self.cards.append(AdvanceTo(Square.Name.PALL_MALL))

        # "Drunk in Charge" Fine £20...
        self.cards.append(FineCard(20))

