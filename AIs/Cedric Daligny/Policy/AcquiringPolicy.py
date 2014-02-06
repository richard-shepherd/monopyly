__author__ = 'Cedric'

from monopyly import *

class AcquiringPolicy(object):
    def __init__(self,ai):
        self.ai = ai
        self.last_offers = []

    def acquire_through_landing(self,game_state,player,property):
        '''
        Called when the AI lands on an unowned property. Only the active
        player receives this notification.

        Must return either the BUY or DO_NOT_BUY action from the
        PlayerAIBase.Action enum.

        The default behaviour is DO_NOT_BUY.
        '''
        if type(property) == Street:
            if property.number_of_houses > 0:
                Logger.log("Trying to acquire a property (through landing) with houses on it " + property.name,Logger.ERROR)

        remaining_after_buying = player.state.cash - property.price
        if self.ai.properties_information[property.name][0] <= remaining_after_buying:
            return PlayerAIBase.Action.BUY
        return PlayerAIBase.Action.DO_NOT_BUY

    def acquire_through_auction(self,game_state,player,property):
        '''
        Called when a property is put up for auction.

        Properties are auctioned when a player lands on an unowned square but does
        not want to buy it. All players take part in the auction, including the
        player who landed on the square.

        The property will be sold to the highest bidder using the eBay rule,
        ie, for £1 more than the second-highest bid.

        Return the amount you bid. To put in a bid this must be a positive integer.
        Zero means that you are not bidding (it does not mean that you are bidding
        zero).

        The default behaviour is not to bid.
        '''
        if type(property) == Street:
            if property.number_of_houses > 0:
                Logger.log("Trying to acquire a property (through auction) with houses on it " + property.name,Logger.ERROR)

        remaining_after_buying = player.state.cash - (property.price * self.ai.properties_information[property.name][3])
        if (self.ai.properties_information[property.name][0] / self.ai.properties_information[property.name][3]) <= remaining_after_buying:
            return property.price * self.ai.properties_information[property.name][3]
        return 0

    def acquire_through_unmortgage(self,game_state,player):
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
        unmortgaged_properties = []
        remaining_after_buying = player.state.cash
        for property in player.state.properties:
            if property.is_mortgaged == True:
                unmortgage_price = (property.price * 0.55)
                if self.ai.properties_information[property.name][0] <= (remaining_after_buying - unmortgage_price):
                    remaining_after_buying -= unmortgage_price
                    unmortgaged_properties.append(property)
        return unmortgaged_properties

    def acquire_through_deal_proposal(self,game_state,player,cash_available):
        '''
        Called to allow the player to propose a deal.

        You return a DealProposal object.

        If you do not want to make a deal, return None.

        If you want to make a deal, you provide this information:
        - The player number of the player you are proposing the deal to
        - A list of properties offered
        - A list of properties wanted
        - Maximum cash offered as part of the deal
        - Minimum cash wanted as part of the deal.

        Properties offered and properties wanted are passed as lists of
        Property objects.

        If you offer money as part of the deal, set the cash wanted to zero
        and vice versa.

        Note that the cash limits will not be shown to the proposed-to player.
        When the deal is offered to them, they set their own limits for accepting
        the deal without seeing your limits. If the limits are acceptable to both
        players, the deal will be done at the halfway point.

        For example, Player1 proposes:
          Propose to: Player2
          Properties offered: Mayfair
          Properties wanted: (none)
          Maximum cash offered: 0
          Minimum cash wanted: 500

        Player2 accepts with these limits:
          Maximum cash offered: 1000
          Minimum cash wanted: 0

        The deal will be done with Player2 receiving Mayfair and paying £750
        to Player1.

        The only 'negotiation' is in the managing of cash along with the deal
        as discussed above. There is no negotiation about which properties are
        part of the deal. If a deal is rejected because it does not contain the
        right properties, another deal can be made at another time with different
        lists of properties.

        Example construction and return of a DealProposal object:
            return DealProposal(
                propose_to_player_number=2,
                properties_offered=[vine_street, bow_street],
                properties_wanted=[park_lane],
                maximum_cash_offered=200)

        The default is for no deal to be proposed.
        '''
        # create the list of property owned by a player not being us
        listed_owned_by_other_properties = []
        for player_inside in game_state.players:
            if player_inside != player:
                for property in player_inside.state.properties:
                    listed_owned_by_other_properties.append([property,self.ai.properties_information[property.name][0]])

        sorted_properties = sorted(listed_owned_by_other_properties,key=lambda elem:elem[1],reverse=True)

        if len(self.last_offers) > 5 or len(self.last_offers) >= len(sorted_properties) - 2:
            self.last_offers = []

        for prop_elem in sorted_properties:
            remaining_after_buying = cash_available - (prop_elem[0].price * self.ai.properties_information[prop_elem[0].name][1])
            if (self.ai.properties_information[prop_elem[0].name][0] / self.ai.properties_information[prop_elem[0].name][1]) <= remaining_after_buying and self.last_offers.count(prop_elem[0]) == 0:
                if type(prop_elem[0]) != Street:
                    self.last_offers.append(prop_elem[0])
                    return DealProposal(
                        propose_to_player=prop_elem[0].owner,
                        properties_offered=[],
                        properties_wanted=[prop_elem[0]],
                        maximum_cash_offered=(prop_elem[0].price * self.ai.properties_information[prop_elem[0].name][1]) )
                elif prop_elem[0].number_of_houses == 0:
                    self.last_offers.append(prop_elem[0])
                    return DealProposal(
                        propose_to_player=prop_elem[0].owner,
                        properties_offered=[],
                        properties_wanted=[prop_elem[0]],
                        maximum_cash_offered=(prop_elem[0].price * self.ai.properties_information[prop_elem[0].name][1]) )
        return None

    def acquire_through_deal_being_proposed(self,game_state,player,deal_proposal):
        '''
        Called when another player proposes a deal to you.

        See propose_deal (above) for details of the DealProposal object.

        Return a DealResponse object.

        To reject a deal:
            return DealResponse(DealResponse.Action.REJECT)

        To accept a deal:
            return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=300)
            or
            return DealResponse(DealResponse.Action.ACCEPT, minimum_cash_wanted=800)

        The default is to reject the deal.
        '''
        if len(deal_proposal.properties_wanted) == 0 or len(deal_proposal.properties_offered) != 1:
            return DealResponse(DealResponse.Action.REJECT)

        property = deal_proposal.properties_offered[0]
        if type(property) == Street:
            if property.number_of_houses > 0:
                Logger.log("Trying to acquire a property (through being proposed) with houses on it " + property.name,Logger.ERROR)

        remaining_after_buying = player.state.cash - (property.price * self.ai.properties_information[property.name][2])
        if (self.ai.properties_information[property.name][0] / self.ai.properties_information[property.name][2]) <= remaining_after_buying:
            return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=property.price * self.ai.properties_information[property.name][2])
        
        # Default to rejecting the deal...
        return DealResponse(DealResponse.Action.REJECT)