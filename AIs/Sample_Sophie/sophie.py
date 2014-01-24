from monopyly import *


class SophieAI(PlayerAIBase):
    '''
    An AI that plays like Sophie.

    She only buys the stations and Mayfair and Park Lane, and
    will enter into fairly generous deals to get hold of them.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.properties_we_like = [Square.Name.MAYFAIR,
                                   Square.Name.PARK_LANE,
                                   Square.Name.KINGS_CROSS_STATION,
                                   Square.Name.MARYLEBONE_STATION,
                                   Square.Name.FENCHURCH_STREET_STATION,
                                   Square.Name.LIVERPOOL_STREET_STATION]

    def get_name(self):
        '''
        Returns this AI's name.
        '''
        return "Sophie"

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property.

        If it is a station or Mayfair or Park Lane, we'll buy it.
        '''
        # Is the property one of the ones we want to buy?
        if property.name not in self.properties_we_like:
            return PlayerAIBase.Action.DO_NOT_BUY

        # We want to buy the property, but do we have enough money?
        if player.state.cash > property.price:
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY

    def propose_deal(self, game_state, player):
        '''
        We have the opportunity to propose a deal.

        If any other player has one of the properties we want, we
        offer them 2x the price for it.
        '''
        deal_proposal = DealProposal()

        # We check to see if any of the properties we like is owned
        # by another player...
        for property_name in self.properties_we_like:
            property = game_state.board.get_square_by_name(property_name)
            if(property.owner is player or property.owner is None):
                # The property is either not owned, or owned by us...
                continue

            # The property is owned by another player, so we make them an
            # offer for it...
            price_offered = property.price * 2
            if player.state.cash > price_offered:
                return DealProposal(
                    properties_wanted=[property],
                    maximum_cash_offered=price_offered,
                    propose_to_player=property.owner)

        # We do not want to propose a deal...
        return None

    def build_houses(self, game_state, player):
        '''
        Sophie always tries to build houses if she can.
        '''
        if player.state.cash < 1000:
            return []

        for owned_set in player.state.owned_unmortgaged_sets:
            if not owned_set.can_build_houses:
                continue
            return [(p, 1) for p in owned_set.properties]

        return []

    def mortgage_properties(self, game_state, player):
        '''
        Sophie mortgages if she is short of cash.
        '''
        if player.state.cash < 500:
            return [p for p in player.state.properties if p.is_mortgaged is False]

    def unmortgage_properties(self, game_state, player):
        '''
        Sophie unmortgages if she is flush with cash.
        '''
        if player.state.cash > 2000:
            return [p for p in player.state.properties if p.is_mortgaged is True]

    def players_birthday(self):
        '''
        Sophie is polite.
        '''
        return "Happy Birthday!"
