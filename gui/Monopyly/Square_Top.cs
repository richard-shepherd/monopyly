using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace mpy
{
    /// <summary>
    /// Draws players and houses on the top squares of the board, 
    /// from Free Parking to Piccadilly.
    /// </summary>
    class Square_Top : Square
    {
        #region Public methods
        
        /// <summary>
        /// Shows the square as mortgaged.
        /// </summary>
        public override void ShowMortgaged(Graphics g)
        {
            // We draw a red line from the bottom-right to the top-left
            // of the square...
            var points = new Point[]
            {
                new Point(Right, Bottom),
                new Point(Right-MORTGAGE_LINE_WIDTH, Bottom),
                new Point(Left, Top),
                new Point(Left+MORTGAGE_LINE_WIDTH, Top)
            };
            g.FillPolygon(Brushes.Red, points);
        }

        /// <summary>
        /// Shows the owner of the square.
        /// </summary>
        public override void ShowOwner(Graphics g, int playerNumber)
        {
            Bitmap playerShape = OwnerShapes[playerNumber];
            g.DrawImageUnscaled(playerShape, Left + 6, Top - 20);
        }

        /// <summary>
        /// Shows houses or hotels.
        /// </summary>
        public override void ShowHouses(Graphics g, int numberOfHouses)
        {
            if(numberOfHouses == 5)
            {
                g.DrawImageUnscaled(HotelHorizontal, Left + 6, Bottom - 17);
            }
            else if(numberOfHouses >= 1 && numberOfHouses <= 4)
            {
                for (int i = 0; i < numberOfHouses; ++i)
                {
                    g.DrawImageUnscaled(HouseHorizontal, Right - i * 10 - 12, Bottom - 16);
                }
            }
        }

        /// <summary>
        /// Shows the player token on the square.
        /// </summary>
        public override void ShowPlayer(Graphics g, int playerNumber, bool inJail)
        {
            NumberOfPlayersOnSquare++;
            Bitmap player = Players[playerNumber];
            g.DrawImageUnscaled(player, Right - 5 - PlayerOffset.X, Bottom - 25 - PlayerOffset.Y);
        }

        #endregion

    }
}
