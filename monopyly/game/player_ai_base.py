
class PlayerAIBase(object):
    '''
    A base class for player AIs.

    Contains default implementations events that players can be
    notified about. Some events will require a decision from the
    AI. Others are just notifications that something has
    occurred.

    Many of the functions are passed game_state and player_state.

    game_state: A copy of the GameState object, including the
                state of all players. Note that some information
                about other players will be 'redacted', such as
                how much money they have.

    player_state: A copy of the AI's own PlayerState object. Each
                  player has a number, so the AI can tell which of
                  the game players it is.

    These objects are passed as copies to avoid the AIs being able
    to directly change the state.
    '''

    class Action(object):
        '''
        An 'enum' for the various actions an AI can perform.
        '''
        BUY = 0
        DO_NOT_BUY = 1

    def start_of_game(self, player_number):
        '''
        Called at the start of the game to tell each AI
        which player-number it is.

        No response is required.
        '''
        pass

    def start_of_turn(self, game_state, player_number):
        '''
        Called when an AI's turn starts. All AIs receive this notification.

        No response is required.
        '''
        pass

    def player_landed_on_square(self, game_state, square_name, player_number):
        '''
        Called when a player lands on a square. All AIs receive this notification.
        '''
        pass

    def landed_on_unowned_property(self, game_state, player_state, property_name):
        '''
        Called when the AI lands on an unowned property. Only the active
        player receives this notification.

        Must return either the BUY or DO_NOT_BUY action from the
        PlayerAIBase.Action enum.

        The default behaviour is DO_NOT_BUY.
        '''
        return PlayerAIBase.Action.DO_NOT_BUY

    def money_will_be_taken(self, player_state, amount):
        '''
        Called shortly before money will be taken from the player.

        Before the money is taken, there will be an opportunity to
        make deals and/or mortgage properties. (This will be done via
        subsequent callbacks.)

        No response is required.
        '''
        pass

    def money_taken(self, player_state, amount):
        '''
        Called when money has been taken from the player.

        No response is required.
        '''
        pass

    def money_given(self, player_state, amount):
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
        pass









