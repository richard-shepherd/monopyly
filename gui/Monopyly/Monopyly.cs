using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using Messaging;

namespace mpy
{
    /// <summary>
    /// The Form that shows the Monopyly board.
    /// </summary>
    public partial class Monopyly : Form
    {
        // *** TEST ***
        class PlayerInfo
        {
            public PlayerInfo(string n) { name = n; }
            public string name;
            public int net_worth = 1500;
            public int games_won = 0;
            public double ms_per_turn = 2.0;
        }
        List<PlayerInfo> player_infos = new List<PlayerInfo>();
        Random rnd = new Random();
        // *** TEST ***

        #region Public methods

        /// <summary>
        /// Constructor.
        /// </summary>
        public Monopyly()
        {
            InitializeComponent();
        }

        #endregion

        #region Private functions

        /// <summary>
        /// Called when the form is loaded.
        /// </summary>
        private void Monopyly_Load(object sender, EventArgs e)
        {
            // We start the messaging-client...
            m_messagingClient = new MessagingClient();
            m_messagingClient.StartOfTournamentEvent += onStartOfTournament;
            m_messagingClient.BoardUpdateEvent += onBoardUpdate;
        }

        /// <summary>
        /// Called when we get a board update.
        /// </summary>
        private void onBoardUpdate(object sender, MessagingClient.BoardUpdateArgs e)
        {
            ctrlBoard.BoardUpdate = e.BoardUpdate;
        }

        /// <summary>
        /// Called when the tournament starts.
        /// </summary>
        private void onStartOfTournament(object sender, MessagingClient.StartOfTournamentArgs e)
        {
            player_infos.Clear();
            foreach(var playerInfo in e.StartOfTournament.player_infos)
            {
                player_infos.Add(new PlayerInfo(playerInfo.player_name));
            }
            ctrlBoard.SetPlayers(from p in player_infos select p.name);
        }

        /// <summary>
        /// Called just before the form closes.
        /// </summary>
        private void Monopyly_FormClosing(object sender, FormClosingEventArgs e)
        {
            m_messagingClient.Dispose();
        }

        /// <summary>
        /// Called when the timer ticks.
        /// </summary>
        private void ctrlTimer_Tick(object sender, EventArgs e)
        {
            // We update the board with the latest game information...
            ctrlBoard.Invalidate();
        }

        #endregion

        #region Private data

        // The messaging client...
        private MessagingClient m_messagingClient = null;

        #endregion

    }
}
