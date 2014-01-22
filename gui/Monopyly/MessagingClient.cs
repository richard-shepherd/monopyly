using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using Messaging;
using ProtoBuf;
using ZeroMQ;

namespace mpy
{
    /// <summary>
    /// Subscribes to messages from the Monopyly game and raises
    /// events when they are received.
    /// </summary>
    class MessagingClient : IDisposable
    {
        #region Events

        /// <summary>
        /// The start-of-tournament event.
        /// </summary>
        public class StartOfTournamentArgs : EventArgs
        {
            public StartOfTournamentMessage StartOfTournament { get; set; }
        }
        public event EventHandler<StartOfTournamentArgs> StartOfTournamentEvent;

        /// <summary>
        /// The start-of-game event.
        /// </summary>
        public event EventHandler<EventArgs> StartOfGameEvent;

        /// <summary>
        /// The board-update event.
        /// </summary>
        public class BoardUpdateArgs : EventArgs
        {
            public BoardUpdateMessage BoardUpdate { get; set; }
        }
        public event EventHandler<BoardUpdateArgs> BoardUpdateEvent;

        #endregion

        #region Public methods

        /// <summary>
        /// Constructor.
        /// </summary>
        public MessagingClient()
        {
            // We create the ZMQ context, and a socket to listen to messages...
            m_context = ZmqContext.Create();
            m_receiveSocket = m_context.CreateSocket(SocketType.SUB);
            m_receiveSocket.Connect("tcp://localhost:12345");
            m_receiveSocket.SubscribeAll();

            // We show a "Connecting" dialog...
            //var connectingForm = new ConnectingForm();
            //connectingForm.Show();
            //Application.DoEvents();

            // We wait until we get a "Hello" message from the server...
            //m_receiveSocket.Receive(m_buffer);

            // We send an ack, to tell the server we're connected...
            //var ackSocket = m_context.CreateSocket(SocketType.REQ);
            //ackSocket.Connect("tcp://localhost:12346");
            //ackSocket.Send("Ack", Encoding.UTF8);
            //ackSocket.Dispose();

            // We hide the "Connecting" dialog...
            //connectingForm.Dispose();

            // We start processing messages on a worker thread...
            m_workerThread = new Thread(processMessages);
            m_workerThread.Start();
        }

        #endregion

        #region IDisposable Members

        /// <summary>
        /// Dispose.
        /// </summary>
        public void Dispose()
        {
            // We shut down the worker thread...
            m_stopThread = true;
            m_workerThread.Join();

            // We shut down ZeroMQ...
            m_receiveSocket.Dispose();
            m_context.Dispose();
        }

        #endregion

        #region Private functions

        /// <summary>
        /// Processes the incoming message queue.
        /// </summary><remarks>
        /// Runs on a worker thread.
        /// </remarks>
        private void processMessages()
        {
            TimeSpan timeout = new TimeSpan(0, 0, 0, 0, 1);
            while (m_stopThread == false)
            {
                // We see if there is a message...
                int bytesReceived = m_receiveSocket.Receive(m_buffer, timeout);
                if (bytesReceived == -1)
                {
                    // There was no message in the queue...
                    continue;
                }

                // We got a message, so we decode it...
                switch (m_buffer[0])
                {
                    case 0:
                        // The 'Hello' message from the server...
                        handleHelloMessage();
                        break;

                    case 1:
                        // The start-of-tournament message...
                        decodeStartOfTournamentMessage(bytesReceived);
                        break;

                    case 2:
                        // The start-of-game message...
                        Utils.raiseEvent(StartOfGameEvent, this, null);
                        break;

                    case 4:
                        // The board-update message...
                        decodeBoardUpdateMessage(bytesReceived);
                        break;

                    default:
                        // An unknown message (or maybe the "Hello" message after 
                        // we connect. We ignore this...
                        break;
                }
            }
        }

        private void handleHelloMessage()
        {
            var ackSocket = m_context.CreateSocket(SocketType.REQ);
            ackSocket.Connect("tcp://localhost:12346");
            ackSocket.Send("Ack", Encoding.UTF8);
            ackSocket.Dispose();
        }

        /// <summary>
        /// Decodes a start-of-tournament message.
        /// </summary>
        private void decodeStartOfTournamentMessage(int bytesReceived)
        {
            // We decode the message...
            MemoryStream memoryStream = new MemoryStream(m_buffer);
            memoryStream.SetLength(bytesReceived);
            memoryStream.Position = 1;
            var data = Serializer.Deserialize<StartOfTournamentMessage>(memoryStream);

            // And raise an event...
            var args = new StartOfTournamentArgs { StartOfTournament = data };
            Utils.raiseEvent(StartOfTournamentEvent, this, args);
        }

        /// <summary>
        /// Decodes a board-update message.
        /// </summary>
        private void decodeBoardUpdateMessage(int bytesReceived)
        {
            // We decode the message...
            MemoryStream memoryStream = new MemoryStream(m_buffer);
            memoryStream.SetLength(bytesReceived);
            memoryStream.Position = 1;
            var data = Serializer.Deserialize<BoardUpdateMessage>(memoryStream);

            // And raise an event...
            var args = new BoardUpdateArgs { BoardUpdate = data };
            Utils.raiseEvent(BoardUpdateEvent, this, args);
        }

        #endregion

        #region Private data

        // The ZMQ context...
        private ZmqContext m_context = null;

        // The socket we use to receive messages...
        private ZmqSocket m_receiveSocket = null;

        // A buffer for receiving messages...
        private byte[] m_buffer = new byte[10000];

        // Thread for processing messages...
        private Thread m_workerThread = null;

        // A signal to stop the worker thread...
        private bool m_stopThread = false;

        #endregion

    }
}
