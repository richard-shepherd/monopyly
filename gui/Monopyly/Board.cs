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
        }

        #endregion

        #region Private methods

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
                // If we couldn't load it from there, we use a dummy...
                return new Bitmap(10, 10);
            }
        }

        /// <summary>
        /// Draws the board...
        /// </summary>
        private void Board_Paint(object sender, PaintEventArgs e)
        {
            Graphics graphics = e.Graphics;

            graphics.DrawString("Hello", SystemFonts.DefaultFont, Brushes.Black, new PointF(12.0, 12.0));

            // We show the board...
            graphics.DrawImageUnscaled(m_board, 0, 0);
        }

        #endregion

        #region Private data

        // Bitmaps for the board, players etc...
        private Bitmap m_board = null;

        #endregion
    }
}
