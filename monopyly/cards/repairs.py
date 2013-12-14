from .card import Card
from ..utility import Logger


class Repairs(Card):
    '''
    "Make general repairs..." and "You are assessed for street repairs..."
    '''

    def __init__(self, amount_per_house, amount_per_hotel):
        '''
        The 'constructor'.
        '''
        self.amount_per_house = amount_per_house
        self.amount_per_hotel = amount_per_hotel

    def play(self, game, current_player):
        '''
        Takes money from the player depending on the number of houses
        and hotel they have.
        '''
        # We work out how much must be paid...
        number_of_houses, number_of_hotels = current_player.state.get_number_of_houses_and_hotels(game.state.board)
        amount = self.amount_per_house * number_of_houses + self.amount_per_hotel * number_of_hotels

        Logger.log("{0} has been assessed for street repairs".format(current_player.name))
        Logger.indent()

        # And take the money...
        game.take_money_from_player(current_player, amount)

        Logger.dedent()

