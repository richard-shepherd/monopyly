__author__ = 'James'
from monopyly import *


class SimProperty(object):
    #A class for experimenting with the number of houses 
    #on a property without modifying the original

    def __init__(self, original_property):
        self.original_property = original_property
        if original_property is None:
            pass
        if isinstance(original_property, Street):
            self.sim_number_of_houses = original_property.number_of_houses
        else:
            self.sim_number_of_houses=0
        self.sim_owner=None
    
    def __getattr__(self, name):
        return getattr(self.original_property, name)


    def sim_number_of_houses(self):
        return self.sim_number_of_houses


class SimPropertySet():
    def __init__(self, properties):
        self.sim_properties=[]
        for current_prop in properties:
            self.sim_properties.append(SimProperty(current_prop))

