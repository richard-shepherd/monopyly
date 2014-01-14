using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace Monopyly
{
    /// <summary>
    /// An base class for squares on the board.
    /// </summary>
    abstract class Square
    {
        #region Public methods and properties

        /// <summary>
        /// The Y-position on the board of the top of the square.
        /// </summary>
        public int Top { get; set; }

        /// <summary>
        /// The Y-position on the board of the bottom of the square.
        /// </summary>
        public int Bottom { get; set; }

        /// <summary>
        /// The X-position on the board of the left of the square.
        /// </summary>
        public int Left { get; set; }

        /// <summary>
        /// The X-position on the board of the right of the square.
        /// </summary>
        public int Right { get; set; }

        #endregion

        #region Abstract methods

        /// <summary>
        /// Shows the square as mortgaged.
        /// </summary>
        public abstract void ShowMortgaged(Graphics graphics);

        /// <summary>
        /// Shows the owner of the square.
        /// </summary>
        public abstract void ShowOwner(Graphics graphics, Bitmap playerShape);

        #endregion

    }
}
