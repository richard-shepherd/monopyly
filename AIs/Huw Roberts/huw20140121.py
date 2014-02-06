import atexit
from monopyly import *
from collections import Counter
import random

# offer cash again sometimes
# keep a track of offers made and refused
# keep a track of the behaviour of other players
# offer different amounts of cash
# do more with BORING sets (such as using them in the get out of jail function)

# Qubix Brookwood
# Retail Decisions


class OtherPlayer(object):
    def __init__(self, name):
        self.name = name
        self.will_sell_for_cash = 0.5
        self.sell_for_cash_confidence = 0.0
        self.max_auction_premium = 0

class SetInfo(object):
    class State(object):
        NONE_OWNED = 0
        ONE_OWNED = 1
        TWO_OF_THREE_OWNED_DIFFERENT = 2
        TWO_OF_THREE_OWNED_SAME = 3
        OWNED_OUTRIGHT = 4
        THREE_OWNED_TWO_OWNERS = 5
        THREE_OWNED_THREE_OWNERS = 6
        TWO_OF_TWO_OWNED_DIFFERENT = 7
        BORING = 8

    def __init__(self, state, owners, props):
        self.state = state
        self.owners = owners
        self.props = props

    def make(owners, props):
        if owners[0] == owners[1]:
            if len(props) == 2:
                return SetInfo(SetInfo.State.OWNED_OUTRIGHT, [owners[0]], props)
            else:
                return SetInfo(SetInfo.State.TWO_OF_THREE_OWNED_SAME, [owners[0]], props)
        else:
            if len(props) == 2:
                return SetInfo(SetInfo.State.TWO_OF_TWO_OWNED_DIFFERENT, owners, props)
            else:
                return SetInfo(SetInfo.State.TWO_OF_THREE_OWNED_DIFFERENT, owners, props)
            return

def log_player_state(player):
    text = ''
    # don't deal with streets where another street in the set has houses
    for x in player.state.properties:
        text = text + x.name +'('
        if x.is_mortgaged:
            text += 'mortgaged'
        if (type(x) == Street):
            if (x.number_of_houses > 0):
                text += str(x.number_of_houses)+'houses'
        text += ') '
    Logger.log(player.ai.get_name()+" has "+text, Logger.DEBUG)


def work_out_owners(property_set):
    """
    @param property_set a PropertySet
    @return: SetInfo
    """
    if type(property_set.properties[0]) != Street:
        return SetInfo(SetInfo.State.BORING, [], [])
    prop1 = property_set.properties[0]
    owner1 = prop1.owner
    prop2 = property_set.properties[1]
    owner2 = prop2.owner
    if len(property_set.properties) == 2:
        if owner1 == None:
            if owner2 == None:
                return SetInfo(SetInfo.State.NONE_OWNED, [], [prop1, prop2])
            else:
                return SetInfo(SetInfo.State.ONE_OWNED, [owner2], [prop2, prop1])
        else:
            if owner2 == None:
                return SetInfo(SetInfo.State.ONE_OWNED, [owner1], [prop1, prop2])
            else:
                return SetInfo.make([owner1,owner2], [prop1,prop2])
    else: # len(property_set) == 3
        prop3 = property_set.properties[2]
        owner3 = prop3.owner
        if owner1 == None:
            if owner2 == None:
                if owner3 == None: # XXX
                    return SetInfo(SetInfo.State.NONE_OWNED, [], [prop1,prop2,prop3])
                else: # XXA
                    return SetInfo(SetInfo.State.ONE_OWNED, [owner3],[prop3,prop1,prop2])
            else:
                if owner3 == None: # XAX
                    return SetInfo(SetInfo.State.ONE_OWNED, [owner2],[prop2,prop1,prop3])
                else: # XA?
                    return SetInfo.make([owner2,owner3], [prop2,prop3,prop1])
        else:
            if owner2 == None:
                if owner3 == None: # AXX
                    return SetInfo(SetInfo.State.ONE_OWNED, [owner1], [prop1,prop2,prop3])
                else: # AX?
                    return SetInfo.make([owner1,owner3],[prop1,prop3,prop2])
            else:
                if owner3 == None: # A?X
                    return SetInfo.make([owner1,owner2],[prop1,prop2,prop3])
                else: # A??
                    # three owners
                    if owner1 == owner2:
                        if owner2 == owner3: # AAA
                            return SetInfo(SetInfo.State.OWNED_OUTRIGHT, [owner1],[prop1,prop2,prop3])
                        else: # AAB
                            return SetInfo(SetInfo.State.THREE_OWNED_TWO_OWNERS, [owner1,owner3],[prop1,prop2,prop3])
                    else:
                        if (owner1 == owner3): # ABA
                            return SetInfo(SetInfo.State.THREE_OWNED_TWO_OWNERS, [owner1,owner2],[prop1,prop3,prop2])
                        else:
                            if (owner2 == owner3): # ABB
                                return SetInfo(SetInfo.State.THREE_OWNED_TWO_OWNERS, [owner2,owner1],[prop2,prop3,prop1])
                            else: # ABC
                                return SetInfo(SetInfo.State.THREE_OWNED_THREE_OWNERS, [owner1,owner2,owner3],[prop1,prop2,prop3])

def is_partial_owner(info, player):
    for owner in info.owners:
        if owner == player:
            return True
    return False

def dont_deal():
    return DealResponse(action=DealResponse.Action.REJECT)

def deal_if_favorable():
    return DealResponse(action=DealResponse.Action.REJECT)

def deal_always():
    return DealResponse(action=DealResponse.Action.ACCEPT)


class PostGiftState:
    S_BAA = 0 # breaks A's set
    S_BAB = 1 # gives B two of three where A had two of three
    S_BAC = 2 # gives B one of A's pair
    S_BAX = 3 # gives B one of A's pair
    S_BBB = 4 # gives B the last of the set
    S_BBC = 5 # gives B two of three
    S_BBX = 6 # gives B two of three
    S_BCC = 7 # gives B negotiation
    S_BC  = 8 # gives B negotiation
    S_BCD = 9 # nothing special
    S_BCX = 10 # gives B a little negotiation
    S_BXX = 11 # gives B potential
    BORING = 12

    x = dont_deal
    d = deal_if_favorable
    y = deal_always

    deal_array = \
        [
            [ x,x,x,x,d,x,x,x,x,x,x,x,x ],
            [ x,x,x,x,y,d,y,x,x,x,x,x,x ],
        ]

    def gift_result(self, set_info, p1, p2):
        """
        Figure out the result of giving away a property from a set before the gift takes place
        """
        if set_info.state == SetInfo.State.OWNED_OUTRIGHT and set_info.owners[0] == p1:
            return PostGiftState.S_BAA
        elif set_info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and set_info.owners[0] == p1 and set_info.owners[1] == p2:
            return PostGiftState.S_BAB
        elif set_info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and set_info.owners[0] == p1 and set_info.owners[1] != None:
            return PostGiftState.S_BAC
        elif set_info.state == SetInfo.State.TWO_OF_THREE_OWNED_SAME and set_info.owners[0] == p1:
            return PostGiftState.S_BAX
        elif set_info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and set_info.owners[0] == p2 and set_info.owners[1] == p1:
            return PostGiftState.S_BBB
        elif set_info.state == SetInfo.State.THREE_OWNED_THREE_OWNERS and \
                (set_info.owners[0] == p1 or set_info.owners[1] == p1 or set_info.owners[2] == p1) and \
                (set_info.owners[0] == p2 or set_info.owners[1] == p2 or set_info.owners[2] == p2):
            return PostGiftState.S_BBC
        elif set_info.state == SetInfo.State.TWO_OF_THREE_OWNED_DIFFERENT and (set_info.owners[0] == p1 or set_info.owners[1] == p1) and \
                (set_info.owners[0] == p2 or set_info.owners[1] == p2):
            return PostGiftState.S_BBX
        elif set_info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and set_info.owners[0] != p2 and set_info.owners[0] == p1:
            return PostGiftState.S_BCC
        elif set_info.state == SetInfo.State.TWO_OF_TWO_OWNED_DIFFERENT and (set_info[0] == p1 and set_info[1] != p2 or \
                set_info[1] == p1 and set_info[0] != p2):
            return PostGiftState.S_BC
        elif set_info.state == SetInfo.State.THREE_OWNED_THREE_OWNERS and \
                (set_info.owners[0] == p1 or set_info.owners[1] == p1 or set_info.owners[2] == p1) and \
                (set_info.owners[0] != p2 and set_info.owners[1] != p2 and set_info.owners[2] != p2):
            return PostGiftState.S_BCD
        elif set_info.state == SetInfo.State.TWO_OF_THREE_OWNED_DIFFERENT and \
                (set_info.owners[0] == p1 or set_info.owners[1] == p1) and \
                (set_info.owners[0] != p2 and set_info.owners[1] != p2):
            return PostGiftState.S_BCX
        elif set_info.state == SetInfo.State.ONE_OWNED and set_info.owners[0] == p1:
            return PostGiftState.S_BXX
        return PostGiftState.BORING

    def should_do_deal(self, me,p2, s1,s2):
        '''
        Should we do a deal between me and p2 where p2 is offering one of s2 to me and
        asking for one of s1 in return?
        '''
        i = self.gift_result(s2,me,p2)
        j = self.gift_result(s1,p2,me)
        func = self.deal_array[i,j]
        return func()



def on_exit(huw_ai):
    print(huw_ai.square_counters)

class HuwAI20140121(PlayerAIBase):
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
                             PropertySet.PURPLE, PropertySet.GREEN, PropertySet.DARK_BLUE, PropertySet.BROWN,
                             PropertySet.STATION, PropertySet.UTILITY]
        self.square_counters = Counter()


    def start_of_game(self):
        self.is_start_of_game = True
        self.others_in_game = {}
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
        return "Huw Boring"

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

    def deal_proposed(self, game_state, me, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''
        # We won't look at deals with multiple properties involved...
        # Only property for cash or property for property...
        if len(deal_proposal.properties_offered) > 1:
            return DealResponse(DealResponse.Action.REJECT)
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)

        avail_cash = me.state.cash + self.easy_reserve
        them = deal_proposal.proposed_by_player
        if len(deal_proposal.properties_offered) == 1 and len(deal_proposal.properties_wanted) == 1:
            property_offered = deal_proposal.properties_offered[0]
            property_wanted = deal_proposal.properties_wanted[0]
            info_offered = work_out_owners(property_offered.property_set)
            info_wanted = work_out_owners(property_wanted.property_set)
            # we'll go for it if it gives us a set and doesn't ruin a set we've already got
            if info_offered.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and info_offered.owners[0] == me and \
                    info_wanted.state != SetInfo.State.OWNED_OUTRIGHT:
                return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=max(0,min(property_offered.price - property_wanted.price, avail_cash)))
            # we'll go for it if it adds to a set we've got at least one of and doesn't break up one of our sets and doesn't give him a set
            elif is_partial_owner(info_offered, me) and \
                    info_wanted.state != SetInfo.State.OWNED_OUTRIGHT and \
                    (info_wanted.state != SetInfo.State.THREE_OWNED_TWO_OWNERS):
                pass

        elif len(deal_proposal.properties_offered) == 1:
            property = deal_proposal.properties_offered[0]
            info = work_out_owners(property.property_set)
            if info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and info.owner1 == me:
                return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=min(property.price*2, avail_cash))
            else:
                return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=min(property.price, avail_cash))
        elif len(deal_proposal.properties_wanted) == 1:
            # never just give away a property for money
            pass
        else:
            pass
        return DealResponse(action=DealResponse.Action.REJECT)

    def deal_result(self, deal_info):
        if deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED:
            Logger.log("** Deal result: INVALID_DEAL_PROPOSED", Logger.DEBUG)
        elif deal_info == PlayerAIBase.DealInfo.SUCCEEDED:
            Logger.log("** Deal result: SUCCEEDED", Logger.DEBUG)
        elif deal_info == PlayerAIBase.DealInfo.DEAL_REJECTED:
            Logger.log("** Deal result: DEAL_REJECTED", Logger.DEBUG)

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
        worth_requesting = []
        infos = dict([ ( set, work_out_owners(player.board.get_property_set(set)) ) for set in self.sets_we_like])
        for info in infos.values():
            if info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and info.owners[0] == player:
                worth_requesting.append( (info.props[2], info) )
            elif info.State == SetInfo.State.TWO_OF_TWO_OWNED_DIFFERENT or info.State == SetInfo.State.TWO_OF_THREE_OWNED_DIFFERENT:
                if info.owners[0] == player:
                    worth_requesting.append( (info.props[1], info) )
                elif info.owners[1] == player:
                    worth_requesting.append( (info.props[0], info) )
            elif info.State == SetInfo.State.THREE_OWNED_THREE_OWNERS:
                if info.owners[0] == player:
                    worth_requesting.append( (info.props[1], info) )
                    worth_requesting.append( (info.props[2], info) )
                elif info.owners[1] == player:
                    worth_requesting.append( (info.props[0], info) )
                    worth_requesting.append( (info.props[2], info) )
                elif info.owners[2] == player:
                    worth_requesting.append( (info.props[0], info) )
                    worth_requesting.append( (info.props[1], info) )

        if len(worth_requesting) > 0:
            (wanted,info) = worth_requesting[random.randint(0,len(worth_requesting)-1)]
            # offer something back
            offer_to = wanted.owner
            Logger.log("Request {} from {}".format(wanted.name, offer_to.ai.get_name()), Logger.DEBUG)
            log_player_state(offer_to)
            for offered in player.state.properties:
                info = infos[offered.property_set.set_enum]
                if info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and info.owners[0] == offer_to:
                    diff = wanted.price - offered.price
                    if diff > 0:
                        return DealProposal(
                            propose_to_player=offer_to,
                            properties_wanted=[wanted],
                            properties_offered =[offered],
                            maximum_cash_offered=diff)
                    else:
                        return DealProposal(
                            propose_to_player=offer_to,
                            properties_wanted=[wanted],
                            properties_offered =[offered],
                            minimum_cash_wanted=-diff)

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
        for set in self.sets_we_like:
            properties = player.board.get_property_set(set)
            info = work_out_owners(properties)
            if info.state == SetInfo.State.NONE_OWNED or \
                    info.state == SetInfo.State.ONE_OWNED or \
                    info.state == SetInfo.State.TWO_OF_THREE_OWNED_SAME:
                return self._get_me_out_of_jail(player)
        return PlayerAIBase.Action.STAY_IN_JAIL

    def _get_me_out_of_jail(self, player):
        if (player.state.number_of_get_out_of_jail_free_cards > 0):
            return PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
        else:
            if player.state.cash > 50:
                return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
            else:
                return PlayerAIBase.Action.STAY_IN_JAIL

    def auction_result(self, status, property, player, amount_paid):
        if (status == PlayerAIBase.Action.AUCTION_SUCCEEDED and player.ai != self):
            premium = amount_paid - property.price
            other_player = self.others_in_game[player.name]
            other_player.max_auction_premium = max(other_player.max_auction_premium, premium)

    def player_landed_on_square(self, game_state, square, player):
        self.square_counters[square.name]+=1

    def deal_completed(self, deal_result):
        Logger.log("* Deal completed", Logger.DEBUG)
