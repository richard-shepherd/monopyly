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
    def __init__(self, player_ais, max_players_per_game, number_of_rounds):
        '''
        The 'constructor'
        '''
        # We assign each player a number, starting at zero...
        self.player_ais = []
        number_of_player_ais = len(player_ais)
        for i in range(number_of_player_ais):
            self.player_ais.append((player_ais[i], i))

        self.number_of_rounds = number_of_rounds

        # We check that there are enough players...
        if number_of_player_ais >= max_players_per_game:
            self.players_per_game = max_players_per_game
        else:
            self.players_per_game = number_of_player_ais

        # If the messaging_server is set up, we send updates to
        # the C# GUI when game events occur...
        self.messaging_server = None

        # We hold the results in a dictionary of player name -> games won...
        self.results = {ai[0].get_name(): 0 for ai in self.player_ais}

    def play(self):
        '''
        Plays the tournament and returns the results as a dictionary of
        AI names to the number of games each won.
        '''
        # We send the start-of-tournament message...
        if self.messaging_server is not None:
            # We send a list of (player-name, player-number)...
            players = [(p[0].get_name(), p[1]) for p in self.player_ais]
            self.messaging_server.send_start_of_tournament_message(players)

        # We play the specified number of rounds...
        for round in range(self.number_of_rounds):
            Logger.log("Playing round {0}".format(round+1), Logger.INFO_PLUS)
            Logger.indent()
            self._play_round()
            Logger.dedent()

        return self.results

    def turn_played(self, game):
        '''
        Called at the end of each turn in a game.

        We notify the GUI of the current game state.
        '''
        # We send the player-info message...
        if self.messaging_server is not None:
            self.messaging_server.send_end_of_turn_messages(tournament=self, game=game, force_send=False)

    def _play_round(self):
        '''
        We play one round and store the results.
        '''
        # We loop through all permutations of the players...
        game_number = 0
        for permutation in itertools.permutations(self.player_ais, self.players_per_game):
            # Each permutation is a collection of player AIs. We play a game with these AIs...
            game = Game()
            game.tournament = self
            for player in permutation:
                game.add_player(player)

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
                self.results[winner_name] += 1

            # We log the results...
            game_number += 1
            player_names = [ai[0].get_name() for ai in permutation]
            message = "Game {0}: {1}. Winner was: {2}".format(game_number, player_names, winner_name)
            Logger.log(message, Logger.INFO_PLUS)

            # We update the GUI...
            if self.messaging_server is not None:
                self.messaging_server.send_end_of_turn_messages(tournament=self, game=game, force_send=True)

