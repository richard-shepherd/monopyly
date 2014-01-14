using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace Monopyly
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
            m_board = loadBitmap("graphics/board.png");
            m_playerShapes.Add(loadBitmap("graphics/circle.png"));
            m_playerShapes.Add(loadBitmap("graphics/square.png"));
            m_playerShapes.Add(loadBitmap("graphics/triangle.png"));
            m_playerShapes.Add(loadBitmap("graphics/star.png"));

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
            go.Top = 434;
            go.Bottom = 500;
            go.Left = 434;
            go.Right = 500;
            m_squares.Add(go);

            // The other bottom squares...
            for(int i=0; i<9; ++i)
            {
                Square_Bottom square = new Square_Bottom();
                square.Top = 434;
                square.Bottom = 500;
                square.Left = (int)(394 - i * 40.8);
                square.Right = (int)(433 - i * 40.8);
                m_squares.Add(square);
            }
        }

        /// <summary>
        /// Loads a bitmap. 
        /// </summary>
        private Bitmap loadBitmap(string filename)
        {
            // We first load it from the working folder...
            try
            {
                return new Bitmap(filename);
            }
            catch(Exception)
            {
                // We couldn't load it...
                return null;
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
            graphics.DrawImageUnscaled(m_board, 0, 0);


            // *** TEST ***
            m_squares[1].ShowMortgaged(graphics);
            m_squares[9].ShowMortgaged(graphics);
            m_squares[1].ShowOwner(graphics, m_playerShapes[0]);
            m_squares[3].ShowOwner(graphics, m_playerShapes[0]);
            m_squares[6].ShowOwner(graphics, m_playerShapes[2]);
            m_squares[8].ShowOwner(graphics, m_playerShapes[1]);
            m_squares[9].ShowOwner(graphics, m_playerShapes[3]);
            // *** TEST ***
        }

        #endregion

        #region Private data

        // Bitmaps for the board, players etc...
        private Bitmap m_board = null;

        // The squares...
        private List<Square> m_squares = new List<Square>();

        // Shapes reprsenting each player...
        private List<Bitmap> m_playerShapes = new List<Bitmap>();

        #endregion
    }
}
