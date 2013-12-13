from ..game import *
from ..squares import PropertySet


class GenerousDaddyAI(PlayerAIBase):
    '''
    An AI that plays like a dad (or at least, like I play when
    I'm playing with my children).

    - It initially buys any properties it can.
    - It builds houses when it has complete sets.
    - It makes favourable deals with other players.
    - It keeps a small reserve of cash.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cash_reserve = 500

    def get_name(self):
        '''
        Returns the name shown for this AI.
        '''
        return "Generous Daddy"

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property. We always buy it if we
        can while keeping a small cash reserve.
        '''
        if player.state.cash > (self.cash_reserve + property.price):
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''
        # We only accept deals for single properties wanted from us...
        if len(deal_proposal.properties_offered) > 0:
            return DealResponse(DealResponse.Action.REJECT)
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)

        # We'll accept as long as the price offered is greater than
        # the original selling price...
        property_name = deal_proposal.properties_wanted[0]
        property = game_state.board.get_square_by_name(property_name)
        return DealResponse(
            action=DealResponse.Action.ACCEPT,
            minimum_cash_wanted=property.price+1)

    def build_houses(self, game_state, player):
        '''
        Gives us the opportunity to build houses.
        '''
        # We find the first set we own that we can build on...
        for owned_set in player.state.owned_sets:
            # We can't build on stations or utilities, or if the
            # set already has hotels on all the properties...
            if not owned_set.can_build_houses:
                continue

            # We see how much money we need for one house on each property...
            cost = owned_set.house_price * owned_set.number_of_properties
            if player.state.cash > (self.cash_reserve + cost):
                # We build one house on each property...
                return [(p.name, 1) for p in owned_set.properties]

        # We can't build...
        return []



