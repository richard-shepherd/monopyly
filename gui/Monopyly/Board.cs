using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace mpy
{
    public partial class Board : UserControl
    {
        #region Public methods

        /// <summary>
        /// Constructor.
        /// </summary>
        public Board()
        {
            InitializeComponent();

            // We load the bitmaps...
            m_board = Utils.loadBitmap("graphics/board.png");

            // We set up the squares...
            setupSquares();
        }

        /// <summary>
        /// Adds players.
        /// </summary>
        public void AddPlayers(IEnumerable<string> names)
        {
            int playerNumber = 0;
            foreach(string name in names)
            {
                PlayerInfo playerInfo = new PlayerInfo(name);
                switch(playerNumber)
                {
                    case 0:
                        playerInfo.Pen = Pens.Yellow;
                        playerInfo.OwnerShape = Utils.loadBitmap("graphics/circle.png");
                        playerInfo.PlayerShape = Utils.loadBitmap("graphics/circle+player.png");
                        break;
                    case 1:
                        playerInfo.Pen = Pens.Blue;
                        playerInfo.OwnerShape = Utils.loadBitmap("graphics/square.png");
                        playerInfo.PlayerShape = Utils.loadBitmap("graphics/square+player.png");
                        break;
                    case 2:
                        playerInfo.Pen = Pens.Green;
                        playerInfo.OwnerShape = Utils.loadBitmap("graphics/triangle.png");
                        playerInfo.PlayerShape = Utils.loadBitmap("graphics/triangle+player.png");
                        break;
                    case 3:
                        playerInfo.Pen = Pens.Crimson;
                        playerInfo.OwnerShape = Utils.loadBitmap("graphics/star.png");
                        playerInfo.PlayerShape = Utils.loadBitmap("graphics/star+player.png");
                        break;
                    default:
                        playerInfo.Pen = Pens.Black;
                        break;
                }
                m_players.Add(playerInfo);
                playerNumber++;
            }
        }

        /// <summary>
        /// Updates the netw-worth for a player. 
        /// </summary><remarks>
        /// The player number is the index of the player in the collection
        /// of players passed to AddPlayers().
        /// </remarks>
        public void UpdateNetWorth(int playerNumber, int netWorth)
        {
            m_players[playerNumber].NetWorthHistory.Add(netWorth);
        }

        #endregion

        #region Private methods

        /// <summary>
        /// Sets up the collection of Squares that make up the board.
        /// </summary>
        private void setupSquares()
        {
            // Go...
            var go = new Square_Bottom();
            go.Top = BOARD_OFFSET + 434;
            go.Bottom = BOARD_OFFSET + 500;
            go.Left = BOARD_OFFSET + 434;
            go.Right = BOARD_OFFSET + 500;
            m_squares.Add(go);

            // The other bottom squares...
            for(int i=0; i<9; ++i)
            {
                var square = new Square_Bottom();
                square.Bottom = BOARD_OFFSET + 500;
                square.Top = square.Top - 67;
                square.Left = BOARD_OFFSET + (int)(394 - i * 40.8);
                square.Right = square.Left + 41;
                m_squares.Add(square);
            }

            // Jail....
            m_squares.Add(new Square_Jail());

            // The left squares...
            for (int i = 0; i < 9; ++i)
            {
                var square = new Square_Left();
                square.Top = BOARD_OFFSET + (int)(392 - i * 40.8);
                square.Bottom = square.Top + 41;
                square.Left = BOARD_OFFSET;
                square.Right = square.Left + 67;
                m_squares.Add(square);
            }

            // Free Parking...
            var freeParking = new Square_Bottom();
            freeParking.Top = BOARD_OFFSET;
            freeParking.Bottom = freeParking.Top + 67;
            freeParking.Left = BOARD_OFFSET;
            freeParking.Right = freeParking.Left + 67;
            m_squares.Add(freeParking);

            // The other top squares...
            for (int i = 0; i < 9; ++i)
            {
                var square = new Square_Top();
                square.Top = BOARD_OFFSET;
                square.Bottom = square.Top + 67;
                square.Left = BOARD_OFFSET + (int)(67 + i * 40.8);
                square.Right = square.Left + 41;
                m_squares.Add(square);
            }

            // Go To Jail...
            var goToJail = new Square_Right();
            goToJail.Top = BOARD_OFFSET;
            goToJail.Bottom = goToJail.Top + 67;
            goToJail.Right = BOARD_OFFSET + 500;
            goToJail.Left = goToJail.Right - 67;
            m_squares.Add(goToJail);

            // The other right squares...
            for (int i = 0; i < 9; ++i)
            {
                var square = new Square_Right();
                square.Top = BOARD_OFFSET + (int)(67 + i * 40.8);
                square.Bottom = square.Top + 41;
                square.Right = BOARD_OFFSET + 500;
                square.Left = square.Right - 67;
                m_squares.Add(square);
            }
        }

        /// <summary>
        /// Draws the board...
        /// </summary>
        private void Board_Paint(object sender, PaintEventArgs e)
        {
            Graphics g = e.Graphics;

            // In design mode, we may not be able to load the graphics 
            // from the relative path...
            if(m_board == null)
            {
                g.FillRectangle(Brushes.LightYellow, 0, 0, Width, Height);
                return;
            }

            // We clear info from the squares before drawing them...
            foreach (Square square in m_squares)
            {
                square.Clear();
            }

            // We show the board,mortgaged and houses...
            showBoard(g);

            // We show the players...
            showPlayers(g);

            // We show the net-worth graph...
            showNetWorth(g);

        }

        /// <summary>
        /// Shows the board, houses etc.
        /// </summary>
        private void showBoard(Graphics g)
        {
            g.DrawImageUnscaled(m_board, BOARD_OFFSET, BOARD_OFFSET);

            // *** TEST ***
            m_squares[31].ShowMortgaged(g);
            m_squares[39].ShowMortgaged(g);

            m_squares[31].ShowOwner(g, m_players[0].OwnerShape);
            m_squares[33].ShowOwner(g, m_players[0].OwnerShape);
            m_squares[36].ShowOwner(g, m_players[2].OwnerShape);
            m_squares[38].ShowOwner(g, m_players[1].OwnerShape);
            m_squares[39].ShowOwner(g, m_players[3].OwnerShape);

            m_squares[31].ShowHouses(g, 4);
            m_squares[34].ShowHouses(g, 5);
            m_squares[36].ShowHouses(g, 3);
            m_squares[38].ShowHouses(g, 2);
            m_squares[39].ShowHouses(g, 1);
            // *** TEST ***
        }

        /// <summary>
        /// Shows the locations of the players.
        /// </summary>
        private void showPlayers(Graphics g)
        {
            // *** TEST ***
            m_squares[38].ShowPlayer(g, m_players[0].PlayerShape, false);
            m_squares[37].ShowPlayer(g, m_players[1].PlayerShape, false);
            m_squares[37].ShowPlayer(g, m_players[2].PlayerShape, false);
            m_squares[37].ShowPlayer(g, m_players[3].PlayerShape, false);
            // *** TEST ***
        }

        /// <summary>
        /// Shows the net-worth graph.
        /// </summary>
        private void showNetWorth(Graphics g)
        {
            int left = BOARD_OFFSET + NET_WORTH_X;
            int right = left + NET_WORTH_WIDTH;
            int top = BOARD_OFFSET + NET_WORTH_Y;
            int bottom = top + NET_WORTH_HEIGHT;

            // We show the grid lines...
            g.DrawLine(Pens.Black, left, top, left, bottom);
            g.DrawLine(Pens.Black, left, bottom, right, bottom);
            for(int i=0; i<8; ++i)
            {
                int y = top + i * NET_WORTH_HEIGHT / 8;
                g.DrawLine(Pens.LightGray, left+1, y, right, y);
            }
            g.DrawString("Net worth", new Font("Arial", 12), Brushes.Black, left, top-10);

            // We scale the values according to the maximum net worth...
            int maxNetWorth = findMaxNetWorth();
            int maxCount = findMaxNetWorthCount();
            g.DrawString(maxCount.ToString(), new Font("Arial", 12), Brushes.Black, left, top+20);

            // If there are fewer than two entries, we cannot graph them...
            if(maxCount < 2)
            {
                return;
            }
            double lineLength = NET_WORTH_WIDTH / (double)maxCount;
            if(lineLength > 5)
            {
                lineLength = 5;
            }

            // We show a line for each player...
            foreach(var player in m_players)
            {
                for(int i=0; i<player.NetWorthHistory.Count-1; ++i)
                {
                    int startX = left + 1 + (int)(i * lineLength);
                    int endX = left + 1 + (int)((i+1) * lineLength);
                    int startY = bottom - player.NetWorthHistory[i] * NET_WORTH_HEIGHT / maxNetWorth;
                    int endY = bottom - player.NetWorthHistory[i + 1] * NET_WORTH_HEIGHT / maxNetWorth;
                    g.DrawLine(player.Pen, startX, startY, endX, endY);
                }
            }
        }

        /// <summary>
        /// Returns the maximum net worth of any of the players
        /// from the history of net worth.
        /// </summary>
        private int findMaxNetWorth()
        {
            int max = 0;
            foreach (var player in m_players)
            {
                foreach (int netWorth in player.NetWorthHistory)
                {
                    if (netWorth > max)
                    {
                        max = netWorth;
                    }
                }
            }
            return max;
        }

        /// <summary>
        /// Returns the size of the largest net-worth list.
        /// </summary>
        private int findMaxNetWorthCount()
        {
            int max = 0;
            foreach (var player in m_players)
            {
                if(player.NetWorthHistory.Count > max)
                {
                    max = player.NetWorthHistory.Count;
                }
            }
            return max;
        }

        #endregion

        #region Private data

        // Constants...
        private const int BOARD_OFFSET = 20;
        private const int NET_WORTH_X = 100;
        private const int NET_WORTH_Y = 300;
        private const int NET_WORTH_WIDTH = 300;
        private const int NET_WORTH_HEIGHT = 100;

        // Bitmaps for the board, players etc...
        private Bitmap m_board = null;

        // The squares...
        private List<Square> m_squares = new List<Square>();

        // Info about one player...
        private class PlayerInfo
        {
            // Constructor...
            public PlayerInfo(string name)
            {
                NetWorthHistory = new List<int>();
            }

            // The player's name...
            public string Name { get; set; }

            // The player's net worth for each turn of the game...
            public List<int> NetWorthHistory { get; set; }

            // The pen for drawing net-worth...
            public Pen Pen { get; set; }

            // The image used to mark properties owned by this player...
            public Bitmap OwnerShape { get; set; }

            // The image used to show the player's position on the board...
            public Bitmap PlayerShape { get; set; }
        }

        // The collection of players...
        private List<PlayerInfo> m_players = new List<PlayerInfo>();

        #endregion
    }
}
