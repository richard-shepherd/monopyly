from monopyly import *
from random import *
from .jamestyasbasics import *

class Bachelorette(JamesTyasBasicsAI):
    '''
    This AI counts its number of turns in a game

    '''
    def __init__(self):
        self.total_games = 0
        self.total_turns = 0
        self.panic_selling = 0
        self.turn_amount_owed = 0
        self.property_probs=PropertyProbCalcs()
        self.board_utils=BoardUtils(self.property_probs)
        self.decision_utils=DecisionUtils(self.property_probs)
        self.turndealcount=0

    def get_name(self):
        return "Bachelorette"

    def propose_deal(self, game_state, player):
        return None