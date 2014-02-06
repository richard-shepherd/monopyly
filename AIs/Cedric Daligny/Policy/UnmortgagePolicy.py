__author__ = 'Cedric'

from monopyly import *

class UnmortgagePolicy(object):
    def __init__(self):
        '''
        ctor
        '''

    def compute(self, game_state, player):
        '''
        Called near the start of the player's turn to give them the
        opportunity to unmortgage properties.

        Unmortgaging costs half the face value plus 10%. Between deciding
        to unmortgage and money being taken the player will be given the
        opportunity to make deals or sell other properties. If after this
        they do not have enough money, the whole transaction will be aborted,
        and no properties will be unmortgaged and no money taken.

        Return a list of property names to unmortgage, like:
        [old_kent_road, bow_street]

        The properties should be Property objects.

        The default is to return an empty list, ie to do nothing.
        '''
        result = []
        remain_cash = player.state.cash - 150;
        for property in player.state.properties:
            if property.is_mortgaged == True:
                if (property.price /2) * 1.1 < remain_cash:
                    remain_cash -= (property.price /2) * 1.1
                    result.append(property.name)
        return result
