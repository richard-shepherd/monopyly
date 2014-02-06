import os
import random
import monopyly

TOURNAMENT = True # enable this just before I submit to disable the debug code
NBR_OWNABLE = 28


def ExceptionSafe(defaultReturnValue) :
    def ExceptionSafeDecorator(undecoratedFunc) :
        def DecoratedFunc(*args, **kwargs) :
            try :
                return undecoratedFunc(*args, **kwargs)
            except :
                if not TOURNAMENT :
                    #os.abort()
                    print('Exception from ' + undecoratedFunc.__name__)
                return defaultReturnValue
        return DecoratedFunc

    return ExceptionSafeDecorator

class EdmundAI(monopyly.PlayerAIBase) :
    '''
    A cunning AI
    '''

    def __init__(self) :
        self.__Reset()


    def __Reset(self) :
        self._nbrPlayersStarted = 0
        self._nbrEminentDomainStreetAuctions = 0
        self._dealInProgress = None
        self._acceptedDeals = []
        self._whiteChapel = None
        self._oldKentRoad = None
        self._otherPlayers = []
        self._previouslyProposedDeals = {} # key = deal(propToGive, propToGet) value = maxPriceProposed
        self._nbrAuctions = 0
        self._nbrSuccessfulDeals = 0
        self._nbrSuccessfulDealsWithMe = 0
        self._squareCount = {}
        self._turnCounter = 0
        self._areAllPropertiesSold = False
        self.__toBeMortgaged = []
        self.__housesToSell = []
        self._player = None
        self._gameState = None
        self._gotGOOJF = False # have I got a "get out of jail free" card
        self._cashReserve = 150
        self._scores = {} # key=player name, value = [score, hasHousesBool]

        # when money will be taken these flags tell us if its a debt or a purchase
        self._auctionInProgress = False
        self._propertyPurchaseInProgress = False


    def _DealAccept(self, dealResponse) :
        self._dealInProgress = (False, dealResponse)
        return dealResponse


    def _DealReject(self):
        return monopyly.DealResponse(monopyly.DealResponse.Action.REJECT)


    def _DealResult(self, dealInfoEnum) :
        if dealInfoEnum == monopyly.PlayerAIBase.DealInfo.SUCCEEDED :
            self._nbrSuccessfulDealsWithMe += 1

            # DealResponse or DealProposal
            if isinstance(self._dealInProgress[1], monopyly.DealProposal) :
                direction = 'proposed'
                deal = self._dealInProgress[1]
                propIGive = str(deal.properties_offered)
                propIGet = str(deal.properties_wanted)
                maxCashToGive = deal.maximum_cash_offered
                minCashToGet = deal.minimum_cash_wanted
            else :
                direction = 'accepted'
            if not TOURNAMENT :
                pass
        return
            # TODO
        print('Deal Succeeded - %s : gave %s for %s (%d offered, %d wanted)' \
                      % (direction, propIGive, propIGet, maxCashToGive, minCashToGet))


    def _DealPropose(self, dealProposal) :
        # TODO fix bug (can't propose deals on properties with houses)
        #if not TOURNAMENT :
        #    print(str(dealProposal.properties_offered))
        #    print(str(dealProposal.properties_wanted))
        #    print(dealProposal.propose_to_player.name)

        self._dealInProgress = (True, dealProposal)
        return dealProposal

    def _DealBuyOneProperty(self) :
        if random.choice([0, 1]) == 0 :
            # try to get the browns (not valued highly so ppl might be willing to sell at > 3* price)
            price = 0
            if self._whiteChapel.owner is not None and self._whiteChapel.owner != self._player :
                prop, price = self._whiteChapel, self._whiteChapel.price * 3
            elif self._oldKentRoad.owner is not None and self._oldKentRoad.owner != self._player :
                prop, price = self._oldKentRoad, self._oldKentRoad.price * 3
            if price > 0 :
                price += random.randint(0, 50)
                if self._player.state.cash < 2 * price :
                    return None
                return self._DealPropose(monopyly.DealProposal(
                            propose_to_player = prop.owner,
                            properties_offered = [],
                            properties_wanted = [prop],
                            maximum_cash_offered = price))

        victim = random.choice(self._otherPlayers)
        if not victim.state.properties :
            return None
        prop = random.choice(list(victim.state.properties))

        rnd = float(random.randint(1, 5)) / 10
        if self.__winning :
            multiplier = 1 - rnd
        elif self._player.state.cash > 500 :
            multiplier = 1 + rnd
        else :
            multiplier = 1 - rnd

        price = int( prop.price * multiplier ) # price will be between 70% - 170% of original price
        if self._player.state.cash < 2 * price :
            return None
        return self._DealPropose(monopyly.DealProposal(
                propose_to_player = victim,
                properties_offered = [],
                properties_wanted = [prop],
                maximum_cash_offered = price))


    def _DealSinglePropWanted(self, player, propWanted) :
        # TODO
        return self._DealReject()
        '''
        if isinstance(propWanted, monopyly.Street) and propWanted.number_of_houses > 0 :
            return monopyly.DealResponse(monopyly.DealResponse.Action.REJECT)
        if len(propWanted.property_set.owners) == 1 :
            return monopyly.DealResponse(monopyly.DealResponse.Action.REJECT)
        if self._NbrPropertiesPlayerNeedsForSet(self._player, propWanted) == 1 :
            return monopyly.DealResponse(monopyly.DealResponse.Action.REJECT)

        TODO reject if player would get a set
        '''

    def _DealSinglePropOffered(self, propOffered) :
        if propOffered.name in self._UnWantedProperties() :
            return self._DealReject()

        playerWouldCompleteSet = (self._NbrPropertiesPlayerNeedsForSet(self._player, propOffered) == 1)

        if playerWouldCompleteSet :
            price = min(propOffered.price * 3, self._player.state.cash - 50)
        else :
            if self._IsPropertyAvailable() != 0 :
                price = propOffered.price / 0.7
            else :
                price = min(self._player.state.cash / 2, propOffered.price * 2)
        return self._DealAccept(
                monopyly.DealResponse(
                    action = monopyly.DealResponse.Action.ACCEPT,
                    maximum_cash_offered = int(price)))


    def _DealCalcPriceForSwap(self, propIGet, propIGive, priceIPreviouslyProposed) :
        '''Swap where both parties get a set. Return >0 to offer money, <0 to want money'''
        setIGet = propIGet.property_set
        setEnemyGets = propIGive.property_set

        _, myAverageSetRentHotels = GetPropertySetAverageRents(setIGet.set_enum)
        _, enemyAverageSetRentHotels = GetPropertySetAverageRents(setEnemyGets.set_enum)

        enemyScore = self._GetPlayerPropertySetScore(propIGet.owner) + enemyAverageSetRentHotels
        myScore = self._GetPlayerPropertySetScore(self._player) + myAverageSetRentHotels
        enemyPlayer = propIGet.owner

        price = Deal.Decision(self._player.state.cash,
                              enemyPlayer.state.cash,
                              myScore - enemyScore)
        if price == Deal.NO :
            return Deal.NO

        # >0 means I give money,   <0 means I want money
        if isinstance(price, float) :
            price = (self._player.state.cash * price) if price > 0 else (enemyPlayer.state.cash * price)

        return int(price)



    def _SetEminentDomainStrategy(self):
        self._EminentDomainAuction = self._EminentDomainAuctionStrategy3
        # within strategy 1 we can choose different sets to focus on
        self._eminentDomainAuctionHighPriceFactor = 0.95 # bid price is this factor * my cash if I really want it
        self._eminentDomainAuctionLowPriceFactor = 0.8   # bid price is this factor * prop price if I don't really want it


    def _EminentDomainAuctionStrategy3(self, prop):
        if prop.name in self._UnWantedProperties() :
            return 41
        if not isinstance(prop, monopyly.Street) :
            return prop.price * self._eminentDomainAuctionLowPriceFactor
        remainingAuctions = (22 + 1 - self._nbrEminentDomainStreetAuctions)
        return self._player.state.cash / remainingAuctions


    def _EminentDomainAuctionStrategy2(self, prop):
        # Stop any other player getting a set and get stations
        if prop.name in self._UnWantedProperties() :
            return 41
        if isinstance(prop, monopyly.Station) :
            return prop.price * self._eminentDomainAuctionHighPriceFactor
        for p in self._otherPlayers :
            nbrNeeded = self._NbrPropertiesPlayerNeedsForSet(p, prop)
            if nbrNeeded == 1 :
                return self._player.state.cash * self._eminentDomainAuctionHighPriceFactor
        return prop.price * self._eminentDomainAuctionLowPriceFactor


    def _EminentDomainAuctionStrategy1(self, prop):
        # Try to get a set score of > 200 and stop anyone else getting sets.
        if prop.name in self._UnWantedProperties() :
            return 41

        if not isinstance(prop, monopyly.Street) :
            return prop.price * self._eminentDomainAuctionLowPriceFactor

        propertySetScore = self._GetPlayerPropertySetScore(self._player)
        buy = False
        nbrOwners = len(prop.property_set.owners)

        if propertySetScore > 200 :
            buy = False # should be enough to win so save the cash for houses.
        elif nbrOwners == 0 or (nbrOwners == 1 and prop.property_set.owners[0][0] == self._player) :
            buy = True

        # override the above decision if we need to stop a player getting a set.
        for player in self._otherPlayers :
            nbrNeeded = self._NbrPropertiesPlayerNeedsForSet(player, prop)
            if nbrNeeded == 1 :
                buy = True
                break

        if not buy :
            return prop.price * self._eminentDomainAuctionLowPriceFactor
        return self._eminentDomainAuctionHighPriceFactor * self._player.state.cash


    def _Output(self) :
        # write an info file to show whats going on

        lines = []
        with open(r'c:\temp\monopoly.txt', 'w') as fileObj :
            lines.append('Turn: %d, nbr auctions: %d' % (self._turnCounter, self._nbrAuctions))
            notWinning = ''
            if not self.__winning :
                notWinning = 'NOT '
            lines.append('I am %swinning' % notWinning)
            lines.append('Properties remain: %d' % self._GetNbrAvailableProperties())

            for player in self._gameState.players :
                propScore, setScore, hasHouses = self._scores.get(player.name, (0,0,False))
                lines.append('------------------------------')
                lines.append('PLAYER: %s  - prop(%d), score(%d) £%d' % (player.name, len(player.state.properties), propScore, player.state.cash))
                lines.append('PropertySet Score = %d, has houses = %s' % (setScore, str(hasHouses)))
                lines.append('\tOwned: ')
                for prop in player.state.properties :
                    propText = '\t\t%s' % prop.name
                    if prop.is_mortgaged :
                        propText += ' - MORTGAGED!'
                    if isinstance(prop, monopyly.Street) and prop.number_of_houses > 0:
                        propText += ' - %d houses' % prop.number_of_houses
                    lines.append(propText)
            fileObj.write('\n'.join(lines))


    def _OutputSquareFrequency(self):
        squareFrequencyText = []

        tmp = [(squareName, count) for squareName, count in self._squareCount.items()]
        tmp.sort(key=lambda x : x[1], reverse=True)

        for s, c in tmp :
            sqIndex = self._gameState.board.get_index_list(s)[0]
            sq = self._gameState.board.squares[sqIndex]
            if isinstance(sq, monopyly.Street) :
                rents = (c * sq.rents[0], c * sq.rents[5]) # no houses, hotel
            else :
                rents = (0,0)
            squareFrequencyText.append('{0} , {1} , {2} , {3}'.format(s.ljust(30, ' '), c, rents[0], rents[1]))
        monopyly.Logger.log('\n' + '\n'.join(squareFrequencyText), monopyly.Logger.INFO)
        monopyly.Logger.log('Total squares landed on = {0}'.format(sum(self._squareCount.values())), monopyly.Logger.INFO )


    def _OnAllPropertiesSold(self):
        self._areAllPropertiesSold = True
        monopyly.Logger.log('All property sold at turn {0}'.format(self._turnCounter))


    def _UnWantedProperties(self) :
        return [
            'Electric Company',
            'Water Works'
        ]


    def _PropertyNeededForSet(self, prop) :
        if prop.property_set.owners :
            for (owner, numOwned, fractionOwned) in prop.property_set.owners :
                if owner.name == self._player.name :
                    return True
        return False


    def _GetOtherPlayersCash(self) :
        return [ player.state.cash for player in self._otherPlayers ]


    def _GetNbrAvailableProperties(self) :
        # total nbr of prop = brown, blue, pink, orange, red, yellow, green, purple, 4stns, 2utils. = 28.
        nbrAvailableProperties = 0
        for square in self._gameState.board.squares :
            if isinstance(square, monopyly.Property) :
                if square.owner is None and not square.is_mortgaged:

                    # I think there is a minor bug
                    # property for a bankrupt player has owner set to None
                    # but is_mortgaged might remain at True so the property can not be resold

                    nbrAvailableProperties += 1

        return nbrAvailableProperties


    def _GetNbrOwnedProperties(self) :
        return NBR_OWNABLE - self._GetNbrAvailableProperties()


    def _IsPropertyAvailable(self) :
        return self._GetNbrAvailableProperties() != 0


    def _SelectPropertiesToMortgage(self, mustRaiseCash) :
        mortgageCandidates = []
        for prop in self._player.state.properties :
            if prop.is_mortgaged :
                continue
            if isinstance(prop, monopyly.Street) :
                if prop.number_of_houses > 0 :
                    continue
                if not mustRaiseCash and self._IsSetOwned(prop) :
                    continue
            mortgageCandidates.append(prop)
        mortgageCandidates.sort(key = lambda x : x.price, reverse = True)
        return mortgageCandidates


    def _SelectHousesToSell(self, cashNeeded) :
        toSell = {}
        cashRaised = 0
        while cashNeeded > cashRaised :
            newCashRaised = 0
            for propertySet in self._player.state.owned_sets :
                if not propertySet.can_build_houses :
                    continue
                mostHouses = [None, 0] # prop, nbrHouses
                for prop in propertySet.properties :
                    # find the property with the most houses
                    nbrRemainingHouses = prop.number_of_houses - toSell.get(prop, 0)
                    if nbrRemainingHouses > mostHouses[1] :
                        mostHouses[0] = prop
                        mostHouses[1] = nbrRemainingHouses
                if mostHouses[0] is not None :
                    if prop not in toSell :
                        toSell[prop] = 0
                    toSell[prop] += 1
                    newCashRaised += prop.house_price / 2
                if cashNeeded <= cashRaised + newCashRaised :
                    break
            if newCashRaised == 0 :
                break
            cashRaised += newCashRaised

        return [(k, v) for k, v in toSell.items()], cashRaised


    def _IsSetOwned(self, prop) :
        return prop.property_set.owner is not None and prop.property_set.owner.name == self._player.name


    def _GetPlayerPropertyScore(self, player) :
        score = 0
        for prop in player.state.properties :
            score += self._GetPropertyScore(prop)

        for propertySet in self._player.state.owned_sets :
            for prop in propertySet.properties :
                score += self._GetPropertyScore(prop)
        return score


    def _PlayerHasHouses(self, player) :
        for prop in player.state.properties :
            if isinstance(prop, monopyly.Street) and prop.number_of_houses > 0 :
                return True
        return False


    def _GetPropertyScore(self, prop) :
        if isinstance(prop, monopyly.Street) :
            return prop.rents[0]
        if isinstance(prop, monopyly.Station) :
            return 50
        if isinstance(prop, monopyly.Utility) :
            return 50
        return 0


    def _GetPlayerPropertySetScore(self, player) :
        score = 0
        for propertySet in player.state.owned_sets :
            # .owners list of (owner, numOwned, fractionOwned)
            if len(propertySet.owners) == 1 and propertySet.owners[0][2] == 1 :
                score += GetPropertySetScore(propertySet.set_enum)
        return score


    # Methods called by the game

    def get_name(self) :
        '''
        Returns the name shown for this AI.
        '''
        return 'Edmund'


    def start_of_game(self):
        '''
        Called at the start of the game.
        No response is required.
        '''
        self.__Reset()


    def start_of_turn(self, gameState, player):
        '''
        Called when an AI's turn starts. All AIs receive this notification.
        No response is required.
        '''

        # store state, player
        if self._gameState is None :
            self._gameState = gameState
            self._otherPlayers = [p for p in self._gameState.players if p.name != self.get_name()]
            self._nbrPlayersStarted = len(self._gameState.players)
            self._oldKentRoad = self._gameState.board.get_square_by_name(monopyly.Square.Name.OLD_KENT_ROAD)
            self._whiteChapel = self._gameState.board.get_square_by_name(monopyly.Square.Name.WHITECHAPEL_ROAD)
            InitialisePropertyInfo(self._gameState.board.squares)

        if self._player is None :
            for player in self._gameState.players :
                if player.name == self.get_name() :
                    self._player = player
                    break

        # calculate player scores
        try :
            #monopyly.Logger.log("{0} Score {1}".format(player.name, score))
            scoreItem = self._scores[player.name] = [0, 0, False] # prop_score, set_score, has_houses
            scoreItem[0] = self._GetPlayerPropertyScore(player)
            scoreItem[1] = self._GetPlayerPropertySetScore(player)
            scoreItem[2] = self._PlayerHasHouses(player)
        except :
            if not TOURNAMENT : raise
        #totalScore = 0
        #for prop in self._gameState.board.squares :
        #    totalScore += self.__GetPropertyScore(prop)
        #totalScore *= 2 # with this method totalScore is 1378

        if not self._areAllPropertiesSold and self._GetNbrAvailableProperties() == 0 :
            self._OnAllPropertiesSold()

        if player.name != self.get_name() :
            return

        # Its my turn.
        self._turnCounter += 1

        # Am I winning?
        try :
            scores = [(playerName, score, setScore, hasHouses) for playerName, (score, setScore, hasHouses) in self._scores.items()]
            maxSetScore = max(scores, key=lambda x : x[2])
            if maxSetScore[2] != 0 :
                self.__winning = maxSetScore[0] == self._player.name
            else :
                maxPropScore = max(scores, key=lambda x : x[1])
                self.__winning = maxPropScore[0] == self._player.name

            # Any houses exist?
            self.__enemyHasHouses = any(s[3] for s in scores)
            self.__iHaveHouses = self._scores[self._player.name][2]
        except :
            if not TOURNAMENT : raise

        if not TOURNAMENT :
            self._Output()


    def player_landed_on_square(self, game_state, square, player):
        '''
        Called when a player lands on a square. All AIs receive this notification.
        '''
        self._auctionInProgress = False
        self._buyingPropertyInProgress = False

        # Square counting
        #if square.name not in self._squareCount :
        #    self._squareCount[square.name] = 1
        #else:
        #    self._squareCount[square.name] += 1


    def landed_on_unowned_property(self, gameState, player, prop) :
        self._buyingPropertyInProgress = True
        if self._nbrPlayersStarted == 2 :
            if prop.name in self._UnWantedProperties() or len(prop.property_set.owners) == 2 :
                return monopyly.PlayerAIBase.Action.DO_NOT_BUY
        else :
            return monopyly.PlayerAIBase.Action.BUY

        '''
        Called when we land on an unowned property

        try :
            nbrNeeded = self._NbrPropertiesPlayerNeedsForSet(self._player, prop)
            if nbrNeeded == 1 :
                self._buyingPropertyInProgress = True
                return monopyly.PlayerAIBase.Action.BUY

            # if all players have less cash remaining than 50% of the price then do not buy (try to get at auction)
            if max(self._GetOtherPlayersCash()) < prop.price / 2 :
                return monopyly.PlayerAIBase.Action.DO_NOT_BUY

            self._buyingPropertyInProgress = True
            return monopyly.PlayerAIBase.Action.BUY

        except :
            if not TOURNAMENT : raise
            self._buyingPropertyInProgress = True
            return monopyly.PlayerAIBase.Action.BUY
        '''


    @ExceptionSafe(None)
    def money_will_be_taken(self, player, amount) :
        '''
        Called shortly before money will be taken from the player.

        Before the money is taken, there will be an opportunity to
        make deals and/or mortgage properties. (This will be done via
        subsequent callbacks.)

        No response is required.
        '''
        if player.name != self._player.name :
            return

        self.__toBeMortgaged = []
        self.__housesToSell = []
        cashNeeded = amount - self._player.state.cash
        if cashNeeded <= 0 :
            return

        mustRaiseCash = not (self._propertyPurchaseInProgress or self._auctionInProgress)

        props = self._SelectPropertiesToMortgage(mustRaiseCash)

        while cashNeeded > 0 and props :
            p = props.pop()
            self.__toBeMortgaged.append(p)
            cashNeeded -= p.mortgage_value

        if cashNeeded > 0 and mustRaiseCash :
            self.__housesToSell, cashRaised = self._SelectHousesToSell(cashNeeded)
            cashNeeded -= cashRaised
            if cashRaised > 0 and cashNeeded > 0 :
                props = self._SelectPropertiesToMortgage(mustRaiseCash)

                while cashNeeded > 0 and props :
                    p = props.pop()
                    self.__toBeMortgaged.append(p)
                    cashNeeded -= p.mortgage_value


    def money_taken(self, player, amount):
        '''
        Called when money has been taken from the player.
        No response is required.
        '''
        pass


    def money_given(self, player, amount):
        '''
        Called when money has been given to the player.
        No response is required.
        '''
        pass


    def got_get_out_of_jail_free_card(self):
        '''
        Called when the player has picked up a
        Get Out Of Jail Free card.
        No response is required.
        '''
        self._gotGOOJF = True


    def players_birthday(self) :
        return 'Happy Birthday!'


    def pay_ten_pounds_or_take_a_chance(self, gameState, player):
        '''
        Called when the player picks up the "Pay a £10 fine or take a Chance" card.

        Return either:
            PlayerAIBase.Action.PAY_TEN_POUND_FINE
            or
            PlayerAIBase.Action.TAKE_A_CHANCE
        '''
        # moving to street chance cards: Mayfair, PallMall, T.square, backThree
        # take a chance only if we own both mayfair and t.square.
        ownMayfair = False
        ownTrafalgarSq = False
        for prop in self._player.state.properties :
            if prop.name == 'Mayfair' :
                ownMayfair = True
            if prop.name == 'Trafalgar Square' :
                ownTrafalgarSq = True
        if ownMayfair and ownTrafalgarSq :
            return monopyly.PlayerAIBase.Action.TAKE_A_CHANCE
        return monopyly.PlayerAIBase.Action.PAY_TEN_POUND_FINE


    @ExceptionSafe(50)
    def property_offered_for_auction(self, gameState, player, prop) :
        if not TOURNAMENT :
            print( str(self._turnCounter) +  '. Auction: ' + prop.name + ' my cash = ' + str(player.state.cash))
        self._nbrAuctions += 1
        self._auctionInProgress = True

        if self._turnCounter == 200 or self._turnCounter == 201 :
            self._SetEminentDomainStrategy()
            if isinstance(prop, monopyly.Street) :
                self._nbrEminentDomainStreetAuctions += 1
            price = int(self._EminentDomainAuction(prop))
            if not TOURNAMENT :
                print('Eminent domain : %s . %d' % (prop.name, price))
            return price

        cashToSpend = self._player.state.cash + \
                      sum(p.mortgage_value for p in self._player.state.properties if not p.is_mortgaged) - \
                      100

        if cashToSpend <= 0 :
            return 5

        if self._nbrPlayersStarted == 2 :
            price = self._AuctionWith2Players(prop)
        else :
            price = self._AuctionWithMoreThan2Players(prop)
        return int( min(cashToSpend, price) )


    def _AuctionWithMoreThan2Players(self, prop) :
        if prop.name in self._UnWantedProperties() :
            return prop.price - 15
        nbrNeeded = self._NbrPropertiesPlayerNeedsForSet(self._player, prop)
        rnd = random.choice([1,2,3,4,5])
        if nbrNeeded == 2 :
            return rnd + (prop.price * 2)
        elif nbrNeeded == 1 :
            return rnd + 1000
        return rnd + prop.price + 15


    def _AuctionWith2Players(self, prop) :
        if prop.name in self._UnWantedProperties() :
            return prop.price - 15
        if len(prop.property_set.owners) == 2:
            return prop.price
        return self._AuctionWithMoreThan2Players(prop)


    def auction_result(self, status, property, player, amountPaid):
        '''
        Called with the result of an auction. All players receive
        this notification.

        status is either AUCTION_SUCCEEDED or AUCTION_FAILED.

        If the auction succeeded, the property, the player who won
        the auction and the amount they paid are passed to the AI.

        If the auction failed, the player will be None and the
        amount paid will be 0.

        No response is required.
        '''
        if not TOURNAMENT :
            print(player.name + ' got %s for %d' % (property.name, amountPaid))


    @ExceptionSafe([])
    def build_houses(self, gameState, player) :
        '''
        Gives us the opportunity to build houses.
        '''
        # We find the first set we own that we can build on...
        for owned_set in player.state.owned_unmortgaged_sets:
            # We can't build on stations or utilities, or if the
            # set already has hotels on all the properties...
            if not owned_set.can_build_houses :
                continue

            currentHouses = [ p.number_of_houses for p in owned_set.properties ]
            nbrHousesNeeded = 5 * len(owned_set.properties) - sum(currentHouses)
            cost = owned_set.house_price
            nbrAffordable = int( (self._player.state.cash - self._cashReserve) / cost)
            nbrToBuy = min(nbrHousesNeeded, nbrAffordable)


            if nbrToBuy > 0 :
                # Build evenly
                toBuy = [0] * len(owned_set.properties)
                previous = currentHouses[0]
                for i, x in enumerate(currentHouses[1:]):
                    if x < previous :
                        toBuy[i+1] += 1
                        if nbrToBuy == sum(toBuy) : break
                    elif x > previous :
                        toBuy[i] += 1
                        if nbrToBuy == sum(toBuy) : break
                for i in range(nbrToBuy - sum(toBuy)) :
                    toBuy[ i % len(toBuy) ] += 1

                ret = [(p, toBuy[i]) for i, p in enumerate(owned_set.properties) ]
                return ret
                #return [(p, nbrToBuy) for p in owned_set.properties]

        # We can't build...
        return []


    def sell_houses(self, game_state, player):
        '''
        Gives the player the option to sell properties.

        This is called when any debt, fine or rent has to be paid. It is
        called just before mortgage_properties (below).

        Notes:
        - You cannot mortgage properties with houses on them, so if you
          plan to mortgage, make sure you sell all the houses first.

        - For each house sold you receive half the price that they were
          bought for.

        - Houses on a set must end up 'balanced', ie no property can have
          more than one more house than any other property in the set.

        Return a list of tuples of the streets and number of houses you
        want to sell. For example:
        [(old_kent_road, 1), (bow_street, 1)]

        The streets should be Property objects.

        The default is not to sell any houses.
        '''
        return self.__housesToSell


    def mortgage_properties(self, game_state, player):
        '''
        Gives the player an option to mortgage properties.

        This is called before any debt is paid (house building, rent,
        tax, fines from cards etc).

        Notes:
        - You receive half the face value of each property mortgaged.

        - You cannot mortgage properties with houses on them.
          (The AI will have been given the option to sell houses before this
          function is called.)

        Return a list of properties to mortgage, for example:
        [bow_street, liverpool_street_station]

        The properties should be Property objects.

        Return an empty list if you do not want to mortgage anything.

        The default behaviour is not to mortgage anything.
        '''
        return self.__toBeMortgaged


    @ExceptionSafe([])
    def unmortgage_properties(self, gameState, player):
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
        cashAvailable = self._player.state.cash - self._cashReserve
        if cashAvailable < 150 :
            return []

        if self._GetNbrAvailableProperties() > 4 :
            return # may need the cash to buy property

        candidates = [ prop for prop in self._player.state.properties if prop.is_mortgaged ]
        candidates.sort(key = lambda x : x.price, reverse = True)
        ret = []
        while candidates and cashAvailable :
            prop = candidates.pop()
            cost = prop.mortgage_value + 0.1 * prop.mortgage_value
            if cashAvailable - cost > 0 :
                cashAvailable -= cost
                ret.append(prop)
            else :
                break

        return ret


    @ExceptionSafe(monopyly.PlayerAIBase.Action.STAY_IN_JAIL)
    def get_out_of_jail(self, gameState, player) :
        '''
        Called in the player's turn, before the dice are rolled, if the player is in jail.

        There are three possible return values:
        PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
        PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
        PlayerAIBase.Action.STAY_IN_JAIL
        '''
        if not self._IsPropertyAvailable() :
            return monopyly.PlayerAIBase.Action.STAY_IN_JAIL

        if self._gotGOOJF :
            self._gotGOOJF = False
            return monopyly.PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD

        return monopyly.PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL


    @ExceptionSafe(None)
    def propose_deal(self, game_state, player) :
        '''
        Called to allow the player to propose a deal.

        You return a DealProposal object.

        If you do not want to make a deal, return None.

        If you want to make a deal, you provide this information:
        - The player you are proposing the deal to
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

        The default is for no deal to be proposed.
        '''
        if not self._areAllPropertiesSold :
            return None

        if self.__winning or (self.__iHaveHouses and not self.__enemyHasHouses) :
            # don't give any sets away if I'm already winning.
            return self._DealBuyOneProperty() # try to buy a random property from random player

        # build collection of who needs what to complete set (where only 1 property is needed)
        propertyNeededForSet = { }  # key = playerName, value = [ propNeededForSet ]

        for propEnum, propSet in self._gameState.board._property_set_map.items() :
            for (owner, numOwned, fractionOwned) in propSet.owners :
                if len(propSet.properties) - numOwned == 1 :
                    for prop in propSet.properties :
                        if prop.owner != owner :
                            propNeeded = prop
                            break
                    propertyNeededForSet.setdefault(owner.name, []).append(propNeeded)

        if len(propertyNeededForSet) < 2 or self.get_name() not in propertyNeededForSet  :
            return self._DealBuyOneProperty()

        potentialDeals = [ ] # list of ( player, propToGive , propToGet )
        for propNeededByMe in propertyNeededForSet[self.get_name()] :
            if propNeededByMe.owner == None :
                continue
            for ownerNeedsProp in propertyNeededForSet.get(propNeededByMe.owner.name, []) :
                if ownerNeedsProp.property_set.set_enum == propNeededByMe.property_set.set_enum :
                    continue
                if ownerNeedsProp.owner == self._player :
                    potentialDeals.append( (propNeededByMe, ownerNeedsProp) )

        # filter out deals that are never acceptable
        potentialDeals = [ deal for deal in potentialDeals if CanIAcceptDeal(deal[0], deal[1]) ]
        if not potentialDeals :
            return self._DealBuyOneProperty()

        dealToPropose = None
        previouslyProposedPrice = 0
        neverBeforeProposed = [ deal for deal in potentialDeals if deal not in self._previouslyProposedDeals ]

        if neverBeforeProposed :
            dealToPropose = max( neverBeforeProposed, key = lambda x: x[0].price )
        else :
            if random.choice([0, 1]) == 0 : # to repeat endlessly retrying the same deal.
                return self._DealBuyOneProperty() # try to buy a random property from random player
            previouslyProposed = [ deal for deal in potentialDeals if deal in self._previouslyProposedDeals ]
            dealToPropose = random.choice(previouslyProposed)
            previouslyProposedPrice = self._previouslyProposedDeals[dealToPropose]

        dealPrice = self._DealCalcPriceForSwap(dealToPropose[0], dealToPropose[1], previouslyProposedPrice)
        self._previouslyProposedDeals[ dealToPropose ] = dealPrice
        if dealPrice == Deal.NO :
            return None

        if dealPrice < 0 :
            dealPrice = -dealPrice
            return self._DealPropose(monopyly.DealProposal(
                propose_to_player = dealToPropose[0].owner,
                properties_offered = [ dealToPropose[1] ],
                properties_wanted = [ dealToPropose[0] ],
                minimum_cash_wanted = int(dealPrice)))

        return self._DealPropose(monopyly.DealProposal(
                propose_to_player = dealToPropose[0].owner,
                properties_offered = [ dealToPropose[1] ],
                properties_wanted = [ dealToPropose[0] ],
                maximum_cash_offered = int(dealPrice)))


    def deal_proposed(self, gameState, player, deal_proposal):
        try :
            return self._deal_proposed(self, gameState, player, deal_proposal)
        except :
            return self._DealReject()


    def _deal_proposed(self, gameState, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''

        if len(deal_proposal.properties_offered) == 1 and not deal_proposal.properties_wanted :
            return self._DealSinglePropOffered(deal_proposal.properties_offered[0])

        # reject if too early in the game
        if self._IsPropertyAvailable() != 0 :
            return self._DealReject()

        if self.__winning :
            return self._DealReject()

        # consider single property deals
        if len(deal_proposal.properties_wanted) == 1 and not deal_proposal.properties_offered :
            return self._DealSinglePropWanted(None, deal_proposal.properties_wanted[0]) # TODO

        # only consider single properties swaps
        if not len(deal_proposal.properties_offered) == 1 and len(deal_proposal.properties_wanted) == 1 :
            return self._DealReject()

        propIGet = deal_proposal.properties_offered[0]
        propIGive = deal_proposal.properties_wanted[0]

        if propIGet.name in self._UnWantedProperties() :
            return self._DealReject()

        # Reject unless I will complete a set.

        if self._NbrPropertiesPlayerNeedsForSet(self._player, propIGet) != 1 :
            return self._DealReject()

        playerWouldCompleteSet = (self._NbrPropertiesPlayerNeedsForSet(propIGet.owner, propIGive) == 1)

        if not playerWouldCompleteSet :
            if propIGet.property_set in (monopyly.PropertySet.BROWN, monopyly.PropertySet.LIGHT_BLUE) :
                price = 0
            else :
                price = propIGet.price * 3
            return self._DealAccept(monopyly.DealResponse(
                action = monopyly.DealResponse.Action.ACCEPT,
                maximum_cash_offered = price))

        if not CanIAcceptDeal( propIGet, propIGive ) :
            return self._DealReject()

        price = self._DealCalcPriceForSwap(propIGet, propIGive, 0)

        if price == Deal.NO :
            return self._DealReject()

        if price < 0 :
            price = -price
            return self._DealAccept(monopyly.DealResponse(
                    action = monopyly.DealResponse.Action.ACCEPT,
                    minimum_cash_wanted = int(price)))

        return self._DealAccept(monopyly.DealResponse(
                action = monopyly.DealResponse.Action.ACCEPT,
                maximum_cash_offered = int(price)))



    def _NbrPropertiesPlayerNeedsForSet(self, player, prop) :
        '''How many properties of the set type of prop does player need to own the set?'''
        propSet = prop.property_set
        nbrOwned = sum(1 for p in propSet.properties if p.owner == player)
        return len(propSet.properties) - nbrOwned


    def deal_result(self, dealInfo):
        #if TOURNAMENT :
        return

        if dealInfo == monopyly.PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED :
            raise Exception('invalid deal')

        if dealInfo == monopyly.PlayerAIBase.DealInfo.SUCCEEDED :
            self._nbrSuccessfulDeals += 1

        if self._dealInProgress is not None :
            self._DealResult(dealInfo)
            self._dealInProgress = None


    def player_went_bankrupt(self, player):
        for i, p in enumerate(self._otherPlayers) :
            if p.name == player.name :
                del self._otherPlayers[i]
                break


    def game_over(self, winner, maximumRoundsPlayed) :
        if not TOURNAMENT :
            print('turn %d. nbr auctions = %d, deals (all, me) = (%d, %d)' % (self._turnCounter, self._nbrAuctions, self._nbrSuccessfulDeals, self._nbrSuccessfulDealsWithMe))


    def ai_error(self, message):
        if not TOURNAMENT :
            print(message)
            os.abort()
        '''
        Called if the return value from any of the Player AI functions
        was invalid. for example, if it was not of the expected type.

        No response is required.
        '''


#################################################################################

# Utilities ideally moved to a separate module

# Probabilities of landing on the squares, taken from running 1 AI for 500,000 turns
# rounded to 3dp

__probabilities = {
    'Mayfair' :                        	0.060,
    'Park Lane' :                      	0.049,
    'Regent Street' :                  	0.061,
    'Bond Street' :                    	0.056,
    'Oxford Street' :                  	0.059,
    'Trafalgar Square' :               	0.073,
    'Leicester Square' :               	0.062,
    'Coventry Street' :                	0.061,
    'Piccadilly' :                     	0.060,
    'Strand' :                         	0.064,
    'Fleet Street' :                   	0.062,
    'Vine Street' :                    	0.069,
    'Marlborough Street' :             	0.068,
    'Bow Street' :                     	0.064,
    'Northumberland Avenue' :          	0.058,
    'Pall Mall' :                      	0.062,
    'Whitehall' :                     	0.053,
    'Pentonville Road' :               	0.053,
    'Euston Road' :                    	0.054,
    'The Angel Islington' :            	0.053,
    'Whitechapel Road' :               	0.050,
    'Old Kent Road' :                  	0.060,
    'Community Chest' :                	0.177,
    'Chance' :                         	0.171,
    'Jail' :                           	0.144,
    'Go' :                             	0.071,
    'Marylebone Station' :             	0.070,
    'Free Parking' :                   	0.066,
    'Fenchurch Street Station' :       	0.063,
    'Water Works' :                    	0.061,
    'Go To Jail' :                     	0.061,
    'Electric Company' :               	0.055,
    'Liverpool Street Station' :       	0.054,
    'Income Tax' :                     	0.054,
    'Kings Cross Station' :            	0.052,
    'Super Tax' :                      	0.049,
}

__setInfo = {
    # P = prob of landing on any square in set
    #            P * set_rent_no_houses,   P * set_rent_hotels
    monopyly.squares.PropertySet.GREEN	:    (9.4,  231.2),
    monopyly.squares.PropertySet.YELLOW :    (8.1,  213.9),
    monopyly.squares.PropertySet.RED:        (7.5,  212.8),
    monopyly.squares.PropertySet.ORANGE :    (5.9,  194.1),
    monopyly.squares.PropertySet.DARK_BLUE : (9.4,  193.3),
    monopyly.squares.PropertySet.PURPLE :    (3.7,  138.0),
    monopyly.squares.PropertySet.LIGHT_BLUE: (2.1,  90.7),
    monopyly.squares.PropertySet.BROWN	:    (0.6,  37.5),
    monopyly.squares.PropertySet.STATION :   (47.8, 47.8),
    monopyly.squares.PropertySet.UTILITY :   (5, 5) # TODO
}

__simpleSetScores = {
    monopyly.squares.PropertySet.UTILITY : 1,
    monopyly.squares.PropertySet.BROWN : 2,
    monopyly.squares.PropertySet.STATION : 3,
    monopyly.squares.PropertySet.LIGHT_BLUE : 4,
    monopyly.squares.PropertySet.PURPLE : 5,
    monopyly.squares.PropertySet.ORANGE : 6,
    monopyly.squares.PropertySet.RED : 7,
    monopyly.squares.PropertySet.YELLOW : 8,
    monopyly.squares.PropertySet.GREEN : 9,
    monopyly.squares.PropertySet.DARK_BLUE : 10,
    }

def SimpleSetScore(propSetName) :
    return __simpleSetScores[propSetName]


class PropertyInfo :
    def __init__(self, name, prob, rents) :
        self.name = name
        self.prob = prob    # probability of landing on in 1 turn.
        self.rents = rents  # [SetRent, NoHouses .. Hotels]
        self.averageRents = [prob * r for r in rents]


__propertyInfo = {} # name : PropertyInfo map.


def InitialisePropertyInfo(squares) :
    for square in squares :
        rents = []
        if isinstance(square, monopyly.Street) :
            rents = [square.rents[0] * 2] + square.rents
        elif isinstance(square, monopyly.Station) :
            rents = [200, 25, 200, 200, 200]
        elif isinstance(square, monopyly.Utility) :
            rents = [10*7, 4*7, 10*7, 10*7, 10*7]
        if rents:
            __propertyInfo[square.name] =  PropertyInfo(square.name, __probabilities[square.name], rents)


def GetPropertyInfo(propertyName) :
    return __propertyInfo[propertyName]


def GetPropertySetAverageRents(propertySetName) :
    '''returns   P * set_rent_without_houses,   P * set_rent_hotels where P is landing on probability'''
    return __setInfo[propertySetName]


def GetPropertySetScore(setEnum):
    return __setInfo[setEnum][1]


def CanIAcceptDeal(propToGet, propToGive) :
    # assumes that the exchange of these two gives each player the set.
    setToGet = propToGet.property_set.set_enum
    setToGive = propToGive.property_set.set_enum

    if setToGet == monopyly.PropertySet.UTILITY :
        return False

    if setToGet == monopyly.PropertySet.STATION :
        return setToGive ==  monopyly.PropertySet.BROWN

    if setToGive == monopyly.PropertySet.BROWN :
        return True

    if setToGive == monopyly.PropertySet.LIGHT_BLUE :
        return setToGet != monopyly.PropertySet.BROWN

    if setToGive == monopyly.PropertySet.PURPLE :
        return setToGet != monopyly.PropertySet.BROWN

    if setToGive == monopyly.PropertySet.ORANGE :
        return setToGet not in (monopyly.PropertySet.BROWN, monopyly.PropertySet.LIGHT_BLUE, monopyly.PropertySet.PURPLE)

    if setToGive == monopyly.PropertySet.RED :
        return setToGet not in (monopyly.PropertySet.BROWN, monopyly.PropertySet.LIGHT_BLUE, monopyly.PropertySet.PURPLE)

    if setToGive == monopyly.PropertySet.YELLOW :
        return setToGet not in (monopyly.PropertySet.BROWN, monopyly.PropertySet.LIGHT_BLUE, monopyly.PropertySet.PURPLE)

    if setToGive == monopyly.PropertySet.GREEN :
        return setToGet not in (monopyly.PropertySet.BROWN, monopyly.PropertySet.LIGHT_BLUE, monopyly.PropertySet.PURPLE)

    if setToGive == monopyly.PropertySet.DARK_BLUE :
        return setToGet not in (monopyly.PropertySet.BROWN, monopyly.PropertySet.LIGHT_BLUE, monopyly.PropertySet.PURPLE)

    if setToGive == monopyly.PropertySet.STATION:
        return setToGet != monopyly.PropertySet.BROWN

    if setToGive == monopyly.PropertySet.UTILITY:
        return True

    return False


class Deal :
    NO = -1

    # buckets for cash
    CASH_1 = 0   # <200
    CASH_2 = 1   # 200-500
    CASH_3 = 2   # 500-1000
    CASH_4 = 3   # >1000

    # buckets for the prop set score comparison
    MAJOR_DISADV = 0
    MINOR_DISADV = 1
    EQUAL = 2
    MINOR_ADV = 3
    MAJOR_ADV = 4

    @staticmethod
    def GetCashBucket(cash):
        if cash < 200 :
            return Deal.CASH_1
        if cash < 500 :
            return Deal.CASH_2
        if cash < 1000 :
            return Deal.CASH_3
        if cash >= 1000 :
            return Deal.CASH_4


    @staticmethod
    def GetScoreDiffBucket(score):
        if score < -40 :
            return Deal.MAJOR_DISADV
        if score < -15 :
            return Deal.MINOR_DISADV
        if score > 40 :
            return Deal.MAJOR_ADV
        if score > 15 :
            return Deal.MINOR_ADV
        return Deal.EQUAL

    __decisionTable = (
        # To determine deal price. >0 means I will give money, <0 means I want money
        # integer is a cash amount
        # float is a multiplier to my cash (if > 0) , his cash (if < 0)
        #
        # MyCash,EnemyCash,Score,       PRICE
        (CASH_1, CASH_1, MAJOR_DISADV,    NO ),
        (CASH_1, CASH_1, MINOR_DISADV,    NO ),
        (CASH_1, CASH_1, EQUAL,           0       ),
        (CASH_1, CASH_1, MINOR_ADV,       10      ),
        (CASH_1, CASH_1, MAJOR_ADV,       0.25    ),

        (CASH_1, CASH_2, MAJOR_DISADV,    NO ),
        (CASH_1, CASH_2, MINOR_DISADV,    -0.5    ),
        (CASH_1, CASH_2, EQUAL,           -0.5    ),
        (CASH_1, CASH_2, MINOR_ADV,       -100    ),
        (CASH_1, CASH_2, MAJOR_ADV,       0.25    ),

        (CASH_1, CASH_3, MAJOR_DISADV,    -0.8    ),
        (CASH_1, CASH_3, MINOR_DISADV,    -0.6    ),
        (CASH_1, CASH_3, EQUAL,           -0.4    ),
        (CASH_1, CASH_3, MINOR_ADV,       -0.4    ),
        (CASH_1, CASH_3, MAJOR_ADV,       -200    ),

        (CASH_1, CASH_4, MAJOR_DISADV,    -0.8    ),
        (CASH_1, CASH_4, MINOR_DISADV,    -0.6    ),
        (CASH_1, CASH_4, EQUAL,           -0.4    ),
        (CASH_1, CASH_4, MINOR_ADV,       -0.4    ),
        (CASH_1, CASH_4, MAJOR_ADV,       -400    ),


        (CASH_2, CASH_1, MAJOR_DISADV,     NO     ),
        (CASH_2, CASH_1, MINOR_DISADV,     0      ),
        (CASH_2, CASH_1, EQUAL,            50     ),
        (CASH_2, CASH_1, MINOR_ADV,        100    ),
        (CASH_2, CASH_1, MAJOR_ADV,        0.5    ),

        (CASH_2, CASH_2, MAJOR_DISADV,     NO     ),
        (CASH_2, CASH_2, MINOR_DISADV,     -0.5   ),
        (CASH_2, CASH_2, EQUAL,            0      ),
        (CASH_2, CASH_2, MINOR_ADV,        100    ),
        (CASH_2, CASH_2, MAJOR_ADV,        0.25   ),

        (CASH_2, CASH_3, MAJOR_DISADV,     -0.8   ),
        (CASH_2, CASH_3, MINOR_DISADV,     -0.6   ),
        (CASH_2, CASH_3, EQUAL,            -0.4   ),
        (CASH_2, CASH_3, MINOR_ADV,        -0.4   ),
        (CASH_2, CASH_3, MAJOR_ADV,        -200   ),

        (CASH_2, CASH_4, MAJOR_DISADV,     -0.8   ),
        (CASH_2, CASH_4, MINOR_DISADV,     -0.6   ),
        (CASH_2, CASH_4, EQUAL,            -0.5   ),
        (CASH_2, CASH_4, MINOR_ADV,        -0.5   ),
        (CASH_2, CASH_4, MAJOR_ADV,        -0.3   ),

        (CASH_3, CASH_1, MAJOR_DISADV,     NO     ),
        (CASH_3, CASH_1, MINOR_DISADV,     0      ),
        (CASH_3, CASH_1, EQUAL,            200    ),
        (CASH_3, CASH_1, MINOR_ADV,        250    ),
        (CASH_3, CASH_1, MAJOR_ADV,        0.5    ),

        (CASH_3, CASH_2, MAJOR_DISADV,     NO     ),
        (CASH_3, CASH_2, MINOR_DISADV,     -0.5   ),
        (CASH_3, CASH_2, EQUAL,            100    ),
        (CASH_3, CASH_2, MINOR_ADV,        100    ),
        (CASH_3, CASH_2, MAJOR_ADV,        0.5    ),

        (CASH_3, CASH_3, MAJOR_DISADV,    -0.7    ),
        (CASH_3, CASH_3, MINOR_DISADV,    -0.5    ),
        (CASH_3, CASH_3, EQUAL,            100    ),
        (CASH_3, CASH_3, MINOR_ADV,        100    ),
        (CASH_3, CASH_3, MAJOR_ADV,        0.5    ),

        (CASH_3, CASH_4, MAJOR_DISADV,    -0.8    ),
        (CASH_3, CASH_4, MINOR_DISADV,    -0.6    ),
        (CASH_3, CASH_4, EQUAL,           -0.25   ),
        (CASH_3, CASH_4, MINOR_ADV,        0      ),
        (CASH_3, CASH_4, MAJOR_ADV,        0.3    ),

        (CASH_4, CASH_1, MAJOR_DISADV,     NO     ),
        (CASH_4, CASH_1, MINOR_DISADV,     -0.3   ),
        (CASH_4, CASH_1, EQUAL,            250    ),
        (CASH_4, CASH_1, MINOR_ADV,        300    ),
        (CASH_4, CASH_1, MAJOR_ADV,        0.5    ),

        (CASH_4, CASH_2, MAJOR_DISADV,     NO     ),
        (CASH_4, CASH_2, MINOR_DISADV,     -0.3   ),
        (CASH_4, CASH_2, EQUAL,            100    ),
        (CASH_4, CASH_2, MINOR_ADV,        300    ),
        (CASH_4, CASH_2, MAJOR_ADV,        0.4    ),

        (CASH_4, CASH_3, MAJOR_DISADV,     -0.8   ),
        (CASH_4, CASH_3, MINOR_DISADV,     -0.4   ),
        (CASH_4, CASH_3, EQUAL,            200    ),
        (CASH_4, CASH_3, MINOR_ADV,        300    ),
        (CASH_4, CASH_3, MAJOR_ADV,        0.4    ),

        (CASH_4, CASH_4, MAJOR_DISADV,     -0.8   ),
        (CASH_4, CASH_4, MINOR_DISADV,     -0.4   ),
        (CASH_4, CASH_4, EQUAL,            0      ),
        (CASH_4, CASH_4, MINOR_ADV,        200    ),
        (CASH_4, CASH_4, MAJOR_ADV,        0.4    ),
    )


    @classmethod
    def CreateDecisionTree(cls) :
        cls._decisionTree = {}
        # dimension the tree
        for cash1 in (Deal.CASH_1, Deal.CASH_2, Deal.CASH_3, Deal.CASH_4) :
            cls._decisionTree[cash1] = {}
            for cash2 in (Deal.CASH_1, Deal.CASH_2, Deal.CASH_3, Deal.CASH_4) :
                cls._decisionTree[cash1][cash2] = {}

        # populate tree
        for (myCash, enemyCash, score, price) in Deal.__decisionTable :
            cls._decisionTree[myCash][enemyCash][score] = price

    @classmethod
    def Decision(cls, myCash, enemyCash, scoreDifference):
        return cls._decisionTree[Deal.GetCashBucket(myCash)]                  \
                                  [Deal.GetCashBucket(enemyCash)]               \
                                  [Deal.GetScoreDiffBucket(scoreDifference)]

Deal.CreateDecisionTree()


