from ..game import *


class DaddyAI(PlayerAIBase):
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
        return "Daddy"

    def landed_on_unowned_property(self, game_state, player_state, property_name, price):
        if player_state.cash > 500 + price:
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY


