import zmq
import time
from ..utility import Logger
from .StartOfTournamentMessage_pb2 import StartOfTournamentMessage


class MessagingServer(object):
    '''
    Uses ZeroMQ to publish messages to the C# GUI.

    The constructor blocks until it has connected to the GUI.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        # We create the ZMQ context...
        self._context = zmq.Context(1)

        # We create the transport we will publish on...
        self._publish_socket = self._context.socket(zmq.PUB)
        self._publish_socket.setsockopt(zmq.HWM, 100000)  # Number of messages to buffer if there is a slow consumer
        self._publish_socket.bind("tcp://*:12345")

        # We wait for the GUI to connect...
        self._connect_to_gui()

    def send_start_of_tournament_message(self, players):
        '''
        Sends the start-of-tournament message.

        'players' is a list of (player-name, player-number)
        '''
        # We create an fill in the message...
        message = StartOfTournamentMessage()
        for player in players:
            player_info = message.player_infos.add()
            player_info.player_name = player[0]
            player_info.player_number = player[1]

        # We send it, tagging it with code 1...
        buffer = message.SerializeToString()
        self._publish_socket.send(bytes([1]) + buffer)

    def _connect_to_gui(self):
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


