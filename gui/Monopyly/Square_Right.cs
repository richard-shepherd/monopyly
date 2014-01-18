using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace mpy
{
    /// <summary>
    /// Draws players and houses on the right squares of the board, 
    /// from Go To Jail to Mayfair.
    /// </summary>
    class Square_Right : Square
    {
        #region Public methods
        
        /// <summary>
        /// Shows the square as mortgaged.
        /// </summary>
        public override void ShowMortgaged(Graphics g)
        {
            // We draw a red line from the bottom-left to the top-right
            // of the square...
            var points = new Point[]
            {
                new Point(Left, Bottom),
                new Point(Left, Bottom-MORTGAGE_LINE_WIDTH),
                new Point(Right, Top),
                new Point(Right, Top+MORTGAGE_LINE_WIDTH)
            };
            g.FillPolygon(Brushes.Red, points);
        }

        /// <summary>
        /// Shows the owner of the square.
        /// </summary>
        public override void ShowOwner(Graphics g, Bitmap ownerShape)
        {
            g.DrawImageUnscaled(ownerShape, Right - 10, Top + 6);
        }

        /// <summary>
        /// Shows houses or hotels.
        /// </summary>
        public override void ShowHouses(Graphics g, int numberOfHouses)
        {
            if(numberOfHouses == 5)
            {
                g.DrawImageUnscaled(HotelVertical, Left, Top + 6);
            }
            else if(numberOfHouses >= 1 && numberOfHouses <= 4)
            {
                for (int i = 0; i < numberOfHouses; ++i)
                {
                    g.DrawImageUnscaled(HouseVertical, Left, Bottom - i * 10 - 13);
                }
            }
        }

        /// <summary>
        /// Shows the player token on the square.
        /// </summary>
        public override void ShowPlayer(Graphics g, Bitmap playerShape, bool inJail)
        {
            NumberOfPlayersOnSquare++;
            g.DrawImageUnscaled(playerShape, Right - 40 + PlayerOffset.X, Top + 5 + PlayerOffset.Y);
        }

        #endregion

    }
}
