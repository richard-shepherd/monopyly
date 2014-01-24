using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace mpy
{
    /// <summary>
    /// Draws players on the Jail / Just Visiting square.
    /// </summary>
    class Square_Jail : Square
    {
        #region Public methods

        /// <summary>
        /// Shows the square as mortgaged.
        /// </summary>
        public override void ShowMortgaged(Graphics graphics)
        {
            // Jail cannot be mortgaged.
        }

        /// <summary>
        /// Shows the owner of the square.
        /// </summary>
        public override void ShowOwner(Graphics graphics, Bitmap ownerShape)
        {
            // Jail cannot be owned.
        }

        /// <summary>
        /// Shows houses or hotels.
        /// </summary>
        public override void ShowHouses(Graphics graphics, int numberOfHouses)
        {
            // Jail does not have houses.
        }

        /// <summary>
        /// Shows the player token on the square.
        /// </summary>
        public override void ShowPlayer(Graphics graphics, Bitmap playerShape, bool inJail)
        {
            NumberOfPlayersOnSquare++;
            graphics.DrawImageUnscaled(playerShape, Left + 5 + PlayerOffset.X, Top + 25 + PlayerOffset.Y);
        }

        #endregion
    }
}
