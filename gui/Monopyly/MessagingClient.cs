using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using ZeroMQ;

namespace mpy
{
    /// <summary>
    /// Subscribes to messages from the Monopyly game and raises
    /// events when they are received.
    /// </summary>
    class MessagingClient : IDisposable
    {
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
            var connectingForm = new ConnectingForm();
            connectingForm.Show();
            Application.DoEvents();

            // We wait until we get a "Hello" message from the server...
            m_receiveSocket.Receive(m_buffer);

            // We send an ack, to tell the server we're connected...
            var ackSocket = m_context.CreateSocket(SocketType.REQ);
            ackSocket.Connect("tcp://localhost:12346");
            ackSocket.Send("Ack", Encoding.UTF8);
            ackSocket.Dispose();

            // We hide the "Connecting" dialog...
            connectingForm.Dispose();
        }

        /// <summary>
        /// Processes all messages in the inbound queue.
        /// </summary>
        public void processMessages()
        {
            TimeSpan timeout = new TimeSpan(0);
            while(true)
            {
                // We see if there is a message...
                int bytesReceived = m_receiveSocket.Receive(m_buffer, timeout);
                if(bytesReceived == -1)
                {
                    // There was no message in the queue...
                    break;
                }

                // We got a message, so we decode it...
                switch (m_buffer[0])
                {
                    case 1:
                        // The start-of-tournament message...
                        decodeStartOfTournamentMessage();
                        break;

                    default:
                        // An unknown message (or maybe the "Hello" message after 
                        // we connect. We ignore this...
                        break;
                }
            }
        }

        #endregion

        #region IDisposable Members

        /// <summary>
        /// Dispose.
        /// </summary>
        public void Dispose()
        {
            m_receiveSocket.Dispose();
            m_context.Dispose();
        }

        #endregion



        #region Private data

        // The ZMQ context...
        private ZmqContext m_context = null;

        // The socket we use to receive messages...
        private ZmqSocket m_receiveSocket = null;

        // A buffer for receiving messages...
        private byte[] m_buffer = new byte[10000];

        #endregion

    }
}
