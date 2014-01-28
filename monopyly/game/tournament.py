import itertools
import time
from .game import Game
from ..utility import Logger


class Tournament(object):
    '''
    Manages a tournament.

    A tournament is a number of games between a collection of players.

    You specify:
    - The collection of player AIs.
    - The maximum number of players in each game.
    - The number of rounds to play.

    Each round plays all permutations of the players against each other. This
    includes the same set of players playing in different orders.

    So a round may consist of a large number of games. For example, if there
    are 15 players playing in groups of 4, there are 32760 games in a round.
    '''

    class _PlayerInfo(object):
        '''
        Holds info about one player including games won, player number
        timing info etc.
        '''
        def __init__(self):
            '''
            The 'constructor'.
            '''
            self.ai = None
            self.games_won = 0
            self.turns_played = 0
            self.processing_seconds = 0.0
            self.name = ""
            self.player_number = -1

    def __init__(self, player_ais, min_players_per_game, max_players_per_game, number_of_rounds):
        '''
        The 'constructor'
        '''
        # We hold a list of _PlayerInfo objects - one for each plater...
        self.player_infos = dict()
        number_of_player_ais = len(player_ais)
        for player_number in range(number_of_player_ais):
            player_info = Tournament._PlayerInfo()
            player_info.ai = player_ais[player_number]
            player_info.name = player_info.ai.get_name()
            player_info.player_number = player_number
            self.player_infos[player_number] = player_info

        self.number_of_rounds = number_of_rounds

        # We check that there are enough players...
        if number_of_player_ais >= max_players_per_game:
            self.max_players_per_game = max_players_per_game
        else:
            self.max_players_per_game = number_of_player_ais

        if min_players_per_game < self.max_players_per_game:
            self.min_players_per_game = min_players_per_game
        else:
            self.min_players_per_game = self.max_players_per_game

        # If the messaging_server is set up, we send updates to
        # the C# GUI when game events occur...
        self.messaging_server = None

    def play(self):
        '''
        Plays the tournament and returns the results as a dictionary of
        AI names to the number of games each won.
        '''
        # We send the start-of-tournament message...
        if self.messaging_server is not None:
            # We send a list of (player-name, player-number)...
            players = [(p.name, p.player_number) for p in self.player_infos.values()]
            self.messaging_server.send_start_of_tournament_message(players)

        # We play the specified number of rounds...
        for round in range(self.number_of_rounds):
            Logger.log("Playing round {0}".format(round+1), Logger.INFO_PLUS)
            Logger.indent()

            # We play one round with each number of plays in the range specified...
            for number_of_players in range(self.min_players_per_game, self.max_players_per_game+1):
                # We play one round with the eminent-domain rule and one without...
                self._play_round(number_of_players, True)
                self._play_round(number_of_players, False)
            Logger.dedent()

        return [(p.name, p.games_won) for p in self.player_infos.values()]

    def turn_played(self, game):
        '''
        Called at the end of each turn in a game.

        We notify the GUI of the current game state.
        '''
        # We send the player-info message...
        if self.messaging_server is not None:
            self.messaging_server.send_end_of_turn_messages(tournament=self, game=game, force_send=False)

    def get_ms_per_turn(self, player):
        '''
        We calculate the ms/turn taken by the player over the whole
        tournament so far.
        '''
        player_info = self.player_infos[player.player_number]

        total_seconds = player_info.processing_seconds + player.state.ai_processing_seconds_used
        total_turns = player_info.turns_played + player.state.turns_played
        if total_turns == 0:
            milliseconds_per_turn = 0.0
        else:
            milliseconds_per_turn = 1000.0 * total_seconds / total_turns

        return milliseconds_per_turn

    def _play_round(self, number_of_players, eminent_domain):
        '''
        We play one round and store the results.
        '''
        # We loop through all permutations of the players...
        game_number = 0
        ais = [(p.ai, p.player_number) for p in self.player_infos.values()]
        for permutation in itertools.permutations(ais, number_of_players):
            # Each permutation is a collection of player AIs. We play a game with these AIs...
            game = Game()
            game.tournament = self
            game.eminent_domain = eminent_domain
            for ai in permutation:
                game.add_player(ai)

            # We notify the GUI that the game has started...
            if self.messaging_server is not None:
                self.messaging_server.send_start_of_game_message()

            # We play the game...
            game.play_game()

            # We add the winner to the results...
            winner = game.winner
            if winner is None:
                winner_name = "Game drawn"
            else:
                winner_name = winner.name

            # We update the player infos...
            for player in itertools.chain(game.state.players, game.state.bankrupt_players):
                player_info = self.player_infos[player.player_number]

                # Did this player win?
                if player_info.name == winner_name:
                    player_info.games_won += 1

                # We update the processing stats...
                player_info.turns_played += player.state.turns_played
                player_info.processing_seconds += player.state.ai_processing_seconds_used

            # We log the results...
            game_number += 1
            player_names = [ai[0].get_name() for ai in permutation]
            message = "Game {0}:  Winner was: {3} ({1} eminent-domain: {2})".format(
                game_number, player_names, eminent_domain, winner_name)
            Logger.log(message, Logger.INFO_PLUS)

            # We update the GUI...
            if self.messaging_server is not None:
                self.messaging_server.send_end_of_turn_messages(tournament=self, game=game, force_send=True)

