from .square import Square
from ..utility import Logger


class Property(Square):
    '''
    A base class for properties, which manages some common features
    of them.

    This include holding whether the property is owned (and if so, who by)
    and whether the property is mortgaged.

    Derived classes are: Street, Station, Utility.
    '''

    def __init__(self, name, property_set, price):
        '''
        The 'constructor'.
        '''
        super().__init__(name)

        # We store the set (BROWN, ORANGE etc, a PropertySet object), and add
        # this property to the set...
        self.property_set = property_set
        self.property_set.add_property(self)

        # The full price of the property.
        # The mortgage price is half of this price.
        self.price = price

        # True if the property is mortgaged...
        self.is_mortgaged = False

        # The owner (a Player object)...
        self.owner = None

    @property
    def mortgage_value(self):
        '''
        The mortgage value
        '''
        return int(self.price / 2)

    def landed_on(self, game, player):
        '''
        When a property is landed on we manage whether there is rent
        to pay, or whether the property can be bought.
        '''
        # If the property is already owned by this player, then there
        # is nothing to do...
        if self.owner is player:
            Logger.log("{0} already owns this property".format(player.name))
            return

        # If the property is mortgaged, then there is nothing to do...
        if self.is_mortgaged:
            Logger.log("Property is mortgaged")
            return

        if self.owner is None:
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
        from ..game import Game

        # We find the amount to pay...
        rent = self.calculate_rent(game, player)

        # We take the rent from the player, and give it to the
        # player who owns the square...
        Logger.log("{0} must pay rent of £{1} to {2}".format(player.name, rent, self.owner.name))
        game.transfer_cash(player, self.owner, rent, Game.Action.PAY_AS_MUCH_AS_POSSIBLE)

    def calculate_rent(self, game, player):
        '''
        Derived classes must implement this method.

        Returns the rent to be paid.
        '''
        raise Exception("calculate_rent not implemented")


