"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Put documentation Here"""

    def __init__(self, Zero_Duration=12, One_Duration=13, Gap_Duration=11, Pause_Duration=14, Send_Times=1):
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='OOK Decode',   # will show up in GRC
            in_sig=[np.float32],
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.Zero_Duration = Zero_Duration
        self.One_Duration = One_Duration
        self.Gap_Duration = Gap_Duration
        self.Pause_Duration = Pause_Duration
        self.Send_Times = Send_Times

    def work(self, input_items, output_items):
        output_items[0][:] = input_items[0]
        print(output_items)
