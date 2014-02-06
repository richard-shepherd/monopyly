from monopyly import *
from collections import deque
import operator
import time

class DarkGreenLightAI(PlayerAIBase):

    SELL_PARM1 = 0.15
    SELL_PARM2 = 1.00
    SELL_PARM3 = 1.00
    SELL_PARM4 = 1.00
    BUY_PARM1 = 0.15
    BUY_PARM2 = 1.00
    BUY_PARM3 = 2.00
    BUY_PARM4 = 0.50
    BID_PARM1 = 0.15
    BID_PARM2 = 1.00
    BID_PARM3 = 2.00
    BID_PARM4 = 0.80

    MAX_BUY_PARM_FAC = 130
    MIN_BUY_PARM_FAC = 70
    MAX_BID_PARM_FAC = 130
    MIN_BID_PARM_FAC = 80
    BID_PARM_INC_UNIT = 20
    MAX_BID_PARM_DEC_UNIT = 5
    MAX_HOLDOUT_FAC = 300
    MIN_HOLDOUT_FAC = 120
    HOLDOUT_ADJUST_UNIT = 30
    HOLDOUT_BID_RATIO = 70
    HOLDOUT_BIG_FAC = 1000000

    NOT_GONNA_HAPPEN = 0.0010
    BARELY_HAPPENS = 0.010
    # for second_cash_reserve
    MIGHT_HAPPEN = 0.05556
    RISK_AVRG_FACTOR = 12.0

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.color_preferred = ["Orange", "Light blue", "Purple", "Brown"]
        # self.color_non_preferred = ["Yellow", "Dark blue", "Red", "Green"]
        self.dice_probabilities = [0.00000, 0.00000, 0.02778, 0.05556, 0.08410, 0.11265, 0.14198, 0.17130, 0.14583
                                 , 0.12037, 0.09414, 0.06790, 0.04090, 0.01389, 0.01389, 0.01389, 0.01312, 0.01235
                                 , 0.01080, 0.00926, 0.00694, 0.00463, 0.00309, 0.00154, 0.00077]
        # Data needed to stay throughout the tournament
        # regarding deal propose
        self.is_buy_parm_fac_init = False
        self.buy_parm_fac = {}
        self.is_players_bid_db_init = False
        self.players_bid_db = {}
        self.is_blacklist_init = False
        self.blacklist = {}
        self.game_count = 0

        # data refreshed every game ====================
        self.start_number = -1
        self.late_add = 0
        self.turn = 0
        self.phase = 0
        self.risk_avrg = 0
        self.cash_reserve = 300
        self.cash_reserve_reliability = 0.0
        self.second_cash_reserve = 300
        self.total_properties_owned = 0
        self.last_deal_received = DealProposal
        self.last_ppty_offered = deque('',2)
        self.last_10_deals_proposed = deque('',10)
        self.money_taking_moment = False
        self.money_taking_amount = 0

        self.property_wish_list = []
        del self.property_wish_list[0:len(self.property_wish_list)]
        self.property_to_mortgage_list = []
        del self.property_to_mortgage_list[0:len(self.property_to_mortgage_list)]
        self.to_build_list = []
        del self.to_build_list[0:len(self.to_build_list)]
        self.landing_cost_list = []
        del self.landing_cost_list[0:len(self.landing_cost_list)]

        self.has_just_proposed = False
        self.last_deal_proposed_to = ""

        self.buy_quote_amount = 0
        self.bid_parm_fac = 100
        self.has_just_bid = False
        self.bid_quote_amount = 0
        self.bid_evp = 0
        self.fake_bid = False

        self.has_just_holdout_bid = False        
        self.holdout_mb = 0
        self.holdout_mh = 0
        self.holdout_ph = 0
        self.holdout_p = None
        self.holdout_snatch = 0

        # self.players_cash = {}

    def get_name(self):
        return "DarkGreenLight"

    def init_for_new_game(self):

        # data refreshed every game ====================
        self.start_number = -1
        self.late_add = 0
        self.turn = 0
        self.phase = 0
        self.risk_avrg = 0
        self.cash_reserve = 300
        self.cash_reserve_reliability = 0.0
        self.second_cash_reserve = 300
        self.total_properties_owned = 0
        self.last_deal_received = DealProposal
        self.last_ppty_offered = deque('',2)
        self.last_10_deals_proposed = deque('',10)
        self.money_taking_moment = False
        self.money_taking_amount = 0

        self.property_wish_list = []
        del self.property_wish_list[0:len(self.property_wish_list)]
        self.property_to_mortgage_list = []
        del self.property_to_mortgage_list[0:len(self.property_to_mortgage_list)]
        self.to_build_list = []
        del self.to_build_list[0:len(self.to_build_list)]
        self.landing_cost_list = []
        del self.landing_cost_list[0:len(self.landing_cost_list)]

        self.has_just_proposed = False
        self.last_deal_proposed_to = ""

        self.buy_quote_amount = 0
        self.bid_parm_fac = 100
        self.has_just_bid = False
        self.bid_quote_amount = 0
        self.bid_evp = 0
        self.fake_bid = False

        self.has_just_holdout_bid = False
        self.holdout_mb = 0
        self.holdout_mh = 0
        self.holdout_ph = 0
        self.holdout_p = None
        self.holdout_snatch = 0

        # self.players_cash = {}

    def start_of_game(self):
        self.init_for_new_game()
        self.game_count += 1

    def buy_parm_fac_init(self, game_state):
        log_level = Logger.DEBUG
        Logger.log("buy_parm_fac_init called", log_level)
        self.buy_parm_fac.clear()
        self.buy_parm_fac = {p.name: 100 for p in game_state.players}
        self.is_buy_parm_fac_init = True

    def players_bid_db_init(self, game_state):
        log_level = Logger.DEBUG
        Logger.log("players_bid_db_init called", log_level)
        self.players_bid_db.clear()
        tuple = (100, 100, 100, 100, self.HOLDOUT_BIG_FAC)
        self.players_bid_db = {p.name: tuple for p in game_state.players}
        self.is_players_bid_db_init = True

    def blacklist_init(self, game_state):
        log_level = Logger.DEBUG
        Logger.log("blacklist_init called", log_level)
        self.blacklist.clear()
        tuple = (0, 0)
        self.blacklist = {p.name: tuple for p in game_state.players}
        self.is_blacklist_init = True

    def start_of_turn(self, game_state, player):
        log_level = Logger.INFO
        if self.turn == 0:

            if not self.is_buy_parm_fac_init:
                self.buy_parm_fac_init(game_state)
            if not self.is_players_bid_db_init:
                self.players_bid_db_init(game_state)
            if not self.is_blacklist_init:
                self.blacklist_init(game_state)

            for p in game_state.players:
                if p.name not in self.buy_parm_fac:
                    self.buy_parm_fac[p.name] = 100
                if p.name not in self.players_bid_db:
                    self.players_bid_db[p.name] = (100, 100, 100, 100, 200)
                if p.name not in self.blacklist:
                    self.blacklist[p.name] = (0, 0)

            db_check_log_level = Logger.INFO
            Logger.log("=== DBCHECK ========================================", db_check_log_level)
            for key, value in self.buy_parm_fac.items():
                Logger.log("[{:20s}] : {}".format(key, value), db_check_log_level)
            for key, value in self.players_bid_db.items():
                Logger.log("[{:20s}] : {}".format(key, value), db_check_log_level)
            for key, value in self.blacklist.items():
                Logger.log("[{:20s}] : {}".format(key, value), db_check_log_level)

        self.turn += 1
        if player.name == self.get_name():

            if self.start_number < 0:
                self.start_number = self.turn
                if self.start_number > 2:
                    self.late_add = 1
                else:
                    self.late_add = 0

            # Refresh Phase and Cash_reserve
            self.get_phase(game_state)

            # Update lists
            # eval ppty that others own
            self.update_property_wish_list(game_state, player)
            # eval ppty that I own
            self.update_to_mortgage_list(player)
            self.update_to_build_list(player)
            self.update_cash_reserve(game_state, player)
            # self.update_players_cash(game_state)


            # Logger.log("cash_reserve_of_this_turn: ${}({}%)".format(self.cash_reserve, self.cash_reserve_reliability), log_level)
            # Display info on game status
            Logger.log("=============[G:{}]({}) Turn {} (Phase{}) @{}===============".format(self.game_count, self.start_number, int(self.turn/4 + 1), self.get_phase(game_state), game_state.board.get_square_by_index(player.state.square).name), log_level)
            # GameState->Players[]->PlayerState->Properties[]
            for temp_player in game_state.players:
                Logger.log("# {} @{}({}) - [hv:${}][nw:${}][anw:${}] : {}"
                .format(temp_player.name, game_state.board.get_square_by_index(temp_player.state.square).name
                    , temp_player.state.square, temp_player.state.cash, temp_player.net_worth
                    , self.get_available_net_worth(temp_player), len(temp_player.state.properties)), log_level)
                if len(temp_player.state.owned_sets) > 0:
                    for temp_ppty_set in temp_player.state.owned_sets:
                        Logger.log("[{}]".format(temp_ppty_set.set_enum), log_level)

                Logger.indent()
                for temp_property in temp_player.state.properties:
                    number_of_houses = 0
                    if isinstance(temp_property, Street):
                        number_of_houses = temp_property.number_of_houses
                    Logger.log("[{:25s}][{:12s}][p:${:3}][h:${:3}][h:{:2d}][r:${:4d}]<{}>".format(temp_property.name, temp_property.property_set
                        , temp_property.price, temp_property.property_set.house_price ,number_of_houses
                        , self.calculate_property_rent(temp_property, game_state), temp_property.is_mortgaged), log_level)
                Logger.dedent()

    def update_cash_reserve(self, game_state, current_player):
        log_level = Logger.DEBUG
        did_get_first_cash_reserve = False
        did_get_second_cash_reserve = False

        self.update_landing_cost_list(game_state, current_player)
        # max_cost_tuple = [x[0] for x in self.landing_cost_list]
        if self.risk_avrg < 0:
            self.risk_avrg = 0
        # Logger.log("Cost_sum : {} / avrg : {}".format(cost_sum, cost_average))
        for i, e in enumerate(self.landing_cost_list):
            self.cash_reserve = -1
            if e[1] < self.NOT_GONNA_HAPPEN:
                continue
            elif e[1] <= self.BARELY_HAPPENS and e[0] >= (self.risk_avrg * self.RISK_AVRG_FACTOR):
                continue
            else:
                if e[0] > 0:
                        self.cash_reserve = e[0]
                        self.cash_reserve_reliability = e[1]
                else:
                        self.cash_reserve = 0
                        self.cash_reserve_reliability = e[1]

                Logger.log("$$ Updated Cash_reserve : {}) ${} {}% [d:{}] ({}[{}] -> {}[{}])"
                    .format(i+1, self.cash_reserve, round(self.cash_reserve_reliability * 100, 3), e[2]
                    , game_state.board.get_square_by_index(current_player.state.square).name
                    , current_player.state.square
                    , game_state.board.get_square_by_index(self.get_next_position(current_player.state.square, e[2])).name
                    , self.get_next_position(current_player.state.square, e[2])), log_level)
                break

        # getting second reserve
        for i, e in enumerate(self.landing_cost_list):
            self.second_cash_reserve = -1
            if e[1] < self.NOT_GONNA_HAPPEN:
                continue
            elif e[1] <= self.MIGHT_HAPPEN:
                continue
            elif e[0] == self.cash_reserve and e[1] == self.cash_reserve_reliability:
                continue
            else:
                if e[0] > 0:
                        self.second_cash_reserve = e[0]
                else:
                        self.second_cash_reserve = 0
                break

        Logger.log("Second Cash Reserve : ${}".format(self.second_cash_reserve),log_level)

        if self.cash_reserve == -1:
            self.cash_reserve = self.get_phase(game_state) * 100 + 100
            self.cash_reserve_reliability = 1
            Logger.log("Can't happen (Cash_Reserve)", Logger.DEBUG)
        if self.second_cash_reserve == -1:
            self.second_cash_reserve = self.get_phase(game_state) * 100 + 100
            Logger.log("Can't happen (second_Cash_Reserve)", Logger.DEBUG)

    def update_landing_cost_list(self, game_state, me):
        log_level = Logger.DEBUG
        del self.landing_cost_list[0:len(self.landing_cost_list)]
        cur_sq_idx = me.state.square
        Logger.log("///////////// Get cash_reserve from this Sqare [{}]({})/////////////// "
                 .format(game_state.board.get_square_by_index(cur_sq_idx), cur_sq_idx), log_level)
        for x in range(2, 25):
            dest_sq_idx = self.get_next_position(cur_sq_idx, x)
            self.estimate_landing_cost(game_state, me, cur_sq_idx, dest_sq_idx, round(self.dice_probabilities[x], 5), x, 0)
        self.landing_cost_list.sort(key=operator.itemgetter(0), reverse=True)
        # Logger.log("///////////// Result /////////////////", log_level)
        temp_sum = 0
        risk_avrg = 0
        # last_i = 0
        for i, e in enumerate(self.landing_cost_list):
            if i < 10:
                Logger.log("{}) ${} {}% [d:{}][{}]".format(i+1, e[0], round(e[1] * 100, 5), e[2]
                        ,game_state.board.get_square_by_index(self.get_next_position(me.state.square, e[2])).name), log_level)

            temp_sum += e[1]
            if e[0] > 0:
                risk_avrg += e[0] * e[1]
            # last_i = i

        Logger.log("% sum {}, risk avrg {}".format(temp_sum, risk_avrg), log_level)
        self.risk_avrg = risk_avrg

    def estimate_landing_cost(self, game_state, me, cur_sq_idx, dest_sq_idx, probability, dice_num, cur_cost):
        log_level = Logger.DEBUG
        # for each case, only consider worst case - the biggest amount that I should pay
        # as this all is to get cash_reserve for next dice rolling

        # cur_sq = game_state.board.get_square_by_index(cur_sq_idx)
        dest_sq = game_state.board.get_square_by_index(dest_sq_idx)
        cost = cur_cost
        Logger.indent()
        Logger.indent()
        # if passing Go, gets $200
        if cur_sq_idx > dest_sq_idx :
            cost += -200

        if isinstance(dest_sq, Property):
            rent = self.calculate_property_rent_i_should_pay(dest_sq, game_state, me)
            self.landing_cost_list.append((cost + rent, probability, dice_num))
            Logger.log("[LC] Ppty - rent for {} :${} {}% [d:{}] [Cur:{} Dest:{}]".format(dest_sq.name, cost + rent, probability * 100 ,dice_num, cur_sq_idx, dest_sq_idx), log_level)

        elif isinstance(dest_sq, CommunityChest):
            # The worst case is either paying 100 as fine or rent for OLD_KENT_ROAD
            # Receive money (8 of 16) 20 / 50 / 30 / 25 / 10 / 200 / 100 / 100
            self.landing_cost_list.append((cost - 20, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 50, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 30, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 25, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 10, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 200, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 100, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 100, probability * 0.0625, dice_num))
            # Pay Money (4 of 16) incl 'pay 10 or take chance' as I always pay 10
            self.landing_cost_list.append((cost + 100, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost + 50, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost + 50, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost + 10, probability * 0.0625, dice_num))
            # Get 'get out of jail' card (1 of 16)
            self.landing_cost_list.append((cost, probability * 0.0625, dice_num))
            # Go to Jail
            if self.get_phase(game_state) < 2 and me.state.number_of_get_out_of_jail_free_cards == 0:
                self.landing_cost_list.append((cost + 50, probability * 0.0625, dice_num))
            else:
                self.landing_cost_list.append((cost, probability * 0.0625, dice_num))
            # Advance to Go from CommunityChest sq
            self.landing_cost_list.append((cost - 200, probability * 0.0625, dice_num))

            # Go back to OLD_KENT_ROAD -> Recursive Call
            # Need to add 200 as it will be getting 200 passing GO, although it's going 'back'
            self.estimate_landing_cost(game_state, me, dest_sq_idx
                    , game_state.board.get_index(Square.Name.OLD_KENT_ROAD), probability * 0.0625, dice_num, cost + 200)

            Logger.log("[LC] CmunityChest {}% [d:{}] [Cur:{} Dest:{}]".format(probability * 0.0625 * 100, dice_num, cur_sq_idx, dest_sq_idx), log_level)

        elif isinstance(dest_sq, Chance):
            # Receive Money (3 of 16)
            self.landing_cost_list.append((cost - 30, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 100, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost - 150, probability * 0.0625, dice_num))
            # Pay Money (3 of 16)
            self.landing_cost_list.append((cost + 30, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost + 100, probability * 0.0625, dice_num))
            self.landing_cost_list.append((cost + 150, probability * 0.0625, dice_num))
            # Repair Cost #1 (40 /115)
            self.landing_cost_list.append((cost + self.calculate_repair_cost(game_state, me, 40, 115), probability * 0.0625, dice_num))
            Logger.log("[LC] Chance - repair cost :${} {}% [d:{}] [Cur:{} Dest:{}]".format(cost + self.calculate_repair_cost(game_state, me, 40, 115), probability * 0.0625 * 100, dice_num, cur_sq_idx, dest_sq_idx), log_level)
            # Repair Cost #2 (25 /100)
            self.landing_cost_list.append((cost + self.calculate_repair_cost(game_state, me, 25, 100), probability * 0.0625, dice_num))
            Logger.log("[LC] Chance - repair cost :${} {}% [d:{}] [Cur:{} Dest:{}]".format(cost + self.calculate_repair_cost(game_state, me, 25, 100), probability * 0.0625 * 100, dice_num, cur_sq_idx, dest_sq_idx), log_level)
            # Get 'get out of jail' card (1 of 16)
            self.landing_cost_list.append((cost, probability * 0.0625, dice_num))

            # AdvanceTo Card (4 of 16)
            for temp_sq in (game_state.board.get_square_by_name(Square.Name.MAYFAIR)
                            , game_state.board.get_square_by_name(Square.Name.TRAFALGAR_SQUARE)
                            , game_state.board.get_square_by_name(Square.Name.MARYLEBONE_STATION)
                            , game_state.board.get_square_by_name(Square.Name.PALL_MALL) ):

                self.estimate_landing_cost(game_state, me, dest_sq_idx
                    , game_state.board.get_index(temp_sq.name), probability * 0.0625, dice_num, cost)

            # for chance card GoBackThreeSpaces
            # 3 cases : INCOME TAX / VINE STREET / COMMUNITY CHEST
            temp_sq = game_state.board.get_square_by_index(self.get_next_position(dest_sq_idx, -3))
            self.estimate_landing_cost(game_state, me, dest_sq_idx
                    , game_state.board.get_index(temp_sq.name), probability * 0.0625, dice_num, cost)

            # Go to Jail
            if self.get_phase(game_state) < 2 and me.state.number_of_get_out_of_jail_free_cards == 0:
                self.landing_cost_list.append((cost + 50, probability * 0.0625, dice_num))
            else:
                self.landing_cost_list.append((cost, probability * 0.0625, dice_num))
            # Go to Go
            self.landing_cost_list.append((cost - 200, probability * 0.0625, dice_num))

            # Logger.log("calc_money(Chance): repair_cost:{} / pay_skool: ${} /  max_rent:{} - final:${} {}% [d:{}]".format(repair_cost, pay_school, max_rent, tuple[0], tuple[1]*100))
        elif isinstance(dest_sq, Tax):
            if dest_sq.name == Square.Name.SUPER_TAX:
                cost += 100
            else:
                cost += 200

            self.landing_cost_list.append((cost, probability, dice_num))
            Logger.log("[LC] Tax :${} {}% [d:{}]".format(cost , probability * 100, dice_num), log_level)
        elif isinstance(dest_sq, Jail) or isinstance(dest_sq, GoToJailSquare):
            if self.get_phase(game_state) < 2 and me.state.number_of_get_out_of_jail_free_cards == 0:
                cost += 50
            self.landing_cost_list.append((cost, probability, dice_num))
        else:
            self.landing_cost_list.append((cost, probability, dice_num))

        # elif isinstance(dest_sq, Go):
        # elif isinstance(dest_sq, FreeParking):
        Logger.dedent()
        Logger.dedent()

    def get_next_position(self, current_position, num_of_squares):
        destination_position = current_position + num_of_squares
        if destination_position > 39:
            destination_position -= 40
        elif destination_position < 0:
            destination_position += 40

        return destination_position

    def get_phase(self, game_state):
        # TBI
        # GameState->Players[]->PlayerState->Properties[]

        cnt = 0
        for temp_player in game_state.players:
            cnt += len(temp_player.state.properties)

        self.total_properties_owned = cnt
        if self.total_properties_owned < 15:
            self.phase = 0
            return self.phase
        elif self.total_properties_owned < 20:
            self.phase = 1
            return self.phase
        elif self.total_properties_owned < 25:
            self.phase = 2
            return self.phase
        elif self.total_properties_owned < 28:
            self.phase = 3
            return self.phase
        else:
            self.phase = 4
            return self.phase

    def calculate_property_rent_i_should_pay(self, ppty, game_state, me):
        if not (ppty.owner is None or me.owns_properties([ppty])):
            if isinstance(ppty, Street):
                return self.calculate_street_rent(ppty)
            elif isinstance(ppty, Station):
                return self.calculate_station_rent(ppty, game_state)
            elif isinstance(ppty, Utility):
                return self.calculate_utility_rent(ppty, game_state)
            else:
                Logger.log("Can't happen1-1", Logger.DEBUG)
                return 0
        else:
            return 0

    def calculate_property_rent(self, ppty, game_state):
        if isinstance(ppty, Street):
            return self.calculate_street_rent(ppty)
        elif isinstance(ppty, Station):
            return self.calculate_station_rent(ppty, game_state)
        elif isinstance(ppty, Utility):
            return self.calculate_utility_rent(ppty, game_state)
        else:
            Logger.log("Can't happen1-2", Logger.DEBUG)
            return 0

    def calculate_street_rent(self, street):
        if street.number_of_houses == 0:
            rent = street.rents[0]
            owner = street.owner
            if street.property_set in owner.state.owned_unmortgaged_sets:
                # The player owns the whole set, so the rent is doubled...
                rent *= 2
        else:
            # The street has houses, so we find the rent for the number
            # of houses there are...
            rent = street.rents[street.number_of_houses]

        return rent

    def calculate_station_rent(self, station, game_state):
        board = game_state.board
        owned_stations = board.get_property_set(PropertySet.STATION).intersection(station.owner.state.properties)
        number_of_owned_stations = len(owned_stations)

        if number_of_owned_stations == 1:
            return 25
        elif number_of_owned_stations == 2:
            return 50
        elif number_of_owned_stations == 3:
            return 100
        elif number_of_owned_stations == 4:
            return 200
        return 0

    def calculate_utility_rent(self, util, game_state):
        board = game_state.board
        owned_utilities = board.get_property_set(PropertySet.UTILITY).intersection(util.owner.state.properties)
        number_of_owned_utilities = len(owned_utilities)

        if number_of_owned_utilities == 1:
            return 4 * 12
        elif number_of_owned_utilities == 2:
            return 10 * 12

        return 0

    def calculate_repair_cost(self, game_state, current_player, house_repair_cost, hotel_repair_cost):

        number_of_houses, number_of_hotels = current_player.state.get_number_of_houses_and_hotels(game_state.board)
        amount = house_repair_cost * number_of_houses + hotel_repair_cost * number_of_hotels

        # Logger.log("{0} has been assessed for street repairs".format(current_player.name))
        # Logger.indent()
        return amount

    def get_color_preference(self, color):
        # preferred color
        if color == "Orange":
            return 8
        elif color == "Light blue":
            return 7
        elif color == "Purple":
            return 6
        elif color == "Brown":
            return 5
        # non-preferred color
        elif color == "Yellow":
            return 4
        elif color == "Dark blue":
            return 3
        elif color == "Red":
            return 2
        elif color == "Green":
            return 1
        else:
            Logger.log("Can't Happen - Color Pref", Logger.DEBUG)
            return 0

    def get_max_cash_of_other_players(self, players):
        max_cash = 0
        for p in players:
            if p.name == self.get_name():
                continue
            max_cash = max(p.state.cash, max_cash)
        return max_cash

    # eval ppty no one owns
    def evaluate_unowned_property(self, player, ppty, property_set):
        log_level = Logger.DEBUG
        # 1 = Never Buy
        # 2 = Better not Buy (Pay Less)
        # 3 = Okay to Buy (Facing Value)
        # 4 = Better Buy (Pay More)
        # 5 = Must Buy at any cost
        if property_set.set_enum == "Utility":
            eval_point = 2
        elif property_set.set_enum == "Station":
            number_of_owned_stations = 0
            for temp_ppty in player.state.properties:
                if isinstance(temp_ppty, Station):
                    number_of_owned_stations += 1

            if number_of_owned_stations < 2:
                eval_point = 4
                Logger.log("u0) I have less than 2 stations (0~1) [{}] : evp:{}".format(number_of_owned_stations, eval_point), log_level)
            else:
                eval_point = 5
                Logger.log("u0) I have more than 1 stations (2~4) [{}] : evp:{}".format(number_of_owned_stations, eval_point), log_level)
        # The case are roughly 3, based on how many ppty are aldy owned in the CSet
        # Case1 : if no ppty is owned in the CSet
        else:
            owner_me = None
            for i, e in enumerate(property_set.owners):
                if e[0].name == player.name:
                    owner_me = property_set.owners[i]
            if property_set.number_of_owned_properties == 0:
                Logger.log("u1)1: better  buy it's owned by no one", log_level)
                eval_point = 3
            # Case2 : only 1 ppty is owned in the CSet
            elif property_set.number_of_owned_properties == 1:
                # Case2-1 : if I own the ppty, buy
                if owner_me is not None:
                    # Case2-1-1 : I can complete monopoly
                    if property_set.number_of_properties == 2:
                        Logger.log("u2) 2-1-1: So I must buy {} as I have 1 of 2".format(ppty.name), log_level)
                        eval_point = 5
                    else:
                        Logger.log("u3) 2-1-2: So I better buy {} as I have 1 of 3".format(ppty.name), log_level)
                        eval_point = 4
                # Case2-2 : if another owns the ppty
                else:
                    # Case2-2-1 : if 1 of 2 is taken by a player, buy to keep him from monopoly
                    if property_set.number_of_properties == 2:
                        Logger.log("u4) 2-2-1: okay to  buy {} to stop monopoly (1 of 2)".format(ppty.name), log_level)
                        eval_point = 2
                    # Case2-2-2 : if it's 1 of 3, okay to buy
                    else:
                        Logger.log("u5) 2-2-2: better not buy {} bcs another owns 1 of 3".format(ppty.name), log_level)
                        eval_point = 2
            # Case3 : When 2 ppty is owned in the CSet
            elif property_set.number_of_owned_properties == 2:
                # case3-1 : 1 player owns 2 ppty
                if len(property_set.owners) == 1:
                    # case3-1-1 : if I own the 2 ppty, must buy
                    if owner_me is not None:
                        Logger.log("u6) 3-1-1: I must buy {} as I've got 2 of 3 ".format(ppty.name), log_level)
                        eval_point = 5
                    else:
                        # if another owns the 2 ppty,  better buy to stop monopoly
                        Logger.log("u7) 3-1-2: ok to  buy {} to stop monopoly".format(ppty.name), log_level)
                        eval_point = 2
                # case3-2 : 2 player each own 1 ppty
                elif len(property_set.owners) == 2:
                    # case3-2-1 : If I'm one of them
                    if owner_me is not None:
                        Logger.log("u8) 3-2-1: okay 2  buy {} to make 2 of 3 ".format(ppty.name), log_level)
                        eval_point = 3
                    # Case3-2-2 : If not
                    else:
                        Logger.log("u9) 3-2-2: better not buy {} bcs others own 2 of 3".format(ppty.name), log_level)
                        eval_point = 2
                else:
                    Logger.log("Can't Happen1-3", Logger.DEBUG)
                    eval_point = 9
            else:
                Logger.log("Can't Happen1-4", Logger.DEBUG)
                eval_point = 9

            eval_point += (0.1 * self.get_color_preference(property_set.set_enum))

        return eval_point

    # for buying other p's ppty
    def update_property_wish_list(self, game_state, player):
        log_level = Logger.DEBUG
        # 1 = Never Get
        # 2 = Better not Get
        # 3 = Okay to Get (paying some premium)
        # 4 = Better Get (paying big premium) one more for monopoly)
        # 5 = Must Get at any cost (when : I can finish monopoly)

        # Clear List
        del self.property_wish_list[0:len(self.property_wish_list)]

        eval_point = 0
        for p in game_state.players:
            # Skip if the player is myself
            if p.name == player.name:
                continue

            for ppty in p.state.properties:
                # Logger.log("[{}] owns {}".format(p.name, ppty.name))
                owner_me = None
                for x in ppty.property_set.owners:
                    if x[0].name == player.name:
                        owner_me = x
                if ppty.property_set.set_enum == "Utility":
                    eval_point = 2
                    Logger.log("Util: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                elif ppty.property_set.set_enum == "Station":
                    number_of_owned_stations = 0
                    for temp_ppty in player.state.properties:
                        if isinstance(temp_ppty, Station):
                            number_of_owned_stations += 1

                    if number_of_owned_stations < 2:
                        eval_point = 4
                        Logger.log("0) [] {} have less than 2 stations (0~1) : [{}] evp:{}".format(ppty.name, player.name, number_of_owned_stations, eval_point), log_level)
                    else:
                        eval_point = 5
                        Logger.log("0) [] {} have more than 1 stations (1~3) : [{}] evp:{}".format(ppty.name, player.name, number_of_owned_stations, eval_point), log_level)
                else:
                    if ppty.number_of_houses > 0:
                        continue
                    # Case1 : all 3 ppty is owned
                    if ppty.property_set.number_of_owned_properties == 3:
                        # Case1-1 : all 3 street is owned by 1p
                        if len(ppty.property_set.owners) == 1:
                            eval_point = 3
                            Logger.log("1) 1-1: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                        # Case1-2 : owned by 2p
                        elif len(ppty.property_set.owners) == 2:
                            # Case1-2-1 : if I'm one of the 2p
                            if owner_me is not None:
                                # Case1-2-1-1 : If I have 2
                                if owner_me[1] == 2:
                                    eval_point = 5
                                    Logger.log("2) 1-2-1-1: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                                # Case1-2-1-2 : If I have 1
                                else:
                                    eval_point = 3
                                    Logger.log("3) 1-2-1-2: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                            # Case1-2-2 : If others have shares
                            else:
                                eval_point = 2
                                Logger.log("4) 1-2-2: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                        # Case1-3 : owned by 3p
                        else:
                            eval_point = 3
                            Logger.log("5) 1-3: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                    # Case2 : 2 ppty is owned
                    elif ppty.property_set.number_of_owned_properties == 2:
                        # Case2-1 : 2 out of 2 is owned in the set
                        if ppty.property_set.number_of_properties == 2:
                            # Case2-1-1 : whole set is owned by this p
                            if len(ppty.property_set.owners) == 1:
                                eval_point = 3
                                Logger.log("6) 2-1-1: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                            # Case2-1-2 : owned by 2 diff players
                            else:
                                # Case2-1-2-1 : if I own 1 of them
                                if owner_me is not None:
                                    eval_point = 5
                                    Logger.log("7) 2-1-2-1: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                                # Case2-1-2-2 : I'm not there
                                else:
                                    eval_point = 3
                                    Logger.log("8) 2-1-2-2: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                        # Case2-2 : 2 ppty owned out of 3 ppty in the set
                        else:
                            # Case2-2-1 : 1p owns 2 of 3
                            if len(ppty.property_set.owners) == 1:
                                eval_point = 3
                                Logger.log("9) 2-2-1: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                            # Case2-2-2 : 2p have 1 ppty each
                            else:
                                # Case2-2-2-1 : if I own 1 of them
                                if owner_me is not None:
                                    eval_point = 4
                                    Logger.log("10) 2-2-2-1: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                                # Case2-2-2-2
                                else:
                                    eval_point = 2
                                    Logger.log("11) 2-2-2-2: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                    # Case3 : 1 ppty is owned
                    elif ppty.property_set.number_of_owned_properties == 1:
                        # Case3-1
                        if ppty.property_set.number_of_properties == 2:
                            eval_point = 4
                            Logger.log("12) 3-1: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)
                        # Case3-2 : if total # of ppty is 3
                        else:
                            eval_point = 4
                            Logger.log("13) 3-2: {} : {}'s point is {}".format(p.name, ppty.name, eval_point), log_level)

                    # calc eval point for street considering color
                    eval_point += 0.1 * self.get_color_preference(ppty.property_set.set_enum)

                    # end of if for street
                # input in the list (Property obj, Player obj, eval_point, quote)
                # quote = (self.BUY_PARM1 * (eval_point - self.BUY_PARM2)
                #          * (eval_point - self.BUY_PARM3) + self.BUY_PARM4 * self.buy_parm_fac[self.get_player_idx(game_state, p)] * 0.1) * ppty.price
                self.property_wish_list.append((ppty, p, round(float(eval_point), 1)))
                # Sort ppty by eval_point, descending order
        self.property_wish_list.sort(key=operator.itemgetter(2), reverse=True)

        Logger.log("*********** property_wish_list ***********", log_level)
        for i, e in enumerate(self.property_wish_list):
            Logger.log("[{}]:{} - {}".format(e[0].name, e[1].name, e[2]), log_level)

    # eval ppty others own
    def evaluate_property_offered(self, ppty):
        eval_point = -1
        for i, e in enumerate(self.property_wish_list):
            if e[0].name == ppty.name:
                eval_point = e[2]
        return eval_point

    # eval ppty I own
    def evaluate_property_wanted(self, player, ppty, ppty_set, proposer_name):
        log_level = Logger.DEBUG
        # 1 = Must Sell
        # 2 = Better Sell (facing value)
        # 3 = Okay to Sell (with some premium)
        # 4 = Better Not Sell (unless huge premium)
        # 5 = Never Sell

        # The more I DON'T want to sell , the higher the point gets.
        if ppty_set.set_enum == "Utility":
            eval_point = 2
            Logger.log("Util: {}'s point is {}".format(ppty.name, eval_point), log_level)
        elif ppty_set.set_enum == "Station":
            number_of_owned_stations = 0
            for temp_ppty in player.state.properties:
                if isinstance(temp_ppty, Station):
                    number_of_owned_stations += 1

            if number_of_owned_stations < 2:
                eval_point = 4
                Logger.log("s0) I have less than 2 stations (0~1) : [{}] evp:{}".format(number_of_owned_stations, eval_point), log_level)
            else:
                eval_point = 5
                Logger.log("s0) I have more than 1 stations (1~3) : [{}] evp:{}".format(number_of_owned_stations, eval_point), log_level)
        else:
            temp_owners = ppty_set.owners
            temp_owners.sort(key=operator.itemgetter(1), reverse=True)
            owner_me_idx = -1
            owner_me = None
            for i, e in enumerate(temp_owners):
                if e[0].name == player.name:
                    owner_me_idx = i
                    owner_me = temp_owners[i]
                    break

            if owner_me is None or owner_me_idx == -1:
                Logger.log("Can't happen1-5", Logger.DEBUG)
                return -1

            is_proposer_same_as_maj_owner = False
            if len(temp_owners) > 1:
                if owner_me_idx == 0:
                    if temp_owners[1][0].name == proposer_name:
                        is_proposer_same_as_maj_owner = True
                else:
                    if temp_owners[0][0].name == proposer_name:
                        is_proposer_same_as_maj_owner = True

            # Case1 : when all 3 ppty is owned by someone
            if ppty_set.number_of_owned_properties == 3:
            # Case1-1: if I own the whole set, never sell
                if owner_me[1] == 3:
                    eval_point = 5
                    Logger.log("s1) 1-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                # Case1-2 : If I own part of the set (2 or 1)
                else:
                    # Case1-2-1 : If the set is owned by 2 players
                    if len(ppty_set.owners) == 2:
                        # Case1-2-1-1 : if I own 2 of 3
                        if owner_me[1] == 2:
                            # better not sell (only 1 left for my Monopoly)
                            eval_point = 4
                            Logger.log("s2) 1-2-1-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                        # Case1-2-1-2 : if I own 1 of 3
                        else:
                            # Case1-2-1-2-1 : if the proposer is the same player who owns 2
                            if is_proposer_same_as_maj_owner:
                                # never sell (allowing other P to monopoly)
                                eval_point = 5
                                Logger.log("s3) 1-2-1-2-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                            # Case1-2-1-2-2 : if the proposer is not the same player who owns rest 2
                            else:
                                eval_point = 3
                                Logger.log("s4) 1-2-1-2-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                    # Case1-2-2 : If the set is owned by 3 players
                    else:
                    # Okay to sell
                        eval_point = 3
                        Logger.log("s5) 1-2-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
            # Case2 : When 2 ppty is owned in the CSet
            elif ppty_set.number_of_owned_properties == 2:
                # Case2-1 : If I own all 2 owned ppty
                if owner_me[1] == 2:
                    # Case2-1-1 : If I owned the whole set
                    if ppty_set.number_of_properties == 2:
                        eval_point = 5
                        Logger.log("s6) 2-1-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                    # Case2-1-2 : If I owned 2 of 3
                    else:
                        # Better not sell (1 more to monopoly)
                        eval_point = 4
                        Logger.log("s7) 2-1-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                # Case2-2 : If I own only 1 of 2
                else:
                    # Case2-2-1 : If the number of pptys in the set is 2 in total
                    if ppty_set.number_of_properties == 2:
                        # Case2-2-1-1 : if the proposer is the same player who owns rest 1
                        if is_proposer_same_as_maj_owner:
                            # Never sell (allowing Monopoly)
                            eval_point = 5
                            Logger.log("s8) 2-2-1-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                        # Case2-2-1-2 : if not,
                        else:
                            # Better not sell (1 more to my Monopoly)
                            eval_point = 4
                            Logger.log("s9) 2-2-1-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                    # Case2-2-2 : If the number of pptys in the set is 3 in total
                    else:
                        if is_proposer_same_as_maj_owner:
                        # Case2-2-2-1 : if the proposer is the same player who owns 1 of 3
                            # Better not sell
                            eval_point = 4
                            Logger.log("s10) 2-2-2-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                        # Case2-2-2-2 : if not
                        else:
                            # okay to sell
                            eval_point = 3
                            Logger.log("s11) 2-2-2-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
            # Case3 : when only 1 ppty is owned in the CSet
            else:
                # Case3-1 : I own 1 of 2
                if ppty_set.number_of_properties == 2:
                    # better not sell (1 more left for my Monopoly)
                    eval_point = 4
                    Logger.log("s12) 3-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                # Case3-2 : I own 1 of 3
                else:
                    eval_point = 4
                    Logger.log("s13) 3-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)

            eval_point += (0.1 * self.get_color_preference(ppty_set.set_enum))

        return float(eval_point)

    def get_available_net_worth(self, player):
        total = player.state.cash

        for ppty in player.state.properties:
            # We add the mortgage value of properties...
            if ppty.is_mortgaged:
                continue
            total += ppty.mortgage_value
            # We add the resale value of houses...
            if type(ppty) == Street:
                total += int(ppty.house_price/2 * ppty.number_of_houses)

        return total

    def has_house_to_build_asap(self, player):
        log_level = Logger.DEBUG
        flag = False
        for os in player.state.owned_sets:
            if os.set_enum == "Station" or os.set_enum == "Utility":
                continue
            else:
                house_num = self.get_num_of_houses_in_set(os)

            if os.set_enum == "Brown":
                if house_num == 10:
                    # Logger.log("HHE - I don't have house enough! ({}) for {}".format(house_num, os.set_enum),log_level)
                    return False
                else:
                    flag = True
            elif os.set_enum == "Dark blue":
                if house_num >= 6:
                    # Logger.log("HHE - I don't have house enough! ({}) for {}".format(house_num, os.set_enum),log_level)
                    return False
                else:
                    flag = True
            else:
                if house_num >= 9:
                    # Logger.log("HHE - I don't have house enough! ({}) for {}".format(house_num, os.set_enum),log_level)
                    return False
                else:
                    flag = True
        # Logger.log("HHE - I have house enough!",log_level)
        return flag

    def has_house_enough(self, player):
        log_level = Logger.DEBUG
        for os in player.state.owned_sets:
            if os.set_enum == "Station" or os.set_enum == "Utility":
                continue
            else:
                house_num = self.get_num_of_houses_in_set(os)

            if os.set_enum == "Brown":
                if house_num < 10:
                    # Logger.log("HHE - I don't have house enough! ({}) for {}".format(house_num, os.set_enum),log_level)
                    return False
            elif os.set_enum == "Dark blue":
                if house_num < 6:
                    # Logger.log("HHE - I don't have house enough! ({}) for {}".format(house_num, os.set_enum),log_level)
                    return False
            else:
                if house_num < 9:
                    # Logger.log("HHE - I don't have house enough! ({}) for {}".format(house_num, os.set_enum),log_level)
                    return False
        # Logger.log("HHE - I have house enough!",log_level)
        return True

    def has_house_to_build(self):
        for i, e in enumerate(self.to_build_list):
            if e[2] > 0:
                return True
        return False

    def get_max_houses_to_build(self, property_set):
        # tbc: text to number
        if property_set.set_enum == "Brown":
            return 10
        else:
            if self.phase == 3:
                if property_set.set_enum == "Light blue" or property_set.set_enum == "Orange":
                    return 15
                elif property_set.set_enum == "Purple":
                    return 12
                elif property_set.set_enum == "Dark blue":
                    return 6
                else:
                    return 9
            elif self.phase == 4:
                if property_set.set_enum == "Dark blue":
                    return 10
                else:
                    return 15
            else:
                if property_set.set_enum == "Dark blue":
                    return 6
                else:
                    return 9

    def get_num_of_houses_in_set(self, ppty_set):
        sum_house = 0
        for ppty in ppty_set.properties:
            if isinstance(ppty, Street):
                sum_house += ppty.number_of_houses

        return sum_house

    def evaluate_property_set_to_build(self, property_set):
        log_level = Logger.INFO

        max_capacity = self.get_max_houses_to_build(property_set)
        house_capacity = max_capacity - self.get_num_of_houses_in_set(property_set)
        set_capacity = int(house_capacity / property_set.number_of_properties)

        eval_point = int((1 - (house_capacity / max_capacity)) * 100 )
        eval_point += self.get_color_preference(property_set.set_enum) * 5

        if self.phase <= 2:
            if house_capacity < property_set.number_of_properties + 1:
                eval_point += 10
        else:
            if property_set.set_enum != "Brown" \
                and int(self.get_num_of_houses_in_set(property_set) / property_set.number_of_properties) >= 3:
                eval_point -= 50
                Logger.log("*** epb] {}] Minus 50 to {} as they have to much set already ({}".format(property_set.set_enum, eval_point, int(self.get_num_of_houses_in_set(property_set) / property_set.number_of_properties)),log_level)
                # time.sleep(2)

        return eval_point

    def update_to_build_list(self, me):
        log_level = Logger.INFO
        del self.to_build_list[0:len(self.to_build_list)]

        for owned_set in me.state.owned_unmortgaged_sets:
            if not owned_set.can_build_houses:
                continue
            self.to_build_list.append((owned_set, self.evaluate_property_set_to_build(owned_set),
                                            self.get_max_houses_to_build(owned_set) - owned_set.properties[0].number_of_houses))
        # Sort Idx of owned_set by eval_result, descending order
        if len(self.to_build_list) > 1:
            self.to_build_list.sort(key=operator.itemgetter(1), reverse=True)
            Logger.log("**** to_build list ",log_level)

        for i, e in enumerate(self.to_build_list):
            Logger.log("[{}] ({})".format(e[0], e[1]),log_level)

    def build_houses(self, game_state, player):
        log_level = Logger.INFO
        # List of tuples -> use list comprehension to get element

        for i, t in enumerate(self.to_build_list):
            budget = player.state.cash - self.cash_reserve + self.get_mortgage_money_available_excl_owned_set(player)
            house_capacity = self.get_max_houses_to_build(t[0]) - self.get_num_of_houses_in_set(t[0])
            set_capacity = int(house_capacity / t[0].number_of_properties)
            money_need_for_set = t[0].number_of_properties * t[0].house_price
            Logger.log("House_Eval_rslt [{}] - eval_point {}".format(t[0].set_enum, t[1]), log_level)

            if house_capacity <= 0:
                Logger.log("Wouldn't build to {} as it aldy reached capacity :{} - Currently has :{}"
                    .format(t[0].set_enum, self.get_max_houses_to_build(t[0]), self.get_num_of_houses_in_set(t[0])), log_level)
                continue

            ppty_to_build = []
            total_count = 0
            # build whole set fisrt if possible
            for num_house in range(set_capacity, 0, -1):
                if money_need_for_set * num_house > budget:
                    continue
                else:
                    budget -= money_need_for_set * num_house
                    for p in t[0].properties:
                        ppty_to_build.append((p, num_house))
                        total_count += num_house
                    break

            if house_capacity <= total_count:
                Logger.log("HB] **************************** ",log_level)
                for i, e in enumerate(ppty_to_build):
                    Logger.log("HB] [{}] - ({}) ".format(e[0], e[1]),log_level)
                return ppty_to_build
            # build each
            each_ppty = []
            for ep in t[0].properties:
                each_ppty.append((ep, ep.number_of_houses))
            each_ppty.sort(key=operator.itemgetter(1), reverse=False)

            for ii, ep in enumerate(each_ppty):
                budget -= ep[0].property_set.house_price
                if budget < 0:
                    break

                count = 1
                if len(ppty_to_build) > 0:
                    for iii, epp in enumerate(ppty_to_build):
                        if epp[0] == ep[0]:
                            count += epp[1]
                            ppty_to_build.remove(epp)
                            break

                ppty_to_build.append((ep[0], count))
                total_count += 1
                if house_capacity <= total_count:
                    Logger.log("HB] **************************** ",log_level)
                    for i, e in enumerate(ppty_to_build):
                        Logger.log("HB] [{}] - ({}) ".format(e[0], e[1]),log_level)
                    return ppty_to_build


            # time.sleep(1)
            Logger.log("HB] **************************** ",log_level)
            for i, e in enumerate(ppty_to_build):
                Logger.log("HB] [{}] - ({}) ".format(e[0], e[1]),log_level)
            return ppty_to_build

        return []

    def sell_houses(self, game_state, player):
        log_level = Logger.INFO

        if self.has_just_holdout_bid or self.fake_bid:
            return None

        money_short = player.state.cash + self.get_mortgage_money_available(player) - self.money_taking_amount
        if money_short >= 0:
            return None

        Logger.log("[SH] Selling houses as I can only get up to ${}[hv:{} + mort:{}] out of {}"
            .format(player.state.cash + self.get_mortgage_money_available(player)
            , player.state.cash, self.get_mortgage_money_available(player), self.money_taking_amount), log_level)
        selling_list = []
        house_money = 0
        add_ppty_money = 0
        tuple_list = []

        for owned_set in player.state.owned_sets:
            # return_money = (owned_set.house_price * 0.5) * owned_set.number_of_properties * owned_set.properties[0].number_of_houses
            if owned_set.set_enum == "Station" or owned_set.set_enum == "Utility":
                continue
            num_house_total = 0
            ppty_price_total = 0
            for ppty in owned_set.properties:
                ppty_price_total += ppty.price
                num_house_total += ppty.number_of_houses
            if num_house_total > 0:
                tuple_list.append((owned_set, self.get_color_preference(owned_set.set_enum), num_house_total
                                   , owned_set.house_price * 0.5  , ppty_price_total * 0.5))
        #  Sort by color preference
        # tuple:
        # e[0] : ppty_set / e[1] : color_preference / e[2] : num of houses / e[3] : price getting for 1 house / e[4] : add ppty price
        tuple_list.sort(key=operator.itemgetter(1), reverse=False)
        ppty_dict = {}
        for i, e in enumerate(tuple_list):
            #  If no houses, skip this set
            if e[2] == 0:
                continue

            ppty_dict.clear()
            ppty_dict = {p.name: 0 for p in e[0].properties}
            # decide how many houses to sell
            for x in range(1, e[2] + 1):
                house_money += e[3]
                # When selling all the house,
                if x == e[2]:
                    add_ppty_money += e[4]

                Logger.log("[SH] Selling {}h of [{}], getting ${} + ({}) out of ${}(short)"
                       .format(x, e[0].set_enum, e[3] * x, add_ppty_money, money_short), log_level)

                if (house_money + add_ppty_money >= abs(money_short)) or x == e[2]:
                    each_ppty = []
                    for ep in e[0].properties:
                        each_ppty.append((ep, ep.number_of_houses))
                    each_ppty.sort(key=operator.itemgetter(1), reverse=True)
                    cnt = 0
                    while  cnt < x:
                        tp = []
                        for i, epp in enumerate(each_ppty):
                            if epp[1] > 0:
                                tp = ((epp[0], epp[1] - 1))
                                ppty_dict[epp[0].name] += 1
                                each_ppty.remove(epp)
                                cnt += 1
                                break
                        each_ppty.append(tp)
                        each_ppty.sort(key=operator.itemgetter(1), reverse=True)

                    for ppty in e[0].properties:
                        selling_list.append((ppty, ppty_dict[ppty.name]))

                    if house_money + add_ppty_money >= abs(money_short):
                        return selling_list

            Logger.log("[SH] *** SUM : ${}(Rcv) + ${}(AdMort) + ${}(Mort) + ${}(Mine) = ${} > ${}"
                    .format(house_money, add_ppty_money, self.get_mortgage_money_available(player), player.state.cash
                    , house_money + add_ppty_money + self.get_mortgage_money_available(player) + player.state.cash
                    , self.money_taking_amount), log_level)


        Logger.log("[SH] Not enough houses to cover all shortage. lets go bankrupt -  {} of {}$"
        .format(add_ppty_money + house_money, money_short), log_level)
        return selling_list

    def get_mortgage_money_available_excl_owned_set(self, player):
        sum_money_to_get = 0
        for ppty in player.state.properties:
            if ppty.is_mortgaged:
                continue
            elif isinstance(ppty, Street) and ppty.property_set.owner is not None:
                continue
            else:
                sum_money_to_get += ppty.mortgage_value

        return  sum_money_to_get

    def get_mortgage_money_available(self, player):
        sum_money_to_get = 0
        for ppty in player.state.properties:
            if ppty.is_mortgaged:
                continue
            elif isinstance(ppty, Street) and self.get_num_of_houses_in_set(ppty.property_set) > 0:
                continue
            else:
                sum_money_to_get += ppty.mortgage_value

        return  sum_money_to_get

    def has_mortgaged_properties(self, player):
        for ppty in player.state.properties:
            if ppty.is_mortgaged:
                return True
        return False

    def mortgage_properties(self, game_state, player):
        log_level = Logger.INFO

        if self.has_just_holdout_bid or self.fake_bid:
            return None

        if self.money_taking_moment and player.state.cash < self.money_taking_amount:
            Logger.log("!!!! need some mortgage !!!!!!!!!", log_level)
            mortgage_list = []
            sum_money_to_get = 0
            for i,e in enumerate(self.property_to_mortgage_list):
                if e[0].is_mortgaged:
                    continue
                elif isinstance(e[0], Street) and e[0].number_of_houses > 0:
                    continue
                else:
                    mortgage_list.append(e[0])
                    sum_money_to_get += e[0].mortgage_value
                    Logger.log("[{}]({}), ${}, sum${}".format(e[0].name, e[1], e[0].price, sum_money_to_get), log_level)
                    if player.state.cash + sum_money_to_get >= self.money_taking_amount:
                        break

            return mortgage_list

    def unmortgage_properties(self, game_state, player):
        log_level = Logger.DEBUG

        if not self.has_mortgaged_properties(player):
            return None

        if self.has_house_to_build():
            return None

        money_balance = player.state.cash - self.cash_reserve
        mortgage_money = self.get_mortgage_money_available_excl_owned_set(player)
        if  money_balance + mortgage_money > 0:
            self.update_to_mortgage_list(player)

            unmortgage_list = []
            sum_money_to_pay = 0
            Logger.log("!!!! doing unmortgage !!!!!!!!!", log_level)
            for i,e in reversed(list(enumerate(self.property_to_mortgage_list))):
                if e[0].is_mortgaged:
                    Logger.log("[UMP] {} [{}] evp:{}".format(e[0].name, e[0].property_set.set_enum, e[1]),log_level)
                    if e[1] < 1:
                        if sum_money_to_pay + e[0].mortgage_value * 1.1 <= money_balance + mortgage_money:
                            sum_money_to_pay += e[0].mortgage_value * 1.1
                            unmortgage_list.append(e[0])
                            Logger.log("[UMP] IMP[{}](evp:{}), ${}, sum:${} allowed:${}".format(e[0].name, e[1], e[0].price, sum_money_to_pay, money_balance + mortgage_money), log_level)
                    else:
                        if sum_money_to_pay + e[0].mortgage_value * 1.1 < money_balance:
                            sum_money_to_pay += e[0].mortgage_value * 1.1
                            unmortgage_list.append(e[0])
                            Logger.log("[UMP] [{}](evp:{}), ${}, sum:${} allowed:${}".format(e[0].name, e[1], e[0].price, sum_money_to_pay, money_balance), log_level)
                else:
                    continue
            return unmortgage_list

        return None

    def update_to_mortgage_list(self, player):
        log_level = Logger.DEBUG
        # 5 = Must
        # 4 = Better
        # 3 = Okay
        # 2 = Better not
        # 1 = Never

        del self.property_to_mortgage_list[0:len(self.property_to_mortgage_list)]
        for ppty in player.state.properties:
            # The more I DON'T want to sell , the higher the point gets.
            if ppty.property_set.set_enum == "Utility":
                eval_point = 4
                Logger.log("m) Util: {}'s point is {}".format(ppty.name, eval_point), log_level)
            elif ppty.property_set.set_enum == "Station":
                number_of_owned_stations = 0
                for temp_ppty in player.state.properties:
                    if isinstance(temp_ppty, Station):
                        number_of_owned_stations += 1

                if number_of_owned_stations < 2:
                    eval_point = 2
                    Logger.log("m0) I have less than 2 stations (0~1) [{}] : evp:{}".format(number_of_owned_stations, eval_point), log_level)
                else:
                    eval_point = 1
                    Logger.log("m0) I have more than 1 stations (2~4) [{}] : evp:{}".format(number_of_owned_stations, eval_point), log_level)

                # Logger.log("m) Station: {}'s point is {}".format(ppty.name, eval_point), log_level)
            else:
                owner_me = None
                owner_me_idx = -1
                temp_owners = ppty.property_set.owners
                temp_owners.sort(key=operator.itemgetter(1), reverse=True)
                for i, e in enumerate(temp_owners):
                    if e[0].name == self.get_name():
                        owner_me_idx = i
                        owner_me = temp_owners[i]
                        break

                if owner_me is None or owner_me_idx == -1:
                    Logger.log("Cant happen 1-2", Logger.DEBUG)
                    return -1

                # Case1 : when all 3 ppty is owned
                if ppty.property_set.number_of_owned_properties == 3:
                # Case1-1: if I own the whole set, never
                    if owner_me[1] == 3:
                        eval_point = 1
                        Logger.log("m1) 1-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                    # Case1-2 : If I own part of the set (2 or 1)
                    else:
                        # Case1-2-1 : If the set is owned by 2 players
                        if len(ppty.property_set.owners) == 2:
                            # Case1-2-1-1 : if I own 2 of 3
                            if owner_me[1] == 2:
                                # okay to get mortgage (only 1 left for my Monopoly)
                                eval_point = 3
                                Logger.log("m2) 1-2-1-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                            # Case1-2-1-2 : if I own 1 of 3
                            else:
                                eval_point = 4
                                Logger.log("m3) 1-2-1-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                        # Case1-2-2 : If the set is owned by 3 players
                        else:
                        # Okay
                            eval_point = 4
                            Logger.log("m4) 1-2-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                # Case2 : When 2 ppty is owned in the CSet
                elif ppty.property_set.number_of_owned_properties == 2:
                    # Case2-1 : If I own all 2 owned ppty
                    if owner_me[1] == 2:
                        # Case2-1-1 : If I owned the whole set
                        if ppty.property_set.number_of_properties == 2:
                            eval_point = 1
                            Logger.log("m5) 2-1-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                        # Case2-1-2 : If I owned 2 of 3
                        else:
                            # Better not (1 more to monopoly)
                            eval_point = 2
                            Logger.log("m6) 2-1-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                    # Case2-2 : If I own only 1 of 2
                    else:
                        eval_point = 4
                        Logger.log("m7) 2-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                # Case3 : when only 1 ppty is owned in the CSet
                else:
                    # Case3-1 : I own 1 of 2
                    if ppty.property_set.number_of_properties == 2:
                        # better not sell (1 more left for my Monopoly)
                        eval_point = 2
                        Logger.log("m8) 3-1 : {}'s point is {}".format(ppty.name, eval_point), log_level)
                    # Case3-2 : I own 1 of 3
                    else:
                        eval_point = 3
                        Logger.log("m9) 3-2 : {}'s point is {}".format(ppty.name, eval_point), log_level)

                eval_point -= (0.1 * self.get_color_preference(ppty.property_set.set_enum))

            self.property_to_mortgage_list.append((ppty, round(float(eval_point), 2)))
            # Sort ppty by eval_point, descending order
        self.property_to_mortgage_list.sort(key=operator.itemgetter(1), reverse=True)

        # Logger.log("*********** to_mortgage_list ***********", log_level)
        # for i, e in enumerate(self.property_to_mortgage_list):
        #     Logger.log("[{}]:{}".format(e[0].name, e[1]), log_level)

    def landed_on_unowned_property(self, game_state, player, ppty):
        log_level = Logger.DEBUG
        # TBI - shd add logic to get mortgage to buy best items
        eval_point = self.evaluate_unowned_property(player, ppty, ppty.property_set)

        # get money status
        money_balance = player.state.cash - self.cash_reserve
        risky_money_balance = player.state.cash - self.second_cash_reserve
        mortgage_money = self.get_mortgage_money_available_excl_owned_set(player)

        # ****************** Params that affect mortgage usage ******************
        self.update_to_build_list(player)
        has_house_to_build_asap = self.has_house_to_build_asap(player)
        has_enough_house = self.has_house_enough(player)
        has_enough_set = False
        if len(player.state.owned_sets) > self.get_max_owned_set(game_state) + 1:
            has_enough_set = True
        # ************************************************************************
        if has_house_to_build_asap:
            budget = money_balance
            if eval_point >=5:
                budget += mortgage_money
            Logger.log("[LUBudget] level1: don't buy unless necessary bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)
        elif has_enough_set:
            budget = risky_money_balance
            if eval_point >=5:
                budget += mortgage_money
            Logger.log("[LUBudget] level2: better not buy , I've got enough bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)
        elif has_enough_house:
            budget = risky_money_balance + mortgage_money
            if eval_point <= 3:
                budget -= mortgage_money
            Logger.log("[LUBudget] level4: better buy , still hungry bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)
        else:
            budget = money_balance + mortgage_money
            if eval_point <= 3:
                budget -= mortgage_money
            Logger.log("[LUBudget] level3: good to buy bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)


        if budget > ppty.price:
            return PlayerAIBase.Action.BUY
        else:
            Logger.log("$$ Couldn't buy unowned ppty due to money short or low evp  nd:${} hv:${} rsv:${} money_bal:${}".format(ppty.price, player.state.cash, self.cash_reserve, money_balance), log_level)
            return PlayerAIBase.Action.DO_NOT_BUY

    def get_max_owned_set(self, game_state):
        max_set = 0
        for p in game_state.players:
            if p.name == self.get_name():
                continue
            max_set = max(len(p.state.owned_sets), max_set)
        return max_set

    def property_offered_for_auction(self, game_state, player, ppty):
        log_level = Logger.INFO
        eval_point = self.evaluate_unowned_property(player, ppty, ppty.property_set)

        # get money status
        money_balance = player.state.cash - self.cash_reserve
        risky_money_balance = player.state.cash - self.second_cash_reserve
        mortgage_money = self.get_mortgage_money_available_excl_owned_set(player)

        # ****************** Params that affect mortgage usage ******************
        self.update_to_build_list(player)
        has_house_to_build_asap = self.has_house_to_build_asap(player)
        has_enough_house = self.has_house_enough(player)
        has_enough_set = False
        if len(player.state.owned_sets) > self.get_max_owned_set(game_state) + 1:
            has_enough_set = True

        # ************************************************************************
        if has_house_to_build_asap:
            budget = money_balance
            if eval_point >=5:
                budget += mortgage_money
            Logger.log("[ACBudget] level1: don't buy unless necessary bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)
        elif has_enough_set:
            budget = risky_money_balance
            if eval_point >=5:
                budget += mortgage_money
            Logger.log("[ACBudget] level2: better not buy , I've got enough bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)
        elif has_enough_house:
            budget = risky_money_balance + mortgage_money
            if eval_point <= 3:
                budget -= mortgage_money
            Logger.log("[ACBudget] level4: better buy , still hungry bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)
        else:
            budget = money_balance + mortgage_money
            if eval_point <= 3:
                budget -= mortgage_money
            Logger.log("[ACBudget] level3: good to buy bg[{}] (mb[{}], rmb[{}], mrt[{}]".format(budget, money_balance, risky_money_balance, mortgage_money),log_level)

        # if this ppty is important to other p, and not to me, try holdout_quote
        holdout_quote = self.try_holdout_bid(game_state, ppty, player)
        if eval_point < 3 and holdout_quote > 0:
            return holdout_quote
        else:
            quote = int((self.BID_PARM1 * (eval_point - self.BID_PARM2)
                            * (eval_point - self.BID_PARM3) + self.BID_PARM4) * ppty.price * self.bid_parm_fac * 0.01)
            mb = quote

            Logger.log("[ACStart] bid for [{}][${}] w/ $ {} evp:{} / bid_fac:{}".format(ppty.name, ppty.price, quote, eval_point, self.bid_parm_fac), log_level)

            #  Refer to DB ******************************************************************
            max_bid_fac = 100
            Logger.indent()
            rival_p = None
            for temp_player in game_state.players:
                if temp_player.name == self.get_name():
                    continue
                temp_eval_point = int(self.evaluate_unowned_property(temp_player, ppty, ppty.property_set))
                tuple = self.players_bid_db[temp_player.name]
                temp_bid_fac = tuple[temp_eval_point - 1]
                if temp_bid_fac > max_bid_fac:
                    max_bid_fac = temp_bid_fac
                    rival_p = temp_player
                    Logger.log("[ACO] For {}, [{}]'s evp:{}, bid_fac:{}".format(temp_player.name, ppty.name, temp_eval_point, temp_bid_fac), log_level)
            Logger.dedent()

            if rival_p is not None:
                rb = int(ppty.price * max_bid_fac * 0.01)
                rh = rival_p.state.cash
                rh_max = self.get_available_net_worth(rival_p)
                mbq = int((self.BID_PARM1 * (eval_point - self.BID_PARM2)* (eval_point - self.BID_PARM3) + self.BID_PARM4) * ppty.price * self.MAX_BID_PARM_FAC * 0.01)
                Logger.log("[ACO] Rival_P :[{}], [{}]'s bid_fac:{}, rb:{}, budget:{}".format(rival_p.name, ppty.name, max_bid_fac, rb, rh), log_level)
                Logger.log("[ACO] My_quote : bid_fac:{}, evp:{}, mvq:{}, budget:{}".format(self.bid_parm_fac, eval_point, mbq, money_balance + mortgage_money), log_level)

                Logger.indent()
                if eval_point >= 5:
                    mb = min((min(rb, rh_max) + 1), mbq)
                    Logger.log("[ACO] Evp:5 mb:[{}]".format(mb), log_level)
                elif eval_point >= 4:
                    mb = min((min(rb, rh) + 1), mbq)
                    Logger.log("[ACO] Evp:4 mb:[{}]".format(mb), log_level)
                # elif eval_point >= 3:
                #     # if rb >= rh:
                #     #     if rh >= budget:
                #     #         mb = int((rb + rh) / 2)
                #     #     else:
                #     #         if rb >= budget:
                #     #             mb = int((rb + budget) / 2)
                #     #         else:
                #     #             mb = int((rb + rh) / 2)
                #     # else:
                #     #     if rb >= budget:
                #     #         mb = int((rb + budget) / 2)
                #     #     else:
                #     #         if rh >= budget:
                #     #             mb = int((rb + budget) / 2)
                #     #         else:
                #     #             mb = int((rb + rh) / 2)
                #
                #     Logger.log("[ACO] Evp:3 mb:[{}]".format(mb), log_level)
                Logger.dedent()

            else:
                Logger.log("[ACO] Don't hv Rival Yet",log_level)
            # **************************************************************************************
            max_tevp = 0
            client = None
            for tp in game_state.players:
                if tp.name == self.get_name():
                    continue
                tevp = int(self.evaluate_unowned_property(tp, ppty, ppty.property_set))
                if tevp > max_tevp:
                    max_tevp = tevp
                    client = tp

            cq = int((self.BID_PARM1 * (max_tevp - self.BID_PARM2)* (max_tevp - self.BID_PARM3) + self.BID_PARM4) * ppty.price * 90 * 0.01)
            Logger.log("[AC] My Client is {} with evp {}, cq ${}".format(client.name, max_tevp, cq),log_level)
            if max_tevp >= 4:
                ch = client.state.cash + self.get_mortgage_money_available_excl_owned_set(client)
            else:
                ch = client.state.cash

            self.has_just_bid = True
            self.fake_bid = False
            self.bid_evp = eval_point
            if mb > budget:
                if budget > cq:
                    self.bid_quote_amount = budget
                    Logger.log("[AC-1-1] Bdgt > cq bid, $[{}] ".format(self.bid_quote_amount),log_level)
                elif budget > ppty.price:
                    self.bid_quote_amount = budget
                    Logger.log("[AC-1-2] Bdgt > FV  bid, $[{}] ".format(self.bid_quote_amount),log_level)
                else:
                    self.fake_bid = True
                    if ch > budget:
                        if cq > ch:
                            self.bid_quote_amount = ch + 1
                            Logger.log("[AC-2-1] Fake  bid, $[{}] ".format(self.bid_quote_amount),log_level)
                        else:
                            self.bid_quote_amount = cq - 1
                            Logger.log("[AC-2-2] Fake  bid, $[{}] ".format(self.bid_quote_amount),log_level)
                    else:
                        self.bid_quote_amount = budget - 1
                        Logger.log("[AC-2-3] Fake bid, $[{}] ".format(self.bid_quote_amount),log_level)
            else:
                self.bid_quote_amount = mb
                Logger.log("[AC-3] Normal bid, $[{}] ".format(self.bid_quote_amount),log_level)

            return self.bid_quote_amount

    def try_holdout_bid(self, game_state, ppty, me):
        log_level = Logger.INFO

        self.has_just_holdout_bid = False
        for oth_p in game_state.players:
            if oth_p.name == self.get_name():
                continue
            oth_evp = self.evaluate_unowned_property(oth_p, ppty, ppty.property_set)
            if oth_evp >= 5:
                self.has_just_holdout_bid = True
                self.holdout_p = oth_p
                break

        if self.has_just_holdout_bid:

            tuple_fac = self.players_bid_db[self.holdout_p.name]
            # mb (my bid) / pb (player bid) / ph (player have) / mh (my have)
            mb = int(ppty.price * tuple_fac[4] * 0.01)
            ph = self.holdout_p.state.cash + self.get_mortgage_money_available_excl_owned_set(self.holdout_p)
            mh = me.state.cash
            mrt = self.get_mortgage_money_available_excl_owned_set(me)
            min_bid = int(ppty.price * self.MIN_HOLDOUT_FAC * 0.01)
            self.holdout_ph = ph
            self.holdout_mh = mh

            # and (mh < int(ppty.price * self.MIN_HOLDOUT_FAC * 0.01)) and (mrt > self.second_cash_reserve):
            # do this only safe
            if mb > mh:
                if ph > mb:
                    if (mh < min_bid * 2) and (mrt >= self.second_cash_reserve):
                        Logger.log("HOB-1) Ppty:[{}](${}) {} : fac {}, bid [{}] ph[{}] (mh:[{}] MIN*2:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid * 2, self.second_cash_reserve, mrt), log_level)
                    else:
                        Logger.log("HOB-1-1) Ppty:[{}](${}) {} : return FV - fac {}, bid [{}] ph[{}] (mh:[{}] MIN*2:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid * 2, self.second_cash_reserve, mrt), log_level)
                        mb = ppty.price
                else:
                    if tuple_fac[4] != self.HOLDOUT_BIG_FAC:
                        if mh < min_bid and (mrt >= self.second_cash_reserve):
                            Logger.log("HOB-2) Ppty:[{}](${}) {} : fac {}, bid [{}] ph[{}] (mh:[{}] MIN:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid, self.second_cash_reserve, mrt), log_level)
                        else:
                            Logger.log("HOB-2-1) Ppty:[{}](${}) {} : return FV - fac {}, bid [{}] ph[{}]  (mh:[{}] MIN:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid, self.second_cash_reserve, mrt), log_level)
                            mb = ppty.price
                    else:
                        if int(mh < int(min_bid * 1.5)) and (mrt >= self.second_cash_reserve):
                            Logger.log("HOB-3) Ppty:[{}](${}) {} : fac {}, bid [{}] ph[{}]  (mh:[{}] MIN*1.5:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, int(min_bid * 1.5), self.second_cash_reserve, mrt), log_level)
                        else:
                            Logger.log("HOB-3-1) Ppty:[{}](${}) {} : return FV - fac {}, bid [{}] ph[{}] (mh:[{}] MIN*1.5:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, int(min_bid * 1.5), self.second_cash_reserve, mrt), log_level)
                            mb = ppty.price
                # self.holdout_mb = mb
                # return mb
            else:
                if ph > mh:
                    if (mb < min_bid * 2) and (mh - mb + mrt >= self.second_cash_reserve):
                        Logger.log("HOB-4) Ppty:[{}](${}) {} : fac {}, bid [{}] ph[{}] (mh:[{}] MIN*2:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid * 2, self.second_cash_reserve, mrt), log_level)
                    else:
                        Logger.log("HOB-4-1) Ppty:[{}](${}) {} : return FV - fac {}, bid [{}] ph[{}] (mh:[{}] MIN*2:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid * 2, self.second_cash_reserve, mrt), log_level)
                        mb = ppty.price
                else:
                    if ph > mb:
                        if (mb < int(min_bid * 1.5)) and (mh - mb + mrt >= self.second_cash_reserve):
                            Logger.log("HOB-5) Ppty:[{}](${}) {} : fac {}, bid [{}] ph[{}] (mh:[{}] MIN*1.5:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid * 1.5, self.second_cash_reserve, mrt), log_level)
                        else:
                            Logger.log("HOB-5-1) Ppty:[{}](${}) {} : return FV - fac {}, bid [{}] ph[{}] (mh:[{}] MIN*1.5:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid * 1.5, self.second_cash_reserve, mrt), log_level)
                            mb = ppty.price
                    else:
                        if mb < min_bid and (mh - mb + mrt >= self.second_cash_reserve):
                            Logger.log("HOB-6) Ppty:[{}](${}) {} : fac {}, bid [{}] ph[{}] (mh:[{}] MIN:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid, self.second_cash_reserve, mrt), log_level)
                        else:
                            Logger.log("HOB-6-1) Ppty:[{}](${}) {} : return FV - fac {}, bid [{}] ph[{}] (mh:[{}] MIN:[{}] cr:[{}] mrt:[{}])".format(ppty.name, ppty.price ,self.holdout_p.name, tuple_fac[4], mb, ph, mh, min_bid, self.second_cash_reserve, mrt), log_level)
                            mb = ppty.price

                # Logger.log("HOB-7) Ppty:[{}](${}) {}'s holdout[{}] : return FV / fac {} (mb:[{}] mh:[{}] MIN:[{}] cr:[{}] mrt:[{}]) ".format(ppty.name, ppty.price ,self.holdout_p.name, 5, tuple_fac[4],  mb, mh, int(ppty.price * self.MIN_HOLDOUT_FAC * 0.01), self.cash_reserve, mrt), log_level)
                # mb = ppty.price

            self.holdout_mb = mb
            return self.holdout_mb
                # self.holdout_mb = ppty.price
                # return ppty.price
        else:
            return 0


    def auction_result(self, status, ppty, player, amount_paid):
        log_level = Logger.INFO

        # adjust player_db
        if self.has_just_holdout_bid:
            current_fac = self.players_bid_db[self.holdout_p.name]
            min_holdout_px = int(ppty.price * self.HOLDOUT_ADJUST_UNIT * 0.01)
            if current_fac[4] == self.HOLDOUT_BIG_FAC:
                my_holdout_px = min_holdout_px
            else:
                my_holdout_px = self.holdout_mb
            if status == self.Action.AUCTION_SUCCEEDED:
                if player.name == self.holdout_p.name:
                    # normal case - I bid 2nd bigger amount after the p
                    # a-2
                    if amount_paid == self.holdout_mb + 1:
                        Logger.log("[ARH-P1] good case",log_level)
                    elif amount_paid == 1:
                        # a-3 / b'-2 / b'-3 / MOP
                        if self.holdout_ph > my_holdout_px and self.holdout_mb > ppty.price:
                            new_fac = int((self.holdout_snatch - 1) / ppty.price * 90)
                            Logger.log("[ARH-P3] SNATCHED!! [{}]".format(self.holdout_snatch - 1), log_level)
                            self.adjust_players_bid_db_to(4, self.holdout_p.name, new_fac)
                        # b-2 / b-3 / c-2 / b'-2 / b'-3 / c'-2
                        else:
                            Logger.log("[ARH-P3-1] Snatched but useless as ph [{}] was less than mb [{}] or I bid FV".format(self.holdout_ph, my_holdout_px), log_level)
                    # when 3rd player bid more than mine and less than the p
                    else:
                        # MPO
                        if self.holdout_mb > amount_paid:
                            if self.holdout_ph > my_holdout_px and self.holdout_mb > ppty.price:
                                new_fac = int((self.holdout_snatch - 1) / ppty.price * 90)
                                Logger.log("[ARH-P4] MPO: SNATCHED!! [{}]".format(self.holdout_snatch - 1), log_level)
                                self.adjust_players_bid_db_to(4, self.holdout_p.name, new_fac)
                            else:
                                Logger.log("[ARH-P4-1] MPO: Snatched but useless as ph [{}] was less than mb  or I bid FV[{}]".format(self.holdout_ph, my_holdout_px), log_level)
                        # POM
                        elif amount_paid > self.holdout_mb + 1:
                            gap = int((amount_paid - 1)/ppty.price * 100 - current_fac[4])
                            if gap > int(self.HOLDOUT_ADJUST_UNIT / 2):
                                Logger.log("[ARHO-P5] POM, oth_fac:[{}], my_fac:[{}], gap:[{}] is big => Inc to [{}]".format(int((amount_paid - 1)/ppty.price * 100), current_fac[4], gap, current_fac[4] + int(gap / 2)), log_level)
                                self.adjust_players_bid_db_to(4, self.holdout_p.name, current_fac[4] + int(gap / 2))
                            else:
                                Logger.log("[ARHO-P5-1] POM, oth_fac:[{}], my_fac:[{}], gap:[{}] is little  or I bid FV, stay at [{}]".format(int((amount_paid - 1)/ppty.price * 100), current_fac[4], gap, current_fac[4]), log_level)
                        else:
                            Logger.log("[ARH-PX1] what else ?!", log_level)
                # as I always bid when mb > mh, case I win is
                #
                elif player.name == self.get_name():
                    if amount_paid  > min_holdout_px:
                        if self.holdout_ph > my_holdout_px and self.holdout_mb > ppty.price:
                            if current_fac[4] == self.HOLDOUT_BIG_FAC:
                                new_fac = int((amount_paid  - 1) / ppty.price * 90)
                                Logger.log("[ARH-M1-1] Spent, but got info [{}]".format(amount_paid  - 1), log_level)
                                self.adjust_players_bid_db_to(4, self.holdout_p.name, new_fac)
                            else:
                                gap = current_fac[4] - int((amount_paid - 1)/ppty.price * 100)
                                if gap > int(self.HOLDOUT_ADJUST_UNIT / 2):
                                    Logger.log("[ARH-M1-1-1] Spent, pb_fac:[{}], my_fac:[{}], gap:[{}] is big => dec to [{}]".format(int((amount_paid - 1)/ppty.price * 100), current_fac[4], gap, current_fac[4] - int(gap / 2)), log_level)
                                    self.adjust_players_bid_db_to(4, self.holdout_p.name, current_fac[4] + int(gap / 2))
                                else:
                                    Logger.log("[ARH-M1-1-2] Spent, pb_fac:[{}], my_fac:[{}], gap:[{}] is little stay at [{}]".format(int((amount_paid - 1)/ppty.price * 100), current_fac[4], gap, current_fac[4]), log_level)
                        else:
                            Logger.log("[ARH-M1-2] MPO: Spent a fortune but useless as ph [{}] was less than mb  or I bid FV[{}]".format(self.holdout_ph, my_holdout_px), log_level)
                    # a-1 / b-1 / c-1
                    elif amount_paid == 1:
                        Logger.log("[ARH-M2] P bid more than MB when MB > PH or didn't bid at all", log_level)
                    # a-4 / b-4 / c-3 / c-4 / b'-4 / c'-3 / c'-4
                    else:
                        Logger.log("[ARH-M3] Do nothing, not useful info ", log_level)
                # other p got it (rare case)
                else:
                    # OMP / POM
                    if amount_paid == self.holdout_mb + 1:
                        Logger.log("[ARHO-O1] OMP / POM, do nothin' as don't know which")
                    # MPO / PMO
                    elif amount_paid == 1:
                        Logger.log("[ARHO-O3] MPO / PMO, $1 ppty , do nothing", log_level)
                    # MOP -> OPM (I bid the biggest, but couldn't get it due to money short)
                    elif self.holdout_mb > amount_paid:
                        if self.holdout_ph > my_holdout_px and self.holdout_mb > ppty.price:
                            new_fac = int((amount_paid - 1) / ppty.price * self.HOLDOUT_BID_RATIO)
                            Logger.log("[ARHO-O4] MOP -> OPM , inc to [{}]".format(new_fac), log_level)
                            self.adjust_players_bid_db_to(4, self.holdout_p.name, new_fac)
                        else:
                            Logger.log("[ARHO-O4] MOP -> OPM , stay at [{}] as ph was little  or I bid FV".format(current_fac[4]), log_level)
                    # OPM
                    else:
                        gap = int((amount_paid - 1)/ppty.price * 100 - current_fac[4])
                        if gap > int(self.HOLDOUT_ADJUST_UNIT / 2):
                            Logger.log("[ARHO-O5] OPM, pb_fac:[{}], my_fac:[{}], gap:[{}] is big => Inc to [{}]".format(int((amount_paid - 1)/ppty.price * 100), current_fac[4], gap, current_fac[4] + int(gap / 2)), log_level)
                            self.adjust_players_bid_db_to(4, self.holdout_p.name, current_fac[4] + int(gap / 2))
                        else:
                            Logger.log("[ARHO-O5-1] OPM, pb_fac:[{}], my_fac:[{}], gap:[{}] is little stay at [{}]".format(int((amount_paid - 1)/ppty.price * 100), current_fac[4], gap, current_fac[4]), log_level)
                    # tbc
                    # Logger.log("Can't Happen HOB3",log_level)
        else:
            if self.has_just_bid and not self.fake_bid and self.bid_evp > 3:
                if status == self.Action.AUCTION_SUCCEEDED:
                    if player.name == self.get_name():
                        if amount_paid == 1:
                            Logger.log("[ACR-1] AmountPaid == 1 ,Do not Adjust bid_parm_fac",log_level)
                        else:
                            amount_gap_fac = round((self.bid_quote_amount - (amount_paid - 1)) / ppty.price, 2) * 100
                            if amount_gap_fac > 10:
                                fac_adjust_point = int(amount_gap_fac / 2)
                                self.bid_parm_fac -= min(self.MAX_BID_PARM_DEC_UNIT, fac_adjust_point)
                                if self.bid_parm_fac < self.MIN_BID_PARM_FAC:
                                    self.bid_parm_fac = self.MIN_BID_PARM_FAC
                                Logger.log("[ACR-2] Adjust bid_parm_fac dec by ({}) to {} (${}(qt) - ${} (paid)) / {} (ppty.price) ".format(min(self.MAX_BID_PARM_DEC_UNIT, fac_adjust_point), self.bid_parm_fac, self.bid_quote_amount, amount_paid - 1, ppty.price),log_level)
                            else:
                                self.bid_parm_fac += int(self.BID_PARM_INC_UNIT / 2)
                                if self.bid_parm_fac > self.MAX_BID_PARM_FAC:
                                    self.bid_parm_fac = self.MAX_BID_PARM_FAC
                                Logger.log("[ACR-3] Adjust bid_parm_fac inc by {} as it was close to second bidder  {} ${}(qt) / ${} (winner paid) ".format(int(self.BID_PARM_INC_UNIT / 2), self.bid_parm_fac, self.bid_quote_amount, amount_paid),log_level)
                    else:
                        # We don't know how much winner actually bid,

                        # winner_cash_flow = self.get_player_cash(player.name) - player.state.cash
                        # amount_gap_fac = round((winner_cash_flow - self.bid_quote_amount) / ppty.price, 2) * 100
                        if amount_paid < self.bid_quote_amount:
                            Logger.log("[ACR-4] Auction failed as I didn't hv enough money ${} (qt) / ${} (winner paid)".format(self.bid_quote_amount, amount_paid),log_level)
                        else:
                            self.bid_parm_fac += self.BID_PARM_INC_UNIT
                            if self.bid_parm_fac > self.MAX_BID_PARM_FAC:
                                self.bid_parm_fac = self.MAX_BID_PARM_FAC

                            Logger.log("[ACR-5] Adjust bid_parm_fac inc by ({}) to {} ${}(qt) / ${} (winner paid) ".format(self.BID_PARM_INC_UNIT, self.bid_parm_fac, self.bid_quote_amount, amount_paid),log_level)
            # I didn't involved in auction, but still can colletc data
            if status == self.Action.AUCTION_SUCCEEDED:
                a=1
                eval_point = int(self.evaluate_property_wanted(player, ppty, ppty.property_set, ""))

                tuple = self.players_bid_db[player.name]
                parm_fac = int(amount_paid - 1 / ppty.price * 90)
                if eval_point == 1:
                    new_tuple = ( max(parm_fac, tuple[0]), tuple[1], tuple[2], tuple[3], tuple[4])
                elif eval_point == 2:
                    new_tuple = ( tuple[0], max(parm_fac, tuple[1]), tuple[2], tuple[3], tuple[4])
                elif eval_point == 3:
                    new_tuple = ( tuple[0], tuple[1], max(parm_fac, tuple[2]), tuple[3], tuple[4])
                elif eval_point == 4:
                    new_tuple = ( tuple[0], tuple[1], tuple[2], max(parm_fac, tuple[3]), tuple[4])
                else:
                    final_val = 0
                    if tuple[4] == self.HOLDOUT_BIG_FAC and parm_fac > self.MIN_HOLDOUT_FAC:
                        final_val = parm_fac
                        Logger.log("WOW for {}, parm_fac{}".format(player.name, final_val),log_level)
                    else:
                        final_val = max(parm_fac, tuple[4])

                    new_tuple = ( tuple[0], tuple[1], tuple[2], tuple[3], final_val)

                self.players_bid_db[player.name] = new_tuple

        self.has_just_holdout_bid = False
        self.has_just_bid = False
        self.fake_bid = False
        # Adjust my parm_fac


    def adjust_players_bid_db_to(self, eval_idx, player_name, new_fac):
        log_level = Logger.INFO
        current_fac = self.players_bid_db[player_name]
        if new_fac > self.MAX_HOLDOUT_FAC:
            final_fac = self.MAX_HOLDOUT_FAC
        elif new_fac < self.MIN_HOLDOUT_FAC:
            final_fac = self.MIN_HOLDOUT_FAC
        else:
            final_fac = new_fac

        Logger.log("adjust from {} to {}".format(current_fac[4], final_fac), log_level)
        if eval_idx == 4:
            tuple_fac = (current_fac[0], current_fac[1], current_fac[2], current_fac[3], final_fac)
            self.players_bid_db[player_name] = tuple_fac
            return
        else:
            a=1
            # tbi

    #  dpdp
    def deal_proposed(self, game_state, player, deal_proposal):
        log_level = Logger.INFO
        # Logger.log("chg-Deal Proposed to {} by {}".format(player.name, self.current_player.name), log_level)

        if self.last_deal_received == deal_proposal:
            Logger.log("SameDeal Proposed - rejecting", log_level)
            return DealResponse(DealResponse.Action.REJECT)

        # get money status
        money_balance = player.state.cash - self.cash_reserve
        risky_money_balance = player.state.cash - self.second_cash_reserve
        mortgage_money = self.get_mortgage_money_available_excl_owned_set(player)

        has_wanted = False
        has_offered = False
        has_never_sell_ppty = False
        has_dont_buy_ppty = False
        has_must_buy_ppty = False
        if len(deal_proposal.properties_wanted) > 0:
            has_wanted = True
        if len(deal_proposal.properties_offered) > 0:
            has_offered = True
            # update wish list
            self.update_property_wish_list(game_state, player)

        quote_sum_wanted = 0
        quote_sum_offered = 0
        if has_wanted:
            for ppty_wanted in deal_proposal.properties_wanted:
                eval_point = self.evaluate_property_wanted(player, ppty_wanted, ppty_wanted.property_set
                    , deal_proposal.proposed_by_player.name)

                if eval_point >= 5:
                    has_never_sell_ppty = True

                quote = int((self.SELL_PARM1 * (eval_point - self.SELL_PARM2) * (eval_point - self.SELL_PARM3)
                         + self.SELL_PARM4) * ppty_wanted.price)

                quote_sum_wanted += int(quote)

                Logger.log(
                    "[DP] wanted : {}: {}[{}]-{} @ ${}".format(deal_proposal.proposed_by_player.name, ppty_wanted.name,
                                                              ppty_wanted.property_set.set_enum, eval_point, quote), log_level)
        if has_offered:
            for ppty_offered in deal_proposal.properties_offered:

                eval_point = self.evaluate_property_offered(ppty_offered)
                
                if eval_point < 3:
                    has_dont_buy_ppty = True
                if eval_point >= 5:
                    has_must_buy_ppty = True
                
                # quote = int((self.BUY_PARM1 * (eval_point - self.BUY_PARM2) * (eval_point - self.BUY_PARM3)
                #          + self.BUY_PARM4) * ppty_offered.price * self.buy_parm_fac[deal_proposal.proposed_by_player.name] * 0.01)
                #  tbc tbd
                quote = int((self.BUY_PARM1 * (eval_point - self.BUY_PARM2) * (eval_point - self.BUY_PARM3)
                         + self.BUY_PARM4) * ppty_offered.price * 0.7)

                quote_sum_offered += int(quote)
                Logger.log(
                    "[DP]offered : {}: {}[{}]-{} @ ${} w/ fac:{}".format(deal_proposal.proposed_by_player.name, ppty_offered.name,
                                                               ppty_offered.property_set.set_enum, eval_point, quote, self.buy_parm_fac[deal_proposal.proposed_by_player.name]), log_level)

        self.last_deal_received = deal_proposal
        # Logger.log("Eval_point_wanted_sum: {} / offered_sum: {}".format(eval_point_wanted, eval_point_offered), log_level)

        # Respond to Proposal
        # when both wanted and offered are proposed
        if has_wanted and has_offered:
            if quote_sum_offered > quote_sum_wanted and (quote_sum_offered - quote_sum_wanted) < money_balance + mortgage_money:
                Logger.log("[DP] Acpt Deal w/ $offered {}".format(quote_sum_offered - quote_sum_wanted), log_level)
                return DealResponse(
                    action=DealResponse.Action.ACCEPT,
                    maximum_cash_offered=int(quote_sum_offered - quote_sum_wanted))
            else:
                Logger.log("[DP] Rjct Deal as quote sum offered is bigger ${}".format(quote_sum_offered - quote_sum_wanted), log_level)
                return DealResponse(DealResponse.Action.REJECT)
        # when having only 'wanted'
        elif has_wanted:
            if has_never_sell_ppty:
                Logger.log("[DP] Rjct Deal as there's a never selling ppty", log_level)
                return DealResponse(DealResponse.Action.REJECT)
            else:
                Logger.log("[DP] Acpt Deal w/ $wanted {}".format(quote_sum_wanted), log_level)
                return DealResponse(
                    action=DealResponse.Action.ACCEPT,
                    minimum_cash_wanted=quote_sum_wanted)
                # when having only 'offered'
        elif has_offered:            
            Logger.log("[DP] Acpt Deal w/offered ${}".format(quote_sum_offered), log_level)
            if has_dont_buy_ppty and not has_must_buy_ppty:
                return DealResponse(DealResponse.Action.REJECT)
            else:
                if quote_sum_offered < money_balance + mortgage_money:
                    return DealResponse(
                        action=DealResponse.Action.ACCEPT,
                        maximum_cash_offered=quote_sum_offered)
                else:
                    return DealResponse(DealResponse.Action.REJECT)
        else:
            Logger.log("Can't happen1-6", Logger.DEBUG)

    def propose_deal(self, game_state, player):
        log_level = Logger.DEBUG
        Logger.log("[DPSTART] --------------------------------------------------------", log_level)
        deal_proposal = None
        if self.has_just_holdout_bid or self.fake_bid:
            return None
        # Sell Deal **********************************************************************
        if self.money_taking_moment:
            if self.money_taking_amount > self.get_available_net_worth(player):
                self.update_to_mortgage_list(player)

                to_sell_list = []
                for i,e in enumerate(self.property_to_mortgage_list):
                    if isinstance(e[0], Street) and e[0].number_of_houses > 0:
                        continue
                    to_sell_list.append((e[0], e[0].price))
                    to_sell_list.sort(key=operator.itemgetter(1), reverse=True)

                for i,e in enumerate(to_sell_list):
                    max_evp = [0, None]
                    for temp_player in game_state.players:
                        if temp_player.name == self.get_name():
                            continue
                        # rebuild the list for other players
                        self.update_property_wish_list(game_state, temp_player)
                        evp_for_player = self.evaluate_property_offered(e[0])
                        # sell this ppty to whom wants this the most
                        if evp_for_player > max_evp[0]:
                            max_evp[0] = evp_for_player
                            max_evp[1] = temp_player

                    deal_proposal = DealProposal(propose_to_player=max_evp[1],
                                     properties_offered=[e[0]],
                                     minimum_cash_wanted=int(e[0].price * 0.7))
                    if e[0] in self.last_ppty_offered:
                        continue
                    Logger.log("[PD] About to broke due:${} (anw:${}) sell this ppty[{}] to:'{}' (evp:{}) @${}"
                            .format(self.money_taking_amount, self.get_available_net_worth(player), e[0].name, max_evp[1].name, max_evp[0], e[0].price - 1), log_level)
                    # rebuild the list for me again
                    self.update_property_wish_list(game_state, player)
                    self.last_ppty_offered.append(e[0])
                    return deal_proposal

            return deal_proposal

        # get money status
        money_balance = player.state.cash - self.cash_reserve
        risky_money_balance = player.state.cash - self.second_cash_reserve
        mortgage_money = self.get_mortgage_money_available_excl_owned_set(player)

        # ****************** Params that affect mortgage usage ******************
        self.update_to_build_list(player)
        has_house_to_build_asap = self.has_house_to_build_asap(player)
        has_enough_house = self.has_house_enough(player)
        has_enough_set = False
        if len(player.state.owned_sets) > self.get_max_owned_set(game_state) + 1:
            has_enough_set = True
        # ************************************************************************

        # Buy Deal **********************************************************************

        for i, e in enumerate(self.property_wish_list):
            quote = int((self.BUY_PARM1 * (e[2] - self.BUY_PARM2)
                    * (e[2] - self.BUY_PARM3) + self.BUY_PARM4) * e[0].price * self.buy_parm_fac[e[1].name] * 0.01)

            if has_house_to_build_asap:
                budget = money_balance
                if e[2] >=5:
                    budget += mortgage_money
            elif has_enough_set:
                budget = risky_money_balance
                if e[2] >=5:
                    budget += mortgage_money
            elif has_enough_house:
                budget = risky_money_balance + mortgage_money
                if e[2] <= 3:
                    budget -= mortgage_money
            else:
                budget = money_balance + mortgage_money
                if e[2] <= 3:
                    budget -= mortgage_money

            if quote > budget:
                continue

            if self.is_player_on_blacklist(e[1].name):
                # Logger.log("[PD] This player ({}) is on blacklist".format(e[1].name), log_level)
                continue

            if (e[2] >= 4) and (quote < player.state.cash - self.cash_reserve):
                pending_deal_proposal = DealProposal(propose_to_player=e[1],
                                                     properties_wanted=[e[0]],
                                                     maximum_cash_offered=quote
                )
                # if I've this proposal is same as last three, skip it
                Logger.log("[DPS] {}) {:23s} ({:15s}) evp:({:1.1f}) qt:${:3d}".format(i, e[0].name, e[1].name, e[2], quote), log_level)
                t = (e[0].name, e[1].name, e[2])
                num_tried = 0
                idx = -1
                # is_fac_fixed = self.buy_parm_fac_fixed[e[1].name]
                is_completed = False
                for ii, ee in reversed(list(enumerate(self.last_10_deals_proposed))):
                    Logger.log("[DQ] {}) {:23s} ({:15s}) evp:({:1.1f}) cmpt?({:1b})"
                    .format(ii, ee[0][0], ee[0][1], ee[0][2], ee[1]), log_level)
                    if ee[0] == t:
                        idx = ii
                        is_completed = ee[1]
                        break

                Logger.indent()
                if is_completed:
                    Logger.log("[PD] Completed or Rejected deal", log_level)
                    Logger.dedent()
                    continue
                else:
                    # New Deal
                    if idx < 0:
                        deal_proposal = pending_deal_proposal
                        self.last_10_deals_proposed.append(((e[0].name, e[1].name, e[2]), False))
                        self.buy_quote_amount = deal_proposal.maximum_cash_offered
                        Logger.log("[PD] {} Proposed New Deal to:{},wh:{}, @ ${} evp:{}".format(player.name, e[1].name, e[0].name, quote, e[2]), log_level)
                        Logger.dedent()
                        break
                    # existing Deal
                    else:
                        deal_proposal = pending_deal_proposal
                        self.last_10_deals_proposed.append(((e[0].name, e[1].name, e[2]), False))
                        self.buy_quote_amount = deal_proposal.maximum_cash_offered
                        Logger.log("[PD] {} Proposed deal existing deal to:{},wh:{}, @ ${} evp:{}".format(player.name, e[1].name, e[0].name, quote, e[2]), log_level)
                        Logger.dedent()
                        break
            else:
                a=1
                # if (quote > player.state.cash - self.cash_reserve):
                    # Logger.log("[PD] $$ Couldn't propose deal for {} due to money short nd:${} hv:${} rsv:${}".format(e[0], quote, player.state.cash, self.cash_reserve), log_level)
                # else:
                    # Logger.log("[PD] Didn't propose deal as  eval_point of {} is less than criteria ({}) > ({})".format(e[0], criteria, e[2]), log_level)

        if deal_proposal is not None:
            self.last_deal_proposed_to = deal_proposal.propose_to_player.name
            self.has_just_proposed = True

        Logger.log("[DPEND] --------------------------------------------------------", log_level)
        return deal_proposal

    def deal_result(self, deal_info):
        log_level = Logger.DEBUG
        if self.has_just_proposed:
            self.has_just_proposed = False
            (num_reject, num_received) = self.blacklist[self.last_deal_proposed_to]
            num_received += 1
            # offered too little money
            if deal_info == 3:
                if self.buy_parm_fac[self.last_deal_proposed_to] < self.MAX_BUY_PARM_FAC:
                    self.buy_parm_fac[self.last_deal_proposed_to] += 15
                    self.last_10_deals_proposed.pop()
                    # retry
                    Logger.log("[DR] Retry this ppty : Buy_parm_fac inc by {} for {} to {}".format(15, self.last_deal_proposed_to, self.buy_parm_fac[self.last_deal_proposed_to]), log_level)
                else:
                    pop = self.last_10_deals_proposed.pop()
                    tuple = [pop[0], True]
                    self.last_10_deals_proposed.append(tuple)

                    Logger.log("[DR] Give up this ppty, we've offered enough for {} fac:{}".format(self.last_deal_proposed_to, self.buy_parm_fac[self.last_deal_proposed_to]), log_level)

            # deal succeed
            elif deal_info == 0:
                pop = self.last_10_deals_proposed.pop()
                tuple = (pop[0], True)
                self.last_10_deals_proposed.append(tuple)
            # INVALID_DEAL_PROPOSED = 1 / ASKED_FOR_TOO_MUCH_MONEY = 2 / PLAYER_DID_NOT_HAVE_ENOUGH_MONEY = 4
            elif deal_info == 1 or deal_info == 2 or deal_info == 4:
                Logger.log("Can't Happen (deal result)", Logger.DEBUG)
                return
            else:
                # if just rejected, consider it completed
                pop = self.last_10_deals_proposed.pop()
                tuple = (pop[0], True)
                self.last_10_deals_proposed.append(tuple)
                # black list
                num_reject += 1
                Logger.log("[BF] Give up, this deal it's JUST rejected for no reason".format(self.last_deal_proposed_to), log_level)

            self.blacklist[self.last_deal_proposed_to] = (num_reject, num_received)

    def deal_completed(self, deal_result):
        log_level = Logger.DEBUG

        if deal_result.proposer.name == self.get_name() and len(deal_result.properties_transferred_to_proposer) > 0:
            amount_wanted = deal_result.cash_transferred_from_proposer_to_proposee * 2 - self.buy_quote_amount
            ppty = None
            for x in deal_result.properties_transferred_to_proposer:
                ppty = x
                break

            amount_gap_fac = int(round((self.buy_quote_amount - amount_wanted) / ppty.price, 2) * 100)

            if amount_gap_fac > 10:
                self.buy_parm_fac[deal_result.proposee.name] -= int(amount_gap_fac / 2)
                if self.buy_parm_fac[deal_result.proposee.name] < self.MIN_BUY_PARM_FAC:
                    self.buy_parm_fac[deal_result.proposee.name] = self.MIN_BUY_PARM_FAC
                Logger.log("[DC] Adjust buy_parm_fac dec by ({}) to {} (${}(qt) - ${} (wanted)) / {} (ppty.price) "
                           .format(int(amount_gap_fac / 2), self.buy_parm_fac[deal_result.proposee.name]
                            , self.buy_quote_amount, amount_wanted, ppty.price),log_level)
            else:
                self.buy_parm_fac[deal_result.proposee.name] += 7
                if self.buy_parm_fac[deal_result.proposee.name] > self.MAX_BUY_PARM_FAC:
                    self.buy_parm_fac[deal_result.proposee.name] = self.MAX_BUY_PARM_FAC
                Logger.log("[DC] Adjust buy_parm_fac inc as it was close to wanted px by ({}) to {} (${}(qt) - ${} (wanted)) / {} (ppty.price) "
                           .format(5, self.buy_parm_fac[deal_result.proposee.name]
                            , self.buy_quote_amount, amount_wanted, ppty.price),log_level)

    def get_out_of_jail(self, game_state, player):
        log_level = Logger.DEBUG
        Logger.log("I'm in jail now", log_level)
        if self.get_phase(game_state) < 2:
            if player.state.number_of_get_out_of_jail_free_cards > 0:
                Logger.log("{} Got out of Jail by using jail free card out of {}"
                .format(self.get_name(), player.state.number_of_get_out_of_jail_free_cards), log_level)
                return self.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
            else:
                mortgage_money = self.get_mortgage_money_available_excl_owned_set(player)
                if (player.state.cash + mortgage_money - self.cash_reserve) >= 50:
                    Logger.log("{} Got out of Jail by paying $50".format(self.get_name()), log_level)
                    return self.Action.BUY_WAY_OUT_OF_JAIL
                else:
                    Logger.log("$$ Couldn't escape jail due to money short nd:${} hv:${} rsv:${}".format(50, player.state.cash, self.cash_reserve), log_level)
                    return self.Action.STAY_IN_JAIL
        else:
            Logger.log("It's late phase({}), let's just stay".format(self.get_phase(game_state)), log_level)
            return self.Action.STAY_IN_JAIL

    def player_went_bankrupt(self, player):
        log_level = Logger.DEBUG
        # del self.buy_parm_fac[player.name]
        # del self.buy_parm_fac_fixed[player.name]

        # if player.name == self.get_name():
        #     Logger.log("Shit!,RedLight went Bankrupt", log_level)

    def players_birthday(self):
        return "Happy Birthday!"

    def pay_ten_pounds_or_take_a_chance(self, game_state, player):
        return self.Action.PAY_TEN_POUND_FINE

    def game_over(self, winner, maximum_rounds_played):
        log_level = Logger.DEBUG
        Logger.log("Winner {}'s remaining time is ;{};s".format(winner.name, winner.state.ai_processing_seconds_remaining), log_level)
        # for key, value in self.players_bid_db.items():
        #     # for i, e in enumerate(value):
        #     Logger.log("[{:25s}] : {}".format(key, value),log_level)

    def money_will_be_taken(self, player, amount):
        self.money_taking_moment = True
        self.money_taking_amount = amount
        if self.has_just_holdout_bid:
            self.holdout_snatch = amount

    def money_taken(self, player, amount):
        self.money_taking_moment = False
        self.money_taking_amount = 0

        self.current_cash = player.state.cash
        self.current_anw = self.get_available_net_worth(player)

    def money_given(self, player, amount):
        self.current_cash = player.state.cash
        self.current_anw = self.get_available_net_worth(player)

    def is_player_on_blacklist(self, player_name):
        (num_rejected, num_received) = self.blacklist[player_name]
        if num_received >= 25 and num_rejected == num_received:
            return True
        else:
            return False

    def player_landed_on_square(self, game_state, square, player):
        log_level = Logger.DEBUG
        if player.name == self.get_name():
            # Logger.log("TEST[LO] who:{} @ {}".format(player.name, square.name), log_level)
            # Logger.log("Update cash reserve", log_level)
            self.update_cash_reserve(game_state, player)

    def get_player_idx(self, game_state, player):
        for i, e in enumerate(game_state.players):
            if e.name == player.name:
                return i
        return -1

    def get_player_idx_with_name(self, game_state, player_name):
        for i, e in enumerate(game_state.players):
            if e.name == player_name:
                return i
        return -1

    # def update_players_cash(self, game_state):
    #     self.players_cash.clear()
    #     self.players_cash = {p.name: p.state.cash for p in game_state.players}

    # def get_player_cash(self, player_name):
    #     return self.players_cash[player_name]

    def player_ran_out_of_time(self, player):
        log_level = Logger.DEBUG
        Logger.log("{} ran out of time".format(player.name), log_level)

    def ai_error(self, message):
        Logger.log("AI_ERROR : {}".format(message), Logger.DEBUG)
