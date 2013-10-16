
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

    def start_of_turn(self, game_state, player_state):
        '''
        Called when the AI's turn starts.

        No response is required.
        '''
        pass

    def start_of_other_players_turn(self, game_state, player_number):
        '''
        Called when another player's turn starts.
        '''
        pass

    def landed_on_unowned_property(self, game_state, player_state, property_name):
        '''
        Called when the AI lands on an unowned property.

        Must return either the BUY or DO_NOT_BUY action. The default
        behaviour is DO_NOT_BUY.
        '''
        return PlayerAIBase.Action.DO_NOT_BUY



