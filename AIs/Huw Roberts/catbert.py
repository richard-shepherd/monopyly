import atexit
from monopyly import *
from collections import Counter
import random
from .utils import *

# go bankrupt "gracefully" - sell houses and sell property to losers.
# plan for the eminent domain


# keep a list of possible deals - reconstruct after each deal, auction, bankruptcy, etc. and at start of game



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
        ONE_OF_THREE_OWNED = 1
        TWO_OF_THREE_OWNED_DIFFERENT = 2
        TWO_OF_THREE_OWNED_SAME = 3
        OWNED_OUTRIGHT = 4
        THREE_OWNED_TWO_OWNERS = 5
        THREE_OWNED_THREE_OWNERS = 6
        TWO_OF_TWO_OWNED_DIFFERENT = 7
        BORING = 8
        ONE_OF_TWO_OWNED = 9

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
                return SetInfo(SetInfo.State.ONE_OF_TWO_OWNED, [owner2], [prop2, prop1])
        else:
            if owner2 == None:
                return SetInfo(SetInfo.State.ONE_OF_TWO_OWNED, [owner1], [prop1, prop2])
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
                    return SetInfo(SetInfo.State.ONE_OF_THREE_OWNED, [owner3],[prop3,prop1,prop2])
            else:
                if owner3 == None: # XAX
                    return SetInfo(SetInfo.State.ONE_OF_THREE_OWNED, [owner2],[prop2,prop1,prop3])
                else: # XA?
                    return SetInfo.make([owner2,owner3], [prop2,prop3,prop1])
        else:
            if owner2 == None:
                if owner3 == None: # AXX
                    return SetInfo(SetInfo.State.ONE_OF_THREE_OWNED, [owner1], [prop1,prop2,prop3])
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

def accept_no_deal(me,him,offered,wanted):
    return DealResponse(action=DealResponse.Action.REJECT)

def accept_deal_if_favorable(me,him,offered,wanted):
    offer_amount = offered.price - wanted.price # if negative then he should give me money
    if offer_amount < 0:
        return DealResponse(action=DealResponse.Action.ACCEPT, minimum_cash_wanted=-offer_amount)
    else:
        offer_amount = me.ai.make_offer_amount(me, offer_amount)
        return DealResponse(action=DealResponse.Action.ACCEPT, maximum_cash_offered=offer_amount)

def accept_deal_always(me,him,offered,wanted):
    offer_amount = offered.price - wanted.price # if negative then he should give me money
    if offer_amount < 0:
        # I want it, so just take the deal
        return DealResponse(action=DealResponse.Action.ACCEPT)
    else:
        offer_amount = me.ai.make_offer_amount(me, offer_amount)
        return DealResponse(action=DealResponse.Action.ACCEPT, maximum_cash_offered=offer_amount)


def make_no_deal(me,him,offered,wanted):
    return None

def make_deal_if_favourable(me,him,offered,wanted):
    offer_amount = offered.price - wanted.price # if negative then he should give me money
    if offer_amount < 0:
        return DealProposal(him, [offered],[wanted], 0, -offer_amount)
    else:
        offer_amount = me.ai.make_offer_amount(me, offer_amount)
        return DealProposal(him, [offered],[wanted], offer_amount)


def make_deal_always(me,him,offered,wanted):
    offer_amount = offered.price - wanted.price # if negative then he should give me money
    if offer_amount < 0:
        # I want it, so offer for nothing
        return DealProposal(him, [offered],[wanted])
    else:
        offer_amount = me.ai.make_offer_amount(me, offer_amount)
        return DealProposal(him, [offered],[wanted], offer_amount)


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

    class x:
        accept = accept_no_deal
        offer = make_no_deal

    class d:
        accept = accept_deal_if_favorable
        offer = make_deal_if_favourable

    class y:
        accept = accept_deal_always
        offer = make_deal_always

    deal_array = \
        [
            [ x,x,x,x,d,x,x,x,x,x,x,x,x ],
            [ x,x,x,x,y,d,y,x,x,x,x,x,x ],
            [ x,x,x,x,y,d,d,x,x,x,x,x,x ],
            [ x,x,x,x,y,d,d,x,x,x,x,x,x ],
            [ x,x,x,x,d,x,x,x,x,x,x,x,x ],
            [ d,x,d,d,y,d,y,x,d,x,x,x,x ],
            [ d,x,d,d,y,x,d,x,x,x,x,x,x ],
            [ x,y,y,y,y,y,y,d,d,x,x,y,x ],
            [ x,y,x,x,y,d,y,x,d,x,x,y,x ],
            [ y,y,y,y,y,y,y,y,y,d,y,y,x ],
            [ y,y,y,y,y,y,y,x,y,x,d,d,x ],
            [ x,y,y,y,y,y,y,x,x,x,d,d,x ],
            [ x,x,x,x,x,x,x,x,x,x,x,x,x ],
        ]

def gift_result(set_info, p1, p2):
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
    elif set_info.state == SetInfo.State.TWO_OF_TWO_OWNED_DIFFERENT and (set_info.owners[0] == p1 and set_info.owners[1] != p2 or \
            set_info.owners[1] == p1 and set_info.owners[0] != p2):
        return PostGiftState.S_BC
    elif set_info.state == SetInfo.State.THREE_OWNED_THREE_OWNERS and \
            (set_info.owners[0] == p1 or set_info.owners[1] == p1 or set_info.owners[2] == p1) and \
            (set_info.owners[0] != p2 and set_info.owners[1] != p2 and set_info.owners[2] != p2):
        return PostGiftState.S_BCD
    elif set_info.state == SetInfo.State.TWO_OF_THREE_OWNED_DIFFERENT and \
            (set_info.owners[0] == p1 or set_info.owners[1] == p1) and \
            (set_info.owners[0] != p2 and set_info.owners[1] != p2):
        return PostGiftState.S_BCX
    elif (set_info.state == SetInfo.State.ONE_OF_TWO_OWNED or set_info.state == SetInfo.State.ONE_OF_THREE_OWNED) and set_info.owners[0] == p1:
        return PostGiftState.S_BXX
    return PostGiftState.BORING

def should_accept_deal(me,him, offered,asked, offered_property,asked_property):
    '''
    Should we do a deal between me and him where he is offering one of offered to me and
    asking for one of asked in return?
    '''
    i = gift_result(asked,me,him)
    j = gift_result(offered,him,me)
    result = PostGiftState.deal_array[i][j].accept(me,him, offered_property, asked_property)
    return result

def make_offer(me,him, offered,asked, offered_property, asked_property):
    '''
    Should we make an offer to player p2 where we are offering one of s1 and
    we are asking for one of
    '''
    if asked_property.property_set == offered_property.property_set:
        return None
    i = gift_result(asked,me,him)
    j = gift_result(offered,him,me)
    result = PostGiftState.deal_array[i][j].offer(me,him, offered_property, asked_property)
    return result


class CatbertAI(PlayerAIBase):
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
        self.post_gift_state = PostGiftState()
        self.max_deals = 0
        self.is_eminent_domain = False

    def start_of_game(self):
        self.is_start_of_game = True
        self.others_in_game = {}
        self.max_deals = 0
        self.is_eminent_domain = False

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
        return "Catbert"

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
        # can't deal with complex stuff
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)

        avail_cash = me.state.cash + self.easy_reserve
        them = deal_proposal.proposed_by_player
        if len(deal_proposal.properties_offered) == 1 and len(deal_proposal.properties_wanted) == 1:
            property_offered = deal_proposal.properties_offered[0]
            property_wanted = deal_proposal.properties_wanted[0]
            info_offered = work_out_owners(property_offered.property_set)
            info_wanted = work_out_owners(property_wanted.property_set)
            return should_accept_deal(me, them, info_offered, info_wanted, property_offered, property_wanted)

        elif len(deal_proposal.properties_offered) > 0:
            property = deal_proposal.properties_offered[0]
            info = work_out_owners(property.property_set)
            if info.state == SetInfo.State.THREE_OWNED_TWO_OWNERS and info.owners[0] == me:
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


    def build_houses(self, game_state, me):
        return do_build_houses(game_state, me, self.sets_we_like, me.state.cash - self.cash_reserve)

    def property_offered_for_auction(self, game_state, me, property):
        multiplier = 1
        if self.is_eminent_domain:
            multiplier = 2
        info = work_out_owners(property.property_set)
        if (info.state == SetInfo.State.TWO_OF_THREE_OWNED_SAME or info.State == SetInfo.State.ONE_OF_TWO_OWNED) \
                and info.owners[0] == me:
            return self.make_offer_amount(me, property.price * 2.5 * multiplier)
        if info.state == SetInfo.State.TWO_OF_THREE_OWNED_SAME or info.State == SetInfo.State.ONE_OF_TWO_OWNED:
            return self.make_offer_amount(me, property.price * 2 * multiplier)
        if info.state == SetInfo.State.ONE_OF_THREE_OWNED and info.owners[0] == me:
            return self.make_offer_amount(me, property.price * 1.5 * multiplier)
        return self.make_offer_amount(me, property.price * multiplier)

    def make_offer_amount(self, player, target):
        target = target + random.randint(1, 20)
        offer = max(0, min(target, player.state.cash+self.easy_reserve-self.cash_reserve))
        return offer

    def work_out_deals(self, me):
        deals = []

        infos = dict([ ( set, work_out_owners(me.board.get_property_set(set)) ) for set in self.sets_we_like])
        for asked_property in me.board.squares:
            if type(asked_property) == Street:
                him = asked_property.owner
                if him != me and him != None:
                    for offered_property in me.state.properties:
                        offered = infos[offered_property.property_set.set_enum]
                        asked = infos[asked_property.property_set.set_enum]
                        deal = make_offer(me,him, offered,asked, offered_property, asked_property)
                        if deal != None:
                            deals.append(deal)
                    deals.append(DealProposal(him, None, [asked_property], self.make_offer_amount(me, asked_property.price)))
        self.max_deals = max(self.max_deals, len(deals))
        return deals

    def propose_deal(self, game_state, me):
        Logger.log("* Propose deal perhaps", Logger.DEBUG)
        if me.state.ai_processing_seconds_remaining < 3:
            return

        deals = self.work_out_deals(me)

        if len(deals) > 0:
            deal = deals[random.randint(0,len(deals)-1)]
            return deal

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
                    info.state == SetInfo.State.ONE_OF_THREE_OWNED or \
                    info.state == SetInfo.State.TWO_OF_THREE_OWNED_SAME or \
                    info.state == SetInfo.State.ONE_OF_TWO_OWNED:
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

    def deal_completed(self, dr):
        Logger.log("* Deal completed proposed by: {}; to {}; giving {} getting {} for {}".
                   format(dr.proposer.ai.get_name(),dr.proposee.ai.get_name(), dr.properties_transferred_to_proposee, dr.properties_transferred_to_proposer,
                          dr.cash_transferred_from_proposer_to_proposee), level=Logger.INFO)

    def game_over(self, winner, maximum_rounds_played):
        Logger.log("* Max deals was "+str(self.max_deals), Logger.INFO)

    def player_ran_out_of_time(self, player):
        Logger.log("* "+player.ai.get_name()+" ran out of time", Logger.DEBUG)

    def unmortgage_properties(self, game_state, me):
        sets = set()
        candidate = None
        for property in me.state.properties:
            property_set = property.property_set
            if property.is_mortgaged and candidate is None:
                candidate = property_set
            if not property_set in sets:
                info = work_out_owners(property.property_set)
                sets.add(property_set)
                if info.State == SetInfo.State.OWNED_OUTRIGHT:
                    if property_set in me.state.owned_unmortgaged_sets:
                        if property.number_of_houses < 5:
                            # we could still build on this set.
                            return
                    else:
                        candidate = property_set
        if candidate is not None:
            properties = []
            unmortgage_cost = 0
            for property in candidate.properties:
                if property.is_mortgaged and property.owner == me:
                    unmortgage_cost += int(property.mortgage_value * 1.1)
                    if unmortgage_cost > me.state.cash-self.cash_reserve:
                        if len(properties) > 0:
                            Logger.log("Unmortgaging "+str(properties), Logger.INFO)
                        return properties
                    properties.append(property)

    def eminent_domain(self, game_state, me):
        self.is_eminent_domain = True
