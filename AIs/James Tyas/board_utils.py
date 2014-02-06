__author__ = 'James'
from monopyly import *
from .property_probs_calcs import PropertyProbCalcs


class BoardUtils():
    def __init__(self, property_probs):
        self.property_probs = property_probs
        pass

    def get_list_of_complete_sets_i_own(self, board, my_own_player):
        property_sets_i_own = None
        all_players_sets = board.get_owned_sets(False)
        for player in all_players_sets:
            if my_own_player.is_same_player(player):
                #Weve found our self
                property_sets_i_own=all_players_sets[player]
                break

        return property_sets_i_own

    def get_properties_i_own_with_houses(self, board, my_own_player):
        all_properties_i_own = self.get_properties_i_own(board, my_own_player)
        properties_i_own_with_houses = []
        for property in all_properties_i_own:
            if isinstance(property, Street):
                if property.number_of_houses > 0:
                    properties_i_own_with_houses.append(property)
        return properties_i_own_with_houses


    def get_properties_i_own(self, board, my_own_player):
        properties_i_own=[]
        for property_set in self.get_all_property_sets():
            for check_property in board.get_properties_for_set(property_set):
                if check_property.owner == my_own_player:
                    properties_i_own.append(check_property)
        return properties_i_own
  
    def get_streets_i_own(self, board, my_own_player):
        streets_i_own=[]
        for property_set in self.get_all_property_sets():
            for check_property in board.get_properties_for_set(property_set):
                if check_property.owner == my_own_player and isinstance(check_property, Street):
                    streets_i_own.append(check_property)
        return streets_i_own

    def get_all_property_sets(self):
        #Returns a collection of all property sets
        all_property_sets = []
        all_property_sets.append(PropertySet.BROWN)
        all_property_sets.append(PropertySet.LIGHT_BLUE)
        all_property_sets.append(PropertySet.PURPLE)
        all_property_sets.append(PropertySet.ORANGE)
        all_property_sets.append(PropertySet.RED)
        all_property_sets.append(PropertySet.YELLOW)
        all_property_sets.append(PropertySet.GREEN)
        all_property_sets.append(PropertySet.DARK_BLUE)
        all_property_sets.append(PropertySet.STATION)
        all_property_sets.append(PropertySet.UTILITY)
        return all_property_sets

    def is_station(self, property_name):
        #Check to see if a property is a station or not

        if (property_name in (Square.Name.KINGS_CROSS_STATION, Square.Name.FENCHURCH_STREET_STATION,
                              Square.Name.LIVERPOOL_STREET_STATION, Square.Name.MARYLEBONE_STATION)):
            return True
        return False

    def number_of_stations_owned(self, board, player):
        num_stations_owned = 0
        for prop in board.get_properties_for_set(PropertySet.STATION):
            if not prop.owner is None and player.is_same_player(prop.owner):
                num_stations_owned = num_stations_owned + 1
        return num_stations_owned

    def is_utility(self, property_name):
        #is this property a utility?
        if (property_name in (Square.Name.ELECTRIC_COMPANY, Square.Name.WATER_WORKS)):
            return True
        return False

    def remove_house_from_property_in_list(self, property, property_list_with_houses):
        #Removes a house from a property in a list
        remaining_list=property_list_with_houses
        #Subtract one house from the property
        remaining_list = [i for i in remaining_list if i is not None]
        for idx, item in enumerate(remaining_list):
            if not property.original_property is None:
                if not item is None:
                    if property.name == item.name:
                        new_item=item
                        new_item.sim_number_of_houses-=1
                        remaining_list[idx] = new_item
                        break
        return remaining_list

    def get_properties_owned_by_others(self, board, my_own_player):
        properties_owned_by_others=[]
        for check_property in board.squares:
            if isinstance(check_property, Property):
                if not my_own_player.is_same_player(check_property.owner):
                    properties_owned_by_others.append(check_property)
        return properties_owned_by_others

    def get_total_expected_loss_per_roll_all_players(self, board, my_own_player):
        properties_owned_by_others=self.get_properties_owned_by_others(board, my_own_player)
        total_expected_loss=0
        for property in properties_owned_by_others:
            #TODO: Stations and utilities
            if isinstance(property, Street):
                set_owned = not property.property_set.owner is None
                total_expected_loss+=self.property_probs.income_per_turn(property.name, property.number_of_houses, set_owned)
        return total_expected_loss

    def percentage_of_property_set_owned_by_player(self, board, player, property_set):
        num_of_properties_in_set=0
        num_of_owned_properties_in_set=0
        for prop in board.squares:
            if isinstance(prop, Property) and prop.property_set == property_set:
                num_of_properties_in_set = num_of_properties_in_set + 1
                if (player is None and prop.owner is None) or (not player is None and player.is_same_player(prop.owner)):
                    num_of_owned_properties_in_set= num_of_owned_properties_in_set + 1
        if num_of_properties_in_set == 0:
            #Shouldn't happen
            return 0
        return (num_of_owned_properties_in_set/num_of_properties_in_set) * 100

    def max_percentage_of_property_owned_by_single_player(self, game_state, property_set):
        max_percentage_owned = 0
        for player in game_state.players:
            percentage_owned_by_player = self.percentage_of_property_set_owned_by_player(game_state.board, player, property_set)
            if max_percentage_owned < percentage_owned_by_player:
                max_percentage_owned = percentage_owned_by_player
        return max_percentage_owned

    def max_loss_single_roll(self,game_state, my_own_player):
        #Returns the maximum possible loss for a single roll
        #the intention being to avoid going bankrupt
            #Loop through all squares from 2 to 12 away
            # and if they are a property - and I'm not the owner, calculate the rent
            max_rent_found=0
            for square in game_state.board.squares:
                distance_to_square = self.forward_number_of_squares_from_player_to_prop(game_state.board, square, my_own_player)
                if 2 <= distance_to_square <=12:
                    if isinstance(square,Property) and not  square.owner is None and not square.owner.is_same_player(my_own_player) :
                        current_rent_calc = self.calculate_rent(square, game_state,my_own_player)
                        if max_rent_found < current_rent_calc:
                            max_rent_found = current_rent_calc
            return max_rent_found

    def calculate_rent(self, property,game_state, player):
        #Don't have access to GAME so calculate rent ourselves
        if isinstance(property, Street):
            return property.calculate_rent(game_state, player)
        if isinstance(property, Station):
            return self.rent_for_stations(self.stations_owned_by_a_player(property.owner, game_state))
        if isinstance(property, Utility):
            return self.average_rent_for_utility(self.utilities_owned_by_a_player(property.owner,game_state))

    def stations_owned_by_a_player(self, player, game_state):
        num_stations_owned=0
        for station in game_state.board.get_properties_for_set(PropertySet.STATION):
            if not station.owner is None and player.is_same_player(station.owner):
                num_stations_owned = num_stations_owned +1
        return num_stations_owned

    def utilities_owned_by_a_player(self, player, game_state):
        num_utilities_owned=0
        for utility in game_state.board.get_properties_for_set(PropertySet.UTILITY):
            if not utility.owner is None and player.is_same_player(utility.owner):
                num_utilities_owned = num_utilities_owned +1
        return num_utilities_owned

    def average_rent_for_utility(self,number_of_utilities_owned):
        #We can't access the dice, so let's average the rent
        rent_prices=[28,70]
        return rent_prices[number_of_utilities_owned-1]

    def rent_for_stations(self, number_of_stations_owned):
        rent_prices=[25,50,100,200]
        return rent_prices[number_of_stations_owned-1]


    def forward_number_of_squares_from_player_to_prop(self,board, property, player):
        #Calculate how many squares forward it is to a particular square from where the player is now
        square_number=board.get_index(property.name)
        if player.state.square < square_number:
            return square_number-player.state.square
        #The square is behind us
        return 40-player.state.square + square_number

