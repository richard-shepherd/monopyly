using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace Monopyly
{
    /// <summary>
    /// Draws the bottom squares of the board, from Go
    /// to Pentonville Road.
    /// </summary>
    class Square_Bottom : Square
    {
        #region Public methods
        
        /// <summary>
        /// Shows the square as mortgaged.
        /// </summary>
        public override void ShowMortgaged(Graphics graphics)
        {
            // We draw a red line from the top-left to the bottom-right 
            // of the square...
            int offset = 6;
            var points = new Point[]
            {
                new Point(Left, Top),
                new Point(Left+offset, Top),
                new Point(Right, Bottom),
                new Point(Right-offset, Bottom)
            };
            graphics.FillPolygon(Brushes.Red, points);
        }

        /// <summary>
        /// Shows the owner of the square.
        /// </summary>
        public override void ShowOwner(Graphics graphics, Bitmap playerShape)
        {
            graphics.DrawImageUnscaled(playerShape, Left + 6, Top - 20);
        }

        #endregion

    }
}
