
class DealResult(object):
    '''
    Details of a deal that has taken place.
    '''
    def __init__(self):
        self.proposer = None
        self.proposee = None
        self.properties_transferred_to_proposer = []
        self.properties_transferred_to_proposee = []
        self.cash_transferred_from_proposer_to_proposee = 0

