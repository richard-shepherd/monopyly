using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace mpy
{
    /// <summary>
    /// Static utility functions.
    /// </summary>
    class Utils
    {
        #region Public functions

        /// <summary>
        /// Loads a bitmap. 
        /// </summary>
        public static Bitmap loadBitmap(string filename)
        {
            try
            {
                return new Bitmap(filename);
            }
            catch (Exception)
            {
                // We couldn't load it...
                return null;
            }
        }

        #endregion
    }
}
