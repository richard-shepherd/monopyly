from ..game import *


class GenerousDaddyAI(PlayerAIBase):
    '''
    An AI that plays like a dad (or at least, like I play when
    I'm playing with my children).

    - It initially buys any properties it can.
    - If it runs out of money it will mortgage properties to be
      able to try to complete a set or build houses.
    - It makes favourable deals with other players.
    - It keeps a small reserve of cash
    '''
    def get_name(self):
        return "Generous Daddy"

    def landed_on_unowned_property(self, game_state, player, property):
        if player_state.cash > 500 + price:
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

