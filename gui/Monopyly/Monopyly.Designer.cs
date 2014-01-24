namespace mpy
{
    partial class Monopyly
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Monopyly));
            this.ctrlTimer = new System.Windows.Forms.Timer(this.components);
            this.ctrlBoard = new mpy.Board();
            this.SuspendLayout();
            // 
            // ctrlTimer
            // 
            this.ctrlTimer.Enabled = true;
            this.ctrlTimer.Interval = 10;
            this.ctrlTimer.Tick += new System.EventHandler(this.ctrlTimer_Tick);
            // 
            // ctrlBoard
            // 
            this.ctrlBoard.BoardUpdate = null;
            this.ctrlBoard.Location = new System.Drawing.Point(0, 0);
            this.ctrlBoard.Name = "ctrlBoard";
            this.ctrlBoard.Size = new System.Drawing.Size(560, 560);
            this.ctrlBoard.TabIndex = 0;
            // 
            // Monopyly
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.Black;
            this.ClientSize = new System.Drawing.Size(559, 551);
            this.Controls.Add(this.ctrlBoard);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "Monopyly";
            this.Text = "Monopyly";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.Monopyly_FormClosing);
            this.Load += new System.EventHandler(this.Monopyly_Load);
            this.ResumeLayout(false);

        }

        #endregion

        private Board ctrlBoard;
        private System.Windows.Forms.Timer ctrlTimer;

    }
}

