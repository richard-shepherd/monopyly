using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

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

            // *** TEST ***
            player_infos.Add(new PlayerInfo("Julian (a player with a really, really, really long name)"));
            player_infos.Add(new PlayerInfo("George"));
            player_infos.Add(new PlayerInfo("Timmy"));
            player_infos.Add(new PlayerInfo("Anne"));
            ctrlBoard.SetPlayers(from p in player_infos select p.name);
            // *** TEST ***
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
            // *** TEST ***
            if (rnd.NextDouble() < 0.01)
            {
                // Game was won...
                ctrlBoard.SetPlayers(from p in player_infos select p.name);
                int player = rnd.Next(0, 4);
                player_infos[player].games_won++;
                for (int i = 0; i < player_infos.Count; ++i)
                {
                    player_infos[i].net_worth = 1500;
                }
            }
            for (int i = 0; i < player_infos.Count; ++i)
            {
                player_infos[i].net_worth += rnd.Next(-100, 100);
                if(player_infos[i].net_worth < 0)
                {
                    player_infos[i].net_worth = 0;
                }
                ctrlBoard.UpdateNetWorth(i, player_infos[i].net_worth);

                player_infos[i].ms_per_turn += (rnd.NextDouble() - 0.5) / 10.0;
                ctrlBoard.UpdateMsPerTurn(i, player_infos[i].ms_per_turn);

                ctrlBoard.UpdateGamesWon(i, player_infos[i].games_won);
            }
            // *** TEST ***


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
