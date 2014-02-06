import atexit
from monopyly import *
from collections import Counter
import random

# can this player make a set by getting this property
def can_make_set_with_property(player, property):
    if type(property) != Street:
        return False
    if (player == property.property_set.owner):
        return False
    for p in property.property_set.properties:
        if (p != property and p.owner != player):
            return False
    return True

class OtherPlayer(object):
    def __init__(self, name):
        self.name = name
        self.will_sell_for_cash = 0.5
        self.sell_for_cash_confidence = 0.0
        self.max_auction_premium = 0

class SetInfo(object):
    def __init__(self, name):
        pass

def on_exit(huw_ai):
    print(huw_ai.square_counters)

class HuwAI20140104(PlayerAIBase):
    '''
    An AI that plays like Huw.
    - It initially buys any properties it can.
    - It builds houses when it has complete sets.
    - It makes favourable deals with other players.
    - It keeps almost no cash.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.is_start_of_game = True
        self.registered_exit = False
        self.cash_reserve = 500
        self.extreme_reserve = 200
        self.easy_reserve = 0
        self.hard_reserve = 0
        self.others = {}
        self.others_in_game = {}
        self.sets_we_like = [PropertySet.ORANGE, PropertySet.LIGHT_BLUE, PropertySet.YELLOW, PropertySet.RED,
                             PropertySet.PURPLE, PropertySet.GREEN, PropertySet.DARK_BLUE, PropertySet.BROWN]
        self.square_counters = Counter()
        self.set_info = {}


    def start_of_game(self):
        self.is_start_of_game = True
        self.others_in_game = {}
        self.set_info = {}
        if not self.registered_exit:
            atexit.register(on_exit, self)
            self.registered_exit = True

    def check_start_of_game(self, game_state):
        if (not self.is_start_of_game):
            return
        self.is_start_of_game = False
        for p in game_state.players:
            if (p.name != self.get_name()):
                if (not p.name in self.others):
                    Logger.log("{0} Found other player {1}".format(self.get_name(), p.name), Logger.INFO)
                    self.others[p.name] = OtherPlayer(p.name)
                self.others_in_game[p.name] = self.others[p.name]

    def get_name(self):
        return "Huw Conservative"

    def calculate_reserve(self, player):
        ''' figure out how much easy money we've got
        '''
        self.easy_reserve = 0
        self.hard_reserve = 0
        text = ''
        # don't deal with streets where another street in the set has houses
        for x in player.state.properties:
            text = text + x.name +'('
            if x.is_mortgaged:
                text += 'mortgaged'
            if not x.is_mortgaged and ((type(x) == Street and x.number_of_houses == 0) or type(x) != Street):
                self.easy_reserve += x.mortgage_value

            if (type(x) == Street):
                if (x.number_of_houses > 0):
                    text += str(x.number_of_houses)+'houses'
                    self.hard_reserve += x.house_price/2 + x.mortgage_value
            text += ') '

        Logger.log('* I\'ve got '+text, Logger.DEBUG)
        Logger.log('* I\'m worth cash {} with mortgages {} and selling houses {}'.format(
            player.state.cash, player.state.cash+self.easy_reserve, player.state.cash+self.easy_reserve+self.hard_reserve), Logger.DEBUG)
        #player.state.properties
        #self.


    def have_other_property_from_set(self, player, property):
        pass

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property. We always buy it if we
        can while keeping a small cash reserve.
        '''
        if (player.state.cash + self.easy_reserve) > (self.cash_reserve + property.price):
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''
        # We won't look at deals with multiple properties involved...
        # Only property for cash or property for property...
        if len(deal_proposal.properties_offered) > 1:
            return DealResponse(DealResponse.Action.REJECT)
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)

        # We'll accept a deal that gives us a property, either
        # for reasonable money or for a worse property.
        if len(deal_proposal.properties_offered) == 1 and len(deal_proposal.properties_wanted) == 1:
            pass
        elif len(deal_proposal.properties_offered) == 1:
            avail_cash = player.state.cash + self.easy_reserve
            property = deal_proposal.properties_offered[0]
            if can_make_set_with_property(self, property):
                return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=min(property.price*2, avail_cash))
            else:
                return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=min(property.price, avail_cash))
        elif len(deal_proposal.properties_wanted) == 1:
            pass
        else:
            pass
        return DealResponse(
            action=DealResponse.Action.REJECT,
            minimum_cash_wanted=0)

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
        max_tuple = max(self.others_in_game.items(), key = (lambda v: v[1].max_auction_premium) )
        offer = property.price + max_tuple[1].max_auction_premium + random.randint(1, 10)
#        offer = (int)(property.price * 1.4) + random.randint(-10, 10)
        offer = max(0, min(offer, player.state.cash+self.easy_reserve-self.cash_reserve))
        return offer

    def propose_deal(self, game_state, player):
        Logger.log("* Propose deal perhaps", Logger.DEBUG)
        avail_cash = player.state.cash + self.easy_reserve
        worth_offering = [x for x in game_state.board.squares
                          if can_make_set_with_property(player, x) and x.owner != None]

        if len(worth_offering) > 0:
            property = worth_offering[random.randint(0,len(worth_offering)-1)]
            offer = property.price + random.randint(1, 10)
            offer = max(0, min(offer, player.state.cash+self.easy_reserve-self.extreme_reserve))
            return DealProposal(
                propose_to_player=property.owner,
                properties_wanted=[property],
                maximum_cash_offered=offer)

        return None


    def start_of_turn(self, game_state, player):
        self.check_start_of_game(game_state)
        if (player.ai == self):
            self.calculate_reserve(player)

    def pay_ten_pounds_or_take_a_chance(self, game_state, player):
        return PlayerAIBase.Action.TAKE_A_CHANCE

    def players_birthday(self):
        return "Happy Birthday!"

    def money_will_be_taken(self, player, amount):
        Logger.log("* Money will be taken "+str(amount), Logger.DEBUG)
        self.owe = amount
        self.to_sell = max(0, amount - player.state.cash - self.easy_reserve)

    def mortgage_properties(self, game_state, player):
        Logger.log("* Mortgage perhaps", Logger.DEBUG)
        need = self.owe - player.state.cash
        to_mortgage = []
        for p in player.state.properties:
            if need > 0 and not p.is_mortgaged:
                to_mortgage.append(p)
                need -= p.mortgage_value

        return to_mortgage

    def sell_houses(self, game_state, player):
        Logger.log("* Sell perhaps", Logger.DEBUG)
        return []

    def get_out_of_jail(self, game_state, player):
        Logger.log("* Get out of jail perhaps", Logger.DEBUG)
        return PlayerAIBase.Action.STAY_IN_JAIL

    def auction_result(self, status, property, player, amount_paid):
        if (status == PlayerAIBase.Action.AUCTION_SUCCEEDED and player.ai != self):
            premium = amount_paid - property.price
            other_player = self.others_in_game[player.name]
            other_player.max_auction_premium = max(other_player.max_auction_premium, premium)

    def player_landed_on_square(self, game_state, square, player):
        self.square_counters[square.name]+=1

