using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace mpy
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
        public override void ShowOwner(Graphics graphics, int playerNumber)
        {
            Bitmap playerShape = OwnerShapes[playerNumber];
            graphics.DrawImageUnscaled(playerShape, Left + 6, Bottom - 10);
        }

        /// <summary>
        /// Shows houses or hotels.
        /// </summary>
        public override void ShowHouses(Graphics graphics, int numberOfHouses)
        {
            if(numberOfHouses == 5)
            {
                graphics.DrawImageUnscaled(HotelHorizontal, Left + 6, Top);
            }
            else if(numberOfHouses >= 1 && numberOfHouses <= 4)
            {
                for (int i = 0; i < numberOfHouses; ++i)
                {
                    graphics.DrawImageUnscaled(HouseHorizontal, Left + i * 10 - 1, Top);
                }
            }
        }

        /// <summary>
        /// Shows the player token on the square.
        /// </summary>
        public override void ShowPlayer(Graphics graphics, int playerNumber, bool inJail)
        {
            NumberOfPlayersOnSquare++;
            Bitmap player = Players[playerNumber];
            graphics.DrawImageUnscaled(player, Left + 5 + PlayerOffset.X, Top + 25 + PlayerOffset.Y);
        }


        #endregion

    }
}
