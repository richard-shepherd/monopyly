from monopyly import *


class GreenDevilAI(PlayerAIBase):
    '''
    This player does nothing - just has the default behaviour
    of the base AI. It does not buy properties, make deals etc.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cash_reserve = 400
        self.properties_we_like = [Square.Name.MAYFAIR,
                                   Square.Name.PARK_LANE,
                                   Square.Name.BOND_STREET,
                                   Square.Name.OXFORD_STREET,
                                   Square.Name.REGENT_STREET,
                                   Square.Name.KINGS_CROSS_STATION,
                                   Square.Name.FENCHURCH_STREET_STATION,
                                   Square.Name.LIVERPOOL_STREET_STATION,
                                   Square.Name.MARYLEBONE_STATION,
                                   Square.Name.ELECTRIC_COMPANY,
                                   Square.Name.WATER_WORKS]

        self.properties_we_dont_trade = [Square.Name.MAYFAIR,
                                   Square.Name.PARK_LANE,
                                   Square.Name.BOND_STREET,
                                   Square.Name.OXFORD_STREET,
                                   Square.Name.REGENT_STREET]

    def get_name(self):
        return "Green Devil"

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Compro se esta na minha lista de propriedades e se consigo guardar uma reserva de 400
        '''

        if property.name not in self.properties_we_like:
            return

        if player.state.cash > (self.cash_reserve + property.price):
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''

        if (len(deal_proposal.properties_wanted) > 0) \
            and (deal_proposal.properties_wanted[0] in self.properties_we_dont_trade):
            return DealResponse(DealResponse.Action.REJECT)

        # We only accept deals for single properties wanted from us...
        if len(deal_proposal.properties_offered) > 0:
            return DealResponse(DealResponse.Action.REJECT)
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)

        # We'll accept as long as the price offered is greater than
        # the original selling price...
        property = deal_proposal.properties_wanted[0]
        return DealResponse(
            action=DealResponse.Action.ACCEPT,
            minimum_cash_wanted=property.price+50)

    def build_houses(self, game_state, player):
        '''
        Gives us the opportunity to build houses.
        '''
        # We find the first set we own that we can build on...
        for owned_set in player.state.owned_unmortgaged_sets:
            # We can't build on stations or utilities, or if the
            # set already has hotels on all the properties...
            if not owned_set.can_build_houses:
                continue

            # We see how much money we need for one house on each property...
            cost = owned_set.house_price * owned_set.number_of_properties
            if player.state.cash > (self.cash_reserve + cost):
                # We build one house on each property...
                return [(p, 1) for p in owned_set.properties]


        # We can't build...
        return []

    def property_offered_for_auction(self, game_state, player, property):
        '''
        We offer the face value in auctions.
        '''
        if property.name in self.properties_we_dont_trade:
            return property.price + 49

        return property.price -50


    def players_birthday(self):

        return "Happy Birthday!"

    def get_out_of_jail(self, game_state, player):
        '''
        Called in the player's turn, before the dice are rolled, if the player
        is in jail.

        There are three possible return values:
        PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
        PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
        PlayerAIBase.Action.STAY_IN_JAIL

        Buying your way out of jail will cost £50.

        The default action is STAY_IN_JAIL.
        '''
        if player.state.cash < (self.cash_reserve + 50):

            return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
        else:
            return PlayerAIBase.Action.STAY_IN_JAIL

