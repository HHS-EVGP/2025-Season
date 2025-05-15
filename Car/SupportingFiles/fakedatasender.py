import struct
import random

import cc1101 #type: ignore
import time


with cc1101.CC1101() as radio:
    # Reset the device
    #radio._reset()

    ## Transmission Variables ##
    radio.set_base_frequency_hertz(433000000)
    radio._set_modulation_format(cc1101.ModulationFormat.MSK)
    radio.set_symbol_rate_baud(5000)
    radio.set_sync_word(b'\x91\xd3')
    radio.set_preamble_length_bytes(4)
    radio.set_output_power([0xC0, 0xC2])

    while True:
        data = [random.uniform(0.0, 1000) for i in range(5)]

        # Encode data as a 32-bit float
        packed_data = struct.pack('<' + 'f' * len(data), *data)

        # Send Data
        print(radio)
        radio.transmit(packed_data)

        print(data)
        print(packed_data)
        print("Packet sent")

        time.sleep(0.25)
