import time
import itertools
from ..utility import Logger
from ..game import Board
from ..squares import Property, Street


class MessagingServer(object):
    '''
    Uses ZeroMQ to publish messages to the C# GUI.
    '''

    def __init__(self, update_every_n_turns, sleep_between_turns_seconds):
        '''
        The 'constructor'.
        '''
        import zmq
        from .BoardUpdateMessage_pb2 import BoardUpdateMessage

        self._update_every_n_turns = update_every_n_turns
        self._sleep_between_turns_seconds = sleep_between_turns_seconds

        # Counts turns for when we are only sending updates
        # every n turns...
        self._turns_since_previous_publish = 0

        # We create the ZMQ context...
        self._context = zmq.Context(1)

        # We create the transport we will publish on...
        self._publish_socket = self._context.socket(zmq.PUB)
        #self._publish_socket.setsockopt(zmq.HWM, 100000)  # Number of messages to buffer if there is a slow consumer
        self._publish_socket.bind("tcp://*:12345")

        # We wait for the GUI to connect...
        self._connect_to_gui()

        # The board-data object we send...
        self.board_update_message = BoardUpdateMessage()
        for i in range(Board.NUMBER_OF_SQUARES):
            self.board_update_message.square_infos.add()

    def send_start_of_tournament_message(self, players):
        '''
        Sends the start-of-tournament message.

        'players' is a list of (player-name, player-number)
        '''
        from .StartOfTournamentMessage_pb2 import StartOfTournamentMessage

        # We create an fill in the message...
        message = StartOfTournamentMessage()
        for player in players:
            player_info = message.player_infos.add()
            player_info.player_name = player[0]
            player_info.player_number = player[1]

        # We send it, tagging it with code 1...
        buffer = message.SerializeToString()
        self._publish_socket.send(bytes([1]) + buffer)

    def send_start_of_game_message(self):
        '''
        Sends a message to the GUI saying that a game is about to start.
        '''
        # The start-of-game message is just a single byte 2...
        self._publish_socket.send(bytes([2]))

    def send_end_of_turn_messages(self, tournament, game, force_send):
        '''
        Called at the end of each turn.
        We send a player-info update and a board update.
        '''
        # We always send the player-info...
        self._send_player_info_message(tournament, game)

        # We check if we need to send a board-update this turn...
        self._turns_since_previous_publish += 1
        if (self._turns_since_previous_publish < self._update_every_n_turns) and (force_send is False):
            return

        # We do want to send an update...
        self._send_board_update_message(game)
        self._turns_since_previous_publish = 0

        # We may be set to sleep between turns...
        if self._sleep_between_turns_seconds > 0:
            time.sleep(self._sleep_between_turns_seconds)

    def _send_player_info_message(self, tournament, game):
        '''
        Sends the PlayerInfoMessage, including games-won, net-worth etc.
        '''
        from .PlayerInfoMessage_pb2 import PlayerInfoMessage

        # We send data about active and bankrupt players...
        player_info_message = PlayerInfoMessage()
        for player in itertools.chain(game.state.players, game.state.bankrupt_players):
            player_info = player_info_message.player_infos.add()
            player_info.player_number = player.player_number
            player_info.net_worth = player.net_worth
            player_info.games_won = tournament.results[player.name]
            player_info.square = player.state.square
            # TODO: Add ms/turn

        # We send the message...
        buffer = player_info_message.SerializeToString()
        self._publish_socket.send(bytes([3]) + buffer)

    def _send_board_update_message(self, game):
        '''
        Sends the BoardUpdateMessage, saying the status of each square on
        the board: who owns it, whether it is mortgaged, houses on it etc.
        '''
        from .BoardUpdateMessage_pb2 import BoardUpdateMessage

        # We update the squares in the board-info-message...
        board = game.state.board
        for i in range(Board.NUMBER_OF_SQUARES):
            square = board.squares[i]
            square_info = self.board_update_message.square_infos[i]

            square_info.square_number = i
            square_info.owner_player_number = -1

            if isinstance(square, Property):
                if square.owner is not None:
                    square_info.owner_player_number = square.owner.player_number
                square_info.is_mortgaged = square.is_mortgaged

            if isinstance(square, Street):
                square_info.number_of_houses = square.number_of_houses

        # We send the message...
        buffer = self.board_update_message.SerializeToString()
        self._publish_socket.send(bytes([4]) + buffer)

    def _connect_to_gui(self):
        import zmq

        # We use the ZeroMQ pattern of broadcasting a "Hello" message, and
        # waiting for the client to respond. We then know that we are connected.
        Logger.log("Waiting for GUI to connect", Logger.INFO_PLUS)

        # We create a socket to listen for the "ready" signal from the gui...
        ack_socket = self._context.socket(zmq.REP)
        ack_socket.bind("tcp://*:12346")

        # We publish "Hello" messages every 100ms until we get
        # a response. The message is just a single 0 byte...
        hello_message = bytes([0])

        while True:
            self._publish_socket.send(hello_message)
            try:
                # We check if the client is connected and has sent an acknowledgement.
                # If no exception is thrown, this means that we got a reply,
                # so the client is connected...
                ack_socket.recv(flags=zmq.NOBLOCK)
                break
            except zmq.ZMQError:
                # There was no reply. So we try again...
                time.sleep(0.1)

        Logger.log("GUI connected", Logger.INFO_PLUS)


