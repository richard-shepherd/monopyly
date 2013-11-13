
class DealResponse(object):
    '''
    The response to a deal from the proposed-to player.
    '''

    class Action(object):
        '''
        An 'enum' for the actions to accept or reject a deal.
        '''
        ACCEPT = 0
        REJECT = 1

    def __init__(
            self,
            action,
            maximum_cash_offered=0,
            minimum_cash_wanted=0):
        '''
        The 'constructor'.

        The action is one of the DealResponse.Action 'enums'.
        '''
        self.action = action
        self.maximum_cash_offered = maximum_cash_offered
        self.minimum_cash_wanted = minimum_cash_wanted

