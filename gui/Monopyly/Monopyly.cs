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

            ctrlBoard.AddPlayers(from p in player_infos select p.name);
            // *** TEST ***
        }

        #endregion

        #region Private functions

        /// <summary>
        /// Called when the timer ticks.
        /// </summary>
        private void ctrlTimer_Tick(object sender, EventArgs e)
        {
            // *** TEST ***
            for (int i = 0; i < player_infos.Count; ++i)
            {
                player_infos[i].net_worth += rnd.Next(-100, 100);
                ctrlBoard.UpdateNetWorth(i, player_infos[i].net_worth);
            }
            // *** TEST ***


            // We update the board with the latest game information...
            ctrlBoard.Invalidate();
        }

        #endregion
    }
}
