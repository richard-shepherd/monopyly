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

        #endregion

        #region Private methods

        /// <summary>
        /// Sets up the collection of Squares that make up the board.
        /// </summary>
        private void setupSquares()
        {
            // Go...
            Square_Bottom go = new Square_Bottom();
            go.Top = BOARD_OFFSET + 434;
            go.Bottom = BOARD_OFFSET + 500;
            go.Left = BOARD_OFFSET + 434;
            go.Right = BOARD_OFFSET + 500;
            m_squares.Add(go);

            // The other bottom squares...
            for(int i=0; i<9; ++i)
            {
                Square_Bottom square = new Square_Bottom();
                square.Top = BOARD_OFFSET + 434;
                square.Bottom = BOARD_OFFSET + 500;
                square.Left = BOARD_OFFSET + (int)(394 - i * 40.8);
                square.Right = BOARD_OFFSET + (int)(433 - i * 40.8);
                m_squares.Add(square);
            }
        }

        /// <summary>
        /// Draws the board...
        /// </summary>
        private void Board_Paint(object sender, PaintEventArgs e)
        {
            Graphics graphics = e.Graphics;

            // In design mode, we may not be able to load the graphics 
            // from the relative path...
            if(m_board == null)
            {
                graphics.FillRectangle(Brushes.LightYellow, 0, 0, Width, Height);
                return;
            }

            // We show the board...
            graphics.DrawImageUnscaled(m_board, BOARD_OFFSET, BOARD_OFFSET);

            // We clear info from the squares before drawing them...
            foreach (Square square in m_squares)
            {
                square.Clear();
            }


            // *** TEST ***
            m_squares[1].ShowMortgaged(graphics);
            m_squares[9].ShowMortgaged(graphics);

            m_squares[7].ShowPlayer(graphics, 0, false);
            m_squares[7].ShowPlayer(graphics, 1, false);
            m_squares[7].ShowPlayer(graphics, 2, false);
            m_squares[7].ShowPlayer(graphics, 3, false);

            m_squares[1].ShowOwner(graphics, 0);
            m_squares[3].ShowOwner(graphics, 0);
            m_squares[6].ShowOwner(graphics, 2);
            m_squares[8].ShowOwner(graphics, 1);
            m_squares[9].ShowOwner(graphics, 3);

            m_squares[1].ShowHouses(graphics, 4);
            m_squares[3].ShowHouses(graphics, 5);
            m_squares[6].ShowHouses(graphics, 3);
            m_squares[8].ShowHouses(graphics, 2);
            m_squares[9].ShowHouses(graphics, 1);

            // *** TEST ***
        }

        #endregion

        #region Private data

        // Constants...
        private const int BOARD_OFFSET = 20;

        // Bitmaps for the board, players etc...
        private Bitmap m_board = null;

        // The squares...
        private List<Square> m_squares = new List<Square>();

        #endregion
    }
}
