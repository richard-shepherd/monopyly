using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace mpy
{
    /// <summary>
    /// Draws players and houses on the bottom squares of the board, 
    /// from Go to Pentonville Road.
    /// </summary>
    class Square_Bottom : Square
    {
        #region Public methods
        
        /// <summary>
        /// Shows the square as mortgaged.
        /// </summary>
        public override void ShowMortgaged(Graphics g)
        {
            // We draw a red line from the top-left to the bottom-right 
            // of the square...
            var points = new Point[]
            {
                new Point(Left, Top),
                new Point(Left+MORTGAGE_LINE_WIDTH, Top),
                new Point(Right, Bottom),
                new Point(Right-MORTGAGE_LINE_WIDTH, Bottom)
            };
            g.FillPolygon(Brushes.Red, points);
        }

        /// <summary>
        /// Shows the owner of the square.
        /// </summary>
        public override void ShowOwner(Graphics g, Bitmap ownerShape)
        {
            g.DrawImageUnscaled(ownerShape, Left + 6, Bottom - 10);
        }

        /// <summary>
        /// Shows houses or hotels.
        /// </summary>
        public override void ShowHouses(Graphics g, int numberOfHouses)
        {
            if(numberOfHouses == 5)
            {
                g.DrawImageUnscaled(HotelHorizontal, Left + 6, Top - 1);
            }
            else if(numberOfHouses >= 1 && numberOfHouses <= 4)
            {
                for (int i = 0; i < numberOfHouses; ++i)
                {
                    g.DrawImageUnscaled(HouseHorizontal, Left + i * 10 - 1, Top);
                }
            }
        }

        /// <summary>
        /// Shows the player token on the square.
        /// </summary>
        public override void ShowPlayer(Graphics g, Bitmap playerShape, bool inJail)
        {
            NumberOfPlayersOnSquare++;
            g.DrawImageUnscaled(playerShape, Left + 5 + PlayerOffset.X, Top + 25 + PlayerOffset.Y);
        }


        #endregion

    }
}
