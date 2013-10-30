from collections import namedtuple
from .property import Property


class Street(Property):
    '''
    A type of Property representing a street.

    Manages rents, house-building and so on.
    '''

    def __init__(self, name, street_set, price, house_price, rents):
        '''
        The 'constructor'.

        rents: passed in as a list: [base, one_house, two_houses, three_houses, four_houses, hotel]
        '''
        # The base class holds the values applicable to all properties...
        super().__init__(name, street_set, price)

        # The price of one house on this street...
        self.house_price = house_price

        # The collection of rents as a list:
        # [base, one_house, two_houses, three_houses, four_houses, hotel]
        self.rents = rents

        # The number of houses on the street.
        # This can go up to 5, indicating that the street has a hotel.
        self.number_of_houses = 0

    def landed_on(self, game, player):
        '''
        When a street is landed on we manage whether there is rent
        to pay, or whether the property can be bought.
        '''
        # If the property is already owned by this player, then there
        # is nothing to do...
        if(self.owner_player_number == player.state.player_number):
            return

        # If the property is mortgaged, then there is nothing to do...
        if(self.is_mortgaged):
            return

        if(self.owner_player_number == Property.NOT_OWNED):
            # The property is not owned, so we offer it for sale...
            game.offer_property_for_sale(player, self)
        else:
            # The property is owned by another player (and is not
            # mortgaged), so rent needs to be paid...
            self._pay_rent(game, player)

    def _pay_rent(self, game, player):
        '''
        The player has landed on a square owned by another player
        and must pay rent.
        '''
        # We find the player to pay...
        player_to_pay = game.state.players[self.owner_player_number]

        # Are there any houses?
        if(self.number_of_houses == 0):
            rent = self.rents[0]
            if(self.street_set in player_to_pay.state.owned_sets):
                # The player owns the whole set, so the rent is doubled...
                rent *= 2
        else:
            # The street has houses, so we find the rent for the number
            # of houses there are...
            rent = self.rents[self.number_of_houses]

        # We take the rent from the player, and give it to the
        # player who owns the square...
        amount_taken = game.take_money_from_player(player, rent)
        game.give_money_to_player(player_to_pay, amount_taken)


