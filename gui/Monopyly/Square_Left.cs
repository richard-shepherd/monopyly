using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace mpy
{
    /// <summary>
    /// Draws players and houses on the left squares of the board, 
    /// from Pall Amll to Vine Street.
    /// </summary>
    class Square_Left : Square
    {
        #region Public methods
        
        /// <summary>
        /// Shows the square as mortgaged.
        /// </summary>
        public override void ShowMortgaged(Graphics g)
        {
            // We draw a red line from the top-right to the bottom-left
            // of the square...
            var points = new Point[]
            {
                new Point(Right, Top),
                new Point(Right, Top+MORTGAGE_LINE_WIDTH),
                new Point(Left, Bottom),
                new Point(Left, Bottom-MORTGAGE_LINE_WIDTH)
            };
            g.FillPolygon(Brushes.Red, points);
        }

        /// <summary>
        /// Shows the owner of the square.
        /// </summary>
        public override void ShowOwner(Graphics g, int playerNumber)
        {
            Bitmap playerShape = OwnerShapes[playerNumber];
            g.DrawImageUnscaled(playerShape, Left - 20, Bottom - 36);
        }

        /// <summary>
        /// Shows houses or hotels.
        /// </summary>
        public override void ShowHouses(Graphics g, int numberOfHouses)
        {
            if(numberOfHouses == 5)
            {
                g.DrawImageUnscaled(HotelVertical, Left + 52, Top + 6);
            }
            else if(numberOfHouses >= 1 && numberOfHouses <= 4)
            {
                for (int i = 0; i < numberOfHouses; ++i)
                {
                    g.DrawImageUnscaled(HouseVertical, Left + 52, Top + i * 10 + 1);
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
            g.DrawImageUnscaled(player, Left + 10 + PlayerOffset.X, Top + 5 + PlayerOffset.Y);
        }

        #endregion

    }
}
