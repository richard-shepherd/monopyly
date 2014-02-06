__author__ = 'Cedric'

from ..Memory import *
from monopyly import *

class DealPolicy(object):
    def __init__(self,memory):
        '''
        ctor
        '''
        self.memory = memory
        self.properties_we_like = [
            [Square.Name.OLD_KENT_ROAD,             80],
            [Square.Name.WHITECHAPEL_ROAD,          80],
            [Square.Name.KINGS_CROSS_STATION,       100],
            [Square.Name.THE_ANGEL_ISLINGTON,       80],
            [Square.Name.EUSTON_ROAD,               80],
            [Square.Name.PENTONVILLE_ROAD,          80],
            [Square.Name.PALL_MALL,                 1],
            [Square.Name.ELECTRIC_COMPANY,          50],
            [Square.Name.WHITEHALL,                 1],
            [Square.Name.NORTHUMBERLAND_AVENUE,     1],
            [Square.Name.MARYLEBONE_STATION,        10],
            [Square.Name.BOW_STREET,                1],
            [Square.Name.MARLBOROUGH_STREET,        1],
            [Square.Name.VINE_STREET,               1],
            [Square.Name.STRAND,                    1],
            [Square.Name.FLEET_STREET,              1],
            [Square.Name.TRAFALGAR_SQUARE,          1],
            [Square.Name.FENCHURCH_STREET_STATION,  10],
            [Square.Name.LEICESTER_SQUARE,          1],
            [Square.Name.COVENTRY_STREET,           1],
            [Square.Name.WATER_WORKS,               50],
            [Square.Name.PICCADILLY,                1],
            [Square.Name.REGENT_STREET,             1],
            [Square.Name.OXFORD_STREET,             1],
            [Square.Name.BOND_STREET,               1],
            [Square.Name.LIVERPOOL_STREET_STATION,  10],
            [Square.Name.PARK_LANE,                 80],
            [Square.Name.MAYFAIR,                   80] ]

    def compute(self, game_state, player, deal_proposal):
        '''
        Called when another player proposes a deal to you.

        See propose_deal (above) for details of the DealProposal object.

        Return a DealResponse object.

        To reject a deal:
            return DealResponse(DealResponse.Action.REJECT)

        To accept a deal:
            return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=300)
            or
            return DealResponse(DealResponse.Action.ACCEPT, minimum_cash_wanted=800)

        The default is to reject the deal.
        '''
        return DealResponse(PlayerAIBase.DealInfo.DEAL_REJECTED)

    def propose(self, ia, game_state, player):
        '''
        Called to allow the player to propose a deal.

        You return a DealProposal object.

        If you do not want to make a deal, return None.

        If you want to make a deal, you provide this information:
        - The player number of the player you are proposing the deal to
        - A list of properties offered
        - A list of properties wanted
        - Maximum cash offered as part of the deal
        - Minimum cash wanted as part of the deal.

        Properties offered and properties wanted are passed as lists of
        Property objects.

        If you offer money as part of the deal, set the cash wanted to zero
        and vice versa.

        Note that the cash limits will not be shown to the proposed-to player.
        When the deal is offered to them, they set their own limits for accepting
        the deal without seeing your limits. If the limits are acceptable to both
        players, the deal will be done at the halfway point.

        For example, Player1 proposes:
          Propose to: Player2
          Properties offered: Mayfair
          Properties wanted: (none)
          Maximum cash offered: 0
          Minimum cash wanted: 500

        Player2 accepts with these limits:
          Maximum cash offered: 1000
          Minimum cash wanted: 0

        The deal will be done with Player2 receiving Mayfair and paying £750
        to Player1.

        The only 'negotiation' is in the managing of cash along with the deal
        as discussed above. There is no negotiation about which properties are
        part of the deal. If a deal is rejected because it does not contain the
        right properties, another deal can be made at another time with different
        lists of properties.

        Example construction and return of a DealProposal object:
            return DealProposal(
                propose_to_player_number=2,
                properties_offered=[vine_street, bow_street],
                properties_wanted=[park_lane],
                maximum_cash_offered=200)

        The default is for no deal to be proposed.
        '''
        for property_name in self.properties_we_like:
            if property_name[1] > 55:
                property = game_state.board.get_square_by_name(property_name[0])
                if(property.owner is player or property.owner is None):
                    # The property is either not owned, or owned by us...
                    continue

                # The property is owned by another player, so we make them an
                # offer for it...
                price_offered = property.price * 1.2
                if player.state.cash > price_offered:
                    return DealProposal(
                        properties_wanted=[property],
                        maximum_cash_offered=price_offered,
                        propose_to_player=property.owner)
        return None
