
class MockDice(object):
    '''
    A mock for the Dice class.

    You can control what the dice will return for the next set of rolls.
    '''
    def __init__(self):
        '''
        The 'constructor'
        '''
        self.roll_results = []
        self.next_roll_index = 0

    def set_roll_results(self, roll_results):
        '''
        You provide the results of the next rolls as a list of tuples
        of the values of the two dice. For example:
        [(3, 4), (1, 5), (6, 4)]
        '''
        self.roll_results = roll_results
        self.next_roll_index = 0

    def roll(self):
        '''
        Returns the next rolls from the results.
        '''
        # We check if we have results to return...
        if(self.next_roll_index >= len(self.roll_results)):
            raise Exception("next_roll_index out of range")

        # We get the next rolls and return them...
        rolls = self.roll_results[self.next_roll_index]
        self.next_roll_index += 1
        return rolls[0], rolls[1]


