class DealProposal(object):
    '''
    Holds details about a deal proposed by one player to another.
    '''

    def __init__(
            self,
            propose_to_player=None,
            properties_offered=None,
            properties_wanted=None,
            maximum_cash_offered=0,
            minimum_cash_wanted=0):
        '''
        The 'constructor'.

        properties_offered and properties_wanted should be passed as lists
        of property names, for example:
        [Square.Name.OLD_KENT_ROAD, Square.Name.BOW_STREET]

        If you offer cash as part of the deal, set maximum_cash_offered and
        set minimum_cash_wanted to zero. And vice versa if you are willing to
        pay money as part of the deal.
        '''
        if (not properties_offered):
            properties_offered = []
        if (not properties_wanted):
            properties_wanted = []

        self.propose_to_player = propose_to_player
        self.properties_offered = properties_offered
        self.properties_wanted = properties_wanted
        self.maximum_cash_offered = maximum_cash_offered
        self.minimum_cash_wanted = minimum_cash_wanted
        self.proposed_by_player = None

    def __str__(self):
        '''
        Renders the proposal as a string.
        '''
        return "Offered: {0}. Wanted: {1}".format(self.properties_offered, self.properties_wanted)

    @property
    def deal_proposed(self):
        '''
        True if a valid deal was proposed, False if not.
        '''
        return True if (self.properties_offered or self.properties_wanted) else False
