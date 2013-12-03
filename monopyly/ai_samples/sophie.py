from ..game import *
from ..squares import *


class SophieAI(PlayerAIBase):
    '''
    An AI that plays like Sophie.

    She only buys the stations and Mayfair and Park Lane, and
    will enter into fairly generous deals to get hold of them.
    '''
    def get_name(self):
        return "Sophie"

    def landed_on_unowned_property(self, game_state, player_state, property_name, price):
        # Is the property one of the ones we want to buy?
        if property_name not in [Square.Name.MAYFAIR,
                                 Square.Name.PARK_LANE,
                                 Square.Name.KINGS_CROSS_STATION,
                                 Square.Name.MARYLEBONE_STATION,
                                 Square.Name.FENCHURCH_STREET_STATION,
                                 Square.Name.LIVERPOOL_STREET_STATION]:
            return

        # We want to buy the property, but do we have enough money?
        if player_state.cash > price:
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY

    def propose_deal(self, game_state, player_state):
        return DealProposal()

