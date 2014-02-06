__author__ = 'James'
from monopyly import *


class PropertyProb():
    def __init__(self, property_name, rolls_recoup_single_prop
                , rolls_recoup_all_sets, rolls_recoup_houses,
                income_single_prop, income_all_sets, income_houses):
        # Structure to store various probabilities
        # and calculations on a property
        # indexed by name
        # rolls_recoup_house expects a list 1-5 of rolls to recoup
        # income_houses expects a list 1-5 of income
        self._property_name = property_name
        self._rolls_recoup_houses = rolls_recoup_houses
        self.rolls_recoup_single_prop = rolls_recoup_single_prop
        self.rolls_recoup_all_sets = rolls_recoup_all_sets
        self.income_single_prop = income_single_prop
        self.income_all_sets = income_all_sets
        self._income_houses = income_houses

    def rolls_to_recoup(self, number_of_houses):
        if number_of_houses == 0:
            return self.rolls_recoup_all_sets
        if number_of_houses>5:
            return 99999
        return self._rolls_recoup_houses[number_of_houses-1]

    def income(self, number_of_houses):
        if number_of_houses > 5:
            return 0
        if number_of_houses == 0:
            return self.income_single_prop
        return self._income_houses[number_of_houses-1]

class StationProb():
    def __init__(self, property_name, list_rolls_recoup_station, list_income_station):
        #expects a list of 1,2,3,4 stations owned for each probability
        self._property_name=property_name
        self.list_income_station = list_income_station
        self.list_rolls_recoup_station=list_rolls_recoup_station

    def rolls_to_recoup(self, number_stations_owned):
        return self.list_rolls_recoup_station[number_stations_owned-1]

    def income(self, number_stations_owned):
        return self.list_income_station[number_stations_owned-1]
