
class MockDice(object):
    '''
    A mock for the Dice class.

    You can control what the dice will return for the next set of rolls.
    '''
    def __init__(self, roll_results = []):
        '''
        The 'constructor'

        You can optionally pass an initial set of roll results.
        '''
        self._roll_results = roll_results
        self._next_roll_index = 0

    def set_roll_results(self, roll_results):
        '''
        You provide the results of the next rolls as a list of tuples
        of the values of the two dice. For example:
        [(3, 4), (1, 5), (6, 4)]
        '''
        self._roll_results = roll_results
        self._next_roll_index = 0

    def roll(self):
        '''
        Returns the next rolls from the results.
        '''
        # We check if we have results to return...
        if(self._next_roll_index >= len(self._roll_results)):
            raise Exception("next_roll_index out of range")

        # We get the next rolls and return them...
        rolls = self._roll_results[self._next_roll_index]
        self._next_roll_index += 1
        return rolls[0], rolls[1]


