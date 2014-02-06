from monopyly import *

import collections
import itertools
import platform
import random
import sys

import time

LOGGING       = False
AUCTIONS_INFO = False
ASSERTING     = False


def ASSERT(condition, msg):
    if ASSERTING and not condition:
        Log('ASSERT: %s' % str(msg))


def DEBUG(msg):
    if LOGGING and 'verbose' in sys.argv:
        print(msg)


prefix = '/tmp' if platform.system() == 'Linux' else 'c:/temp'
logFile = None
try:
    if LOGGING:
        mode = 'wb' if 'clean' in sys.argv else 'ab'
        logFile = open(r'%s/Monopoly_%s.log' % (prefix, platform.node()), mode)
except:
    pass


def Log(msg=''):
    if logFile:
        logFile.write(('%s\n' % msg).encode())
    print(msg)


logResults = None
try:
    if LOGGING:
        logResults = open(r'MonopolyResults_%s.log' % (platform.node()), 'ab')
        logResults.write('\n'.encode())
except:
    pass


def LogResults(msg=''):
    if LOGGING:
        if logResults:
            logResults.write(('%s\n' % msg).encode())
            logResults.flush()
        print(msg)


class LogHandler(object):
    def __init__(self, minimum_log_level=Logger.WARNING, message_processor=None):
        self.minimum_log_level = minimum_log_level
        self.message_processor = message_processor

    def handle_log_message(self, message, level, indent_level):
        self.message_processor(message)


class BrillAI(PlayerAIBase):
    '''
    An AI that plays like a dad (or at least, similarly to how
    I play when I'm playing with my children).

    - It initially buys any properties it can.
    - It builds houses when it has complete sets.
    - It makes favourable deals with other players.
    - It keeps a small reserve of cash.
    '''
    UTILITIES = [Square.Name.ELECTRIC_COMPANY,
                 Square.Name.WATER_WORKS]

    PROPERTIES_WE_LIKE = [Square.Name.MAYFAIR,
                          Square.Name.ELECTRIC_COMPANY,
                          Square.Name.WATER_WORKS,
                          Square.Name.KINGS_CROSS_STATION,
                          Square.Name.MARYLEBONE_STATION,
                          Square.Name.FENCHURCH_STREET_STATION,
                          Square.Name.LIVERPOOL_STREET_STATION,
                          Square.Name.PARK_LANE,
                          ]
    AUCTIONS = {}

    def __init__(self):
        '''
        The 'constructor'.
        '''

        self.properties_offer_info = {'queue': [{'property_name': x, 'status': None, 'offer': 0, 'factor': 1, 'owner': None} for x in self.PROPERTIES_WE_LIKE],
                                      'processing': [], 'won': [], 'rejected': []}
        self.cash_reserve      = 500
        self.house_factor      = 1
        self.like_factor       = 3
        self.offer_factor      = 4
        self.random_factor     = 7
        self.property_factor   = 11
        self.debt_amount       = 0
        self.game_start        = time.clock()
        self.tournament_start  = time.clock()

        self.square_count      = [0] * 40
        self.square_names      = None
        self.bids              = {}
        self.in_auction        = False
        self.player_turn       = None
        self.deal_count        = 0
        self.offers_to_players = {}
        self.opponents         = []
        self.handler           = False
        self.add_handler()
        self.eminent           = False
        self.eminent_threshold = 200
        self.eminent_limit     = 100
        self.game_state        = None
        self.turns             = 0

    def get_name(self):
        '''
        Returns the name shown for this AI.
        '''
        return "Brill"

    def start_of_game(self):
        self.properties_offer_info = {'queue': [{'property_name': x, 'status': None, 'offer': 0, 'factor': 1, 'owner': None} for x in self.PROPERTIES_WE_LIKE],
                                      'processing': [], 'won': [], 'rejected': []}
        self.opponents             = []
        self.turns                 = 0
        self.game_start            = time.clock()
        self.game_state            = None

        self.eminent_start         = False

    def add_handler(self):
        def message_processor(message):
            if message.startswith('Bids: ') and len(message) > len('Bids: []'):
                bids = message.replace('Bids: ', '')
                try:
                    self.bids = {}
                    for bid in bids[2:-2].replace('), (', '#').split('#'):
                        bidder, price = bid.split(', ')
                        self.bids[bidder.strip("'")] = int(float(price))
                except Exception:
                    pass

        if not self.handler:
            self.Handler = True
            Logger.add_handler(LogHandler(message_processor=message_processor))

    def SetUp(self, config):
        self.tournament_start  = time.clock()
        self.cash_reserve      = config.get('reserve',         self.cash_reserve)
        self.house_factor      = config.get('house_factor',    self.house_factor)
        self.property_factor   = config.get('property_factor', self.property_factor)
        self.like_factor       = config.get('like_factor',     self.like_factor)
        self.offer_factor      = config.get('offer_factor',    self.offer_factor)
        self.random_factor     = config.get('random_factor',   self.random_factor)
        self.eminent_limit     = config.get('eminent_limit',   self.eminent_limit)

    def player_went_bankrupt(self, player):
        if player.name == self.get_name() and AUCTIONS_INFO:
            property_owners, property_state = {}, {}
            houses, unmortgaged             = [], []
            for player in player.board.game_state.players:
                for property in player.state.properties:
                    property_state[property.name] = {'owner': player.name, 'houses': getattr(property, 'number_of_houses', ' '),
                                                     'mortgaged': property.is_mortgaged, 'full_set':  property.property_set in player.state.owned_sets, 'unmortgaged_set': property.property_set in player.state.owned_unmortgaged_sets}
                    property_owners.update(property_state)
                    if player.name == property.owner:
                        houses.append(getattr(property, 'number_of_houses', 0))
                        unmortgaged.append(not property.is_mortgaged)
            for name, count in zip(enumerate(self.square_names), self.square_count):
                property_owner = property_owners.get(name[1].name, {'owner': '', 'houses': ' ', 'mortgaged': '', 'full_set':  '', 'unmortgaged_set': ''})
                Log('%3d, %5d %30s, %20s %s%s%s%s' % (name[0], count, name[1], property_owner['owner'],
                                                                        'S' if property_owner['full_set']        else ' ',
                                                                        'M' if property_owner['mortgaged']       else ' ',
                                                                        'U' if property_owner['unmortgaged_set'] else ' ',
                                                                            str(property_owner['houses']),
                                                                    ))
            ASSERT(not(any(houses) or any(unmortgaged)), 'House selling/Mortgaging Failure')
            Log("Gone Bankrupt")

    def game_over(self, winner, maximum_rounds_played):
        self.winner = winner
        self.maximum_rounds_played = maximum_rounds_played

        if not LOGGING:
            return

        players_info    = {}
        property_owners = {}
        players_state   = [] if winner is None else [(True, winner.board.game_state.bankrupt_players), (False, winner.board.game_state.players)]
        for bankrupt, players in players_state:
            for player in players:
                property_state = {}
                for property in player.state.properties:
                    property_state[property.name] = {'owner': player.name, 'houses': getattr(property, 'number_of_houses', ' '),
                                                     'mortgaged': property.is_mortgaged, 'full_set':  property.property_set in player.state.owned_sets, 'unmortgaged_set': property.property_set in player.state.owned_unmortgaged_sets}
                property_owners.update(property_state)
                players_info[player.name] = {'bankrupt': bankrupt, 'net_worth': player.net_worth, 'cash': player.state.cash, 'properties': [x.name for x in player.state.properties], 'sets': str(player.state.owned_sets)}

        Log('=' * 80)
        if AUCTIONS_INFO:
            for player, bids in self.AUCTIONS.items():
                Log('\n%s' % str(player))
                for property, values in bids.items():
                    Log('  %s  %4d, %.6f, %4d %s' % ('*' if values['won'] else ' ', values['price'], values['factor'], values['delta'], property))

            for name, count in zip(enumerate(self.square_names), self.square_count):
                property_owner = property_owners.get(name[1].name, {'owner': '', 'houses': ' ', 'mortgaged': '', 'full_set':  '', 'unmortgaged_set': ''})
                Log('%3d, %5d %30s, %20s %s%s%s%s' % (name[0], count, name[1], property_owner['owner'],
                                                                        'S' if property_owner['full_set']        else ' ',
                                                                        'M' if property_owner['mortgaged']       else ' ',
                                                                        'U' if property_owner['unmortgaged_set'] else ' ',
                                                                           str(property_owner['houses']),
                                                                    ))
        elapsed_time = time.clock() - self.game_start
        Log('Reserve = {0}, house = {1}, like = {2}, offer = {3}, random = {4}, turns {5}, elapsed = {6:.3f}'.format(self.cash_reserve, self.house_factor, self.like_factor, self.offer_factor, self.random_factor, self.turns, elapsed_time))

        Log()
        for player, info in sorted(players_info.items(), key=lambda x: x[1]['net_worth'], reverse=True):
            Log('%16s : net_worth = %6d, cash = %6d %s' % (player, info['net_worth'], info['cash'], 'Bankrupt' if info['bankrupt'] else ''))

        if self.eminent_start:
            Log('eminent')

    def tournament_over(self, results):
        players = ', '.join('{0} : {1}'.format(*x) for x in sorted(results, key=lambda x: x[1], reverse=True))
        elapsed_time = time.clock() - self.tournament_start
        LogResults("Ranking [ {0} ] Reserve = {1}, house = {2}, like = {3}, offer = {4}, random = {5}, elapsed = {6:.3f}{7}".format(
                   players, self.cash_reserve, self.house_factor, self.like_factor, self.offer_factor, self.random_factor, elapsed_time, ', eminent' if self.eminent else ''))

    def get_cash_reserve(self, game_state, player):
        position = player.state.square
        if not any(x.number_of_houses for x in game_state.board.squares if hasattr(x, 'number_of_houses') and x.number_of_houses):
            return self.cash_reserve / 5.0
        return self.cash_reserve / 2.0 + (self.cash_reserve * (40.0 - position) / 80.0)

    def get_cash_total(self, game_state, player):
        house_value = sum(x.house_price // 2 for x in game_state.board.squares if isinstance(x, Street))
        mortgaged_value = sum(x.mortgage_value for x in player.state.properties if not x.is_mortgaged)
        return house_value + mortgaged_value + player.state.cash

    def start_of_turn(self, game_state, player):
        self.turns += 1
        self.in_auction = False

        if self.game_state is None:
            self.game_state = game_state

        if self.square_names is None:
            self.square_names = list(game_state.board.squares)

        if not self.opponents:
            self.opponents    = [x.name for x in game_state.players if x.name != self.get_name()]
        self.player_turn = player
        self.deal_count  = 0
        self.square_count[player.state.square] += 1

    def get_out_of_jail(self, game_state, player):
        if player.state.number_of_get_out_of_jail_free_cards >= 1:
            return PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
        elif player.state.cash > self.get_cash_reserve(game_state, player):
            return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
        else:
            return PlayerAIBase.Action.STAY_IN_JAIL

    def property_for_set(self, player, game_state, property):
        owners      = [x.owner.name if x.owner else None for x in property.property_set.properties]
        owner_count = dict((x, owners.count(x)) for x in owners)
        return (owner_count, len(owners))

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property. We always buy it if we
        can while keeping a small cash reserve.
        '''
        if player.state.cash > self.get_cash_reserve(game_state, player) + property.price:
            return PlayerAIBase.Action.BUY
        elif property.name in self.PROPERTIES_WE_LIKE:
            return PlayerAIBase.Action.BUY
        else:
            buy = False
            amount = property.price - player.state.cash
            total_cash = self.get_cash_total(game_state, player)
            if (total_cash - amount) > self.cash_reserve:
                buy = True
            else:
                owner_count, total = self.property_for_set(player, game_state, property)
                owned, free = owner_count.get(player.name, 0), owner_count.get(None, 0)
                if owned + free == total and free == 1:
                    #only one set pieces free
                    buy = (total_cash - amount) > self.cash_reserve / 5
            if buy:
                return PlayerAIBase.Action.BUY
            else:
                return PlayerAIBase.Action.DO_NOT_BUY

    def propose_deal(self, game_state, player):
        '''
        We have the opportunity to propose a deal.

        If any other player has one of the properties we want, we
        offer them 2x the price for it.
        '''
        self.deal_count += 1

        # We check to see if any of the properties we like is owned
        # by another player...
        for p in self.properties_offer_info['queue']:
            p['owner'] = game_state.board.get_square_by_name(p['property_name']).owner

        for idx in range(len(self.properties_offer_info['queue'])):
            property_name = self.properties_offer_info['queue'][idx]['property_name']
            property = game_state.board.get_square_by_name(property_name)
            if property.owner is player or property.owner is None:
                # The property is either not owned, or owned by us...
                continue

            # The property is owned by another player, so we make them an
            # offer for it...

            offer = self.properties_offer_info['queue'].pop(idx)
            offer['offer'] += offer['factor'] * property.price + 1
            self.properties_offer_info['processing'].append(offer)
            return DealProposal(
                properties_wanted=[property],
                maximum_cash_offered=offer['offer'],
                propose_to_player=property.owner)

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''
        # We only accept deals for single properties wanted from us...
        if len(deal_proposal.properties_offered) > 0:
            return DealResponse(DealResponse.Action.REJECT)
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)
        if (len(deal_proposal.properties_wanted) == 1) and \
                (deal_proposal.properties_wanted[0].name in self.PROPERTIES_WE_LIKE):
            return DealResponse(DealResponse.Action.ACCEPT)

        return DealResponse(DealResponse.Action.REJECT)

    def deal_result(self, deal_info):
        for prop in self.properties_offer_info['processing']:
            prop['status'] = deal_info

        if deal_info == PlayerAIBase.DealInfo.SUCCEEDED:
            pass
        elif deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED:
            pass
        elif deal_info == PlayerAIBase.DealInfo.ASKED_FOR_TOO_MUCH_MONEY:
            pass
        elif deal_info == PlayerAIBase.DealInfo.OFFERED_TOO_LITTLE_MONEY:
            for prop in self.properties_offer_info['processing']:
                prop['factor'] += 1
                #increase factor for all properties by this owner
                for p in (x for x in self.properties_offer_info['queue'] if x['owner'] == prop['owner']):
                    p['factor'] += 1
            pass
        elif deal_info == PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY:
            pass
        elif deal_info == PlayerAIBase.DealInfo.DEAL_REJECTED:
            while self.properties_offer_info['processing']:
                prop = self.properties_offer_info['processing'].pop()
                self.properties_offer_info['rejected'].append(prop)

                #move all properties by this owner to end of queue
                prop_want, prop_reject = [], []
                for p in self.properties_offer_info['queue']:
                    if p['owner'] == prop['owner']:
                        prop_reject.append(p)
                    else:
                        prop_want.append(p)
                self.properties_offer_info['queue'] = prop_want + prop_reject
                pass

    def deal_completed(self, deal_result):
        pass

    def build_houses(self, game_state, player):
        '''
        Gives us the opportunity to build houses.
        '''
        if not [x for x in player.state.owned_unmortgaged_sets if x.can_build_houses]:
            return []

        # We find the first set we own that we can build on...
        number_of_houses = sum(x.number_of_houses for x in game_state.board.squares if isinstance(x, Street))
        free_props       = sum(1 for x in game_state.board.squares if hasattr(x, 'owner') and x.owner is None)
        owned_unmortgaged_sets = sorted((x for x in player.state.owned_unmortgaged_sets if x.can_build_houses), key=lambda x: min((n.number_of_houses, x.house_price) for n in x.properties))
        row_cost = min(x.house_price * x.number_of_properties for x in owned_unmortgaged_sets)

        if (player.state.cash > self.house_factor * self.cash_reserve
                or (player.state.cash > row_cost + self.cash_reserve / 2 and number_of_houses > 0)
                or (player.state.cash > row_cost + self.cash_reserve / 2 and free_props == 0)
                or (self.turns >= self.eminent_threshold - 1 and number_of_houses == 0)):
            total_cost     = 0
            changed        = True
            property_build = []
            house_count    = {}
            for owned_set in owned_unmortgaged_sets:
                for p in owned_set.properties:
                    house_count[p] = 0

            while player.state.cash > (self.get_cash_reserve(game_state, player) + total_cost) and changed:
                changed = False
                for owned_set in owned_unmortgaged_sets:
                    # We can't build on stations or utilities, or if the
                    # set already has hotels on all the properties...
                    if not owned_set.can_build_houses:
                        continue

                    # We see how much money we need for one house on each property...
                    cost = owned_set.house_price * owned_set.number_of_properties
                    if player.state.cash > (self.get_cash_reserve(game_state, player) + total_cost + cost):
                        for p in owned_set.properties:
                            if p.number_of_houses + house_count[p] >= 5:
                                continue
                            changed = True
                            house_count[p] += 1
                            total_cost += p.house_price
                            # We build one house on each property...
                            property_build.append((p, 1))
                        if ASSERTING:
                            houses_by_prop = collections.Counter(x[0] for x in property_build)
                            houses_for_each_property_set = [p.number_of_houses + houses_by_prop[p] for p in owned_set.properties]
                            ASSERT(max(houses_for_each_property_set) - min(houses_for_each_property_set) < 2, 'Unbalanced house build')
            if property_build:
                if ASSERTING:
                    house_by_prop = collections.Counter(x[0] for x in property_build)
                    for p, n in house_by_prop.items():
                        ASSERT(p.number_of_houses + n <= 5, 'Too Many Houses')
                return property_build
            properties = []
            for owned_set in (x for x in player.state.owned_unmortgaged_sets if x.can_build_houses):
                properties.extend(owned_set.properties)
            #build one house on cheapest property
            props_sorted = sorted((x for x in properties if x.number_of_houses < 5), key=lambda x: x.house_price)
            if props_sorted and number_of_houses == 0:
                return [(props_sorted[0], 1)]
        # We can't build...
        return []

    def property_offered_for_auction(self, game_state, player, property):
        '''
        We offer the face value multiplied by dynamic factor in auctions.
        '''
        self.in_auction = True

        ASSERT(player is not None, 'player is None')

        bids           = sorted(x.get(property.name, {}).get('factor', 0) for x in (self.AUCTIONS.get(bidder, {}) for bidder in self.opponents))
        if bids[-1] > 0:
            pass
        bid_factor     = abs(max(bids))
        if bid_factor <= 0:
            bid_all    = [0]
            for prop_info in itertools.chain(x[1] for x in self.AUCTIONS.items() if x[0] in self.opponents):
                for f in list(prop_info.values()):
                    bid_all.append(f.get('factor', 0))
            bid_factor = abs(max(bid_all))
            bid_factor = bid_factor if bid_factor > 0 else self.property_factor / 10

        owner_count, total = self.property_for_set(player, game_state, property)
        owned = owner_count.get(player.name, 0)
        free  = owner_count.get(None, 0)
        available_cash       = self.get_cash_total(game_state, player) - self.cash_reserve // 2
        total_property_price = sum(x.price for x in game_state.board.squares if hasattr(x, 'owner') and x.owner is None)
        total_factor         = 1 + (available_cash / total_property_price)

        if self.eminent_start:
            amount_offered = int(property.price * total_factor) + random.randint(0, property.price)
            if owned > 0:
                pass
            elif free == 1:
                amount_offered * 3
            elif player.net_worth > 3 * self.cash_reserve:
                pass
            elif player.net_worth > 2 * self.cash_reserve:
                amount_offered = property.price + random.randint(0, property.price // 10)
            elif player.net_worth > self.cash_reserve:
                amount_offered = property.price // 2 + random.randint(0, property.price // 10)
            else:
                amount_offered = player.net_worth // 10
            return amount_offered
        else:
            amount_offered = int(property.price * self.property_factor / 10)
            bid_offered    = int(bid_factor * property.price)
            owned_set      = [x for x in player.state.owned_unmortgaged_sets if x.can_build_houses]

            if owned + free == total and free == 1:
                self.in_auction = not isinstance(property, Street)
                return available_cash if len(owned_set) == 0 else available_cash - self.cash_reserve // 2
            elif owned > 0:
                pass
            elif free == 1:
                return available_cash - self.cash_reserve // 2
            elif property.name in self.PROPERTIES_WE_LIKE and player.state.cash > self.like_factor * self.cash_reserve:
                amount_offered = random.randint(0, property.price) + amount_offered * 2
            elif bid_offered > player.state.cash:
                return bid_offered - 1
            else:
                amount_offered += random.randint(-property.price // 20, property.price // self.random_factor)
            max_bid = int(property.price * total_factor) + random.randint(0, property.price)
            return max(amount_offered, bid_offered, max_bid)

    def auction_result(self, status, property, player, amount_paid):
        self.in_auction = False

        if property is None:
            return

        for bidder, bid in self.bids.items():
            self.AUCTIONS.setdefault(bidder, {})[property.name] = {'price': property.price, 'bid': bid, 'factor': float(bid) / property.price, 'delta': (bid - property.price), 'won': bidder == player.name}

    def money_will_be_taken(self, player, amount):
        DEBUG('money_will_be_taken(%d)' % amount)
        self.debt_amount = amount

    def sell_houses(self, game_state, player):
        if self.debt_amount < player.state.cash or self.in_auction:
            DEBUG('sell_houses CASH %s, %s' % (player.state.cash, repr(self.in_auction)))
            return []
        else:
            pass
        amount = 0
        houses = []

        if not player.state.owned_unmortgaged_sets:
            DEBUG('sell_houses NO SETS %s, %s' % (player.state.cash, repr(self.in_auction)))
            return houses

        store = {}
        for owned_set in (x for x in player.state.owned_unmortgaged_sets if x.can_build_houses):
            store.update(dict((x.name, [x, x.number_of_houses]) for x in owned_set.properties))

        flag = True
        while flag:
            flag = False
            for owned_set in (x for x in player.state.owned_unmortgaged_sets if x.can_build_houses):
                for p in sorted(owned_set.properties, key=lambda x: x.number_of_houses, reverse=True):
                    if store[p.name][1] > 0:
                        flag = True
                        store[p.name][1] -= 1
                        amount += p.house_price // 2
                        houses += [(p, 1)]
                        if player.state.cash + amount > self.debt_amount:
                            if ASSERTING:
                                houses_by_prop = collections.Counter(x[0] for x in houses)
                                for k, v in houses_by_prop.items():
                                    if v > k.number_of_houses:
                                        ASSERT(v <= k.number_of_houses, 'Selling Too many houses %d > %d' % (v, k.number_of_houses))
                                houses_for_each_property_set = [p.number_of_houses - houses_by_prop[p] for p in owned_set.properties]
                                ASSERT(max(houses_for_each_property_set) - min(houses_for_each_property_set) < 2, 'Unbalanced house selling')
                            DEBUG('sell_houses SELL %s, %s' % (player.state.cash, repr(houses)))
                            return houses
        DEBUG('sell_houses RET %s, %s, %d' % (player.state.cash, repr(self.in_auction), self.debt_amount))
        return houses

    def mortgage_properties(self, game_state, player):
        properties = []
        amount     = 0
        owned_sets = [x.name for s in player.state.owned_sets for x in s.properties]

        if self.debt_amount < player.state.cash or self.in_auction:
            DEBUG('mortgage_properties CASH %s, %s' % (player.state.cash, repr(self.in_auction)))
            return properties

        for property in player.state.properties:
            if property.name in self.UTILITIES or property.is_mortgaged or property.name in owned_sets:
                continue
            properties.append(property)
            amount += property.mortgage_value
            if player.state.cash + amount > self.debt_amount:
                DEBUG('mortgage_properties PROPERTIES %s, %s, %d, %d' % (player.state.cash, repr(properties), self.debt_amount, amount))
                return properties

        for property in (x for x in player.state.properties if x.name in self.UTILITIES and not x.is_mortgaged):
            properties.append(property)
            amount += property.mortgage_value
            if player.state.cash + amount > self.debt_amount:
                DEBUG('mortgage_properties UTILITIES %s, %s' % (player.state.cash, repr(properties)))
                return properties

        sorted_property_sets = sorted((x for x in player.state.properties if x.name in owned_sets and not x.is_mortgaged), key=lambda x: x.mortgage_value, reverse=True)
        for property in sorted_property_sets:
            properties.append(property)
            amount += property.mortgage_value
            if player.state.cash + amount > self.debt_amount:
                DEBUG('mortgage_properties SETS %s, %s' % (player.state.cash, repr(properties)))
                return properties

        DEBUG('mortgage_properties ALL %s, %s' % (player.state.cash, repr(properties)))
        return properties

    def money_taken(self, player, amount):
        if player.state.cash < 0:
            DEBUG('Not Enough Cash %d' % amount)

    def unmortgage_properties(self, game_state, player):
        if player.state.cash < self.cash_reserve:
            return
        properties_to_unmortgage = []
        amount = player.state.cash - self.cash_reserve
        mortgaged_properties = sorted((x for x in player.state.properties if x.is_mortgaged), key=lambda x: x.mortgage_value)
        while amount > 0 and mortgaged_properties:
            property = mortgaged_properties.pop()
            if property.mortgage_value < amount:
                amount -= property.mortgage_value
                properties_to_unmortgage.append(property)
        return properties_to_unmortgage

    def players_birthday(self):
        return "Happy Birthday!"

    def player_landed_on_square(self, game_state, square, player):
        pass

    def money_given(self, player, amount):
        pass

    def eminent_domain(self, game_state, player):
        self.eminent_start = True

    def ai_error(self, message):
        '''
        Called if the return value from any of the Player AI functions
        was invalid. for example, if it was not of the expected type.

        No response is required.
        '''
        Log('Error: ' + message)
        pass
