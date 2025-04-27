import random
from Crypto.Cipher import AES

from yaosfe.circuits import LogicCircuit, GarbledCircuit
from yaosfe.gates import LogicGate, GarbledGate

class Garbler:

    def __init__(self, seed = None):
        self.random = random.Random(seed)

    def garble(self, lc: LogicCircuit, input_bits: list[int]) -> GarbledCircuit:

        if not isinstance(lc, LogicCircuit):
            raise ValueError("Garbler accepts only LogicCircuit instances")

        if len(input_bits) != len(lc.input_ids):
            raise ValueError("Lengths of input_ids and input_bits differ")

        self.keys = [ 
            (self.random.randbytes(GarbledGate.KEY_SIZE), self.random.randbytes(GarbledGate.KEY_SIZE))
            for _ in range(lc.n)
        ]

        garbled_gates = [ self._garble_gate(g) for g in lc.gates ]

        input_keys = [ self.keys[idx][value] for idx, value in zip (lc.input_ids, input_bits) ]

        gc = GarbledCircuit(
            lc.input_ids,
            lc.output_ids,
            garbled_gates,
            input_keys,
        )

        return gc

    def decrypt(self, output_ids: list[int], output_keys: list[bytes]) -> list[int]:

        if len(output_ids) != len(output_keys):
            raise ValueError("Lengths of output_ids and output_keys differ")

        # Lookup the value in self.keys
        output_bits = []
        for idx, key in zip(output_ids, output_keys):

            key0, key1 = self.keys[idx]
            if key == key0: 
                output_bits.append(0)
            elif key == key1:
                output_bits.append(1)
            else:
                raise ValueError("Secret key not found in data for previous garbled circuit")

        return output_bits

    def _garble_gate(self, gate: LogicGate) -> GarbledGate:

        garbled_values = []

        for in_bits, out_val in enumerate(gate.values):

            key_out = self.keys[gate.id][out_val]

            # Logic "NOT" Gate
            if len(gate.inputs) == 1:
                # Get the key corresponding to the "in_bits" value on the input
                key_single = self.keys[gate.inputs[0]][in_bits] 

                # Double use of the same key does not increase the security, but makes it 
                # consistent with the 2-input logic gates
                key_in = key_single + key_single

            # Logic Binary Gate (AND, OR, XOR, ...)
            else:
                assert len(gate.inputs) == 2

                # Split input bits into individual bit values (left, right)
                bit_left = (in_bits & 2) >> 1
                bit_right = in_bits & 1

                key_left = self.keys[gate.inputs[0]][bit_left]
                key_right = self.keys[gate.inputs[1]][bit_right]

                key_in = key_left + key_right

            aes = AES.new(key_in, AES.MODE_ECB)
            ciphertext = aes.encrypt(key_out + GarbledGate.PAD_ZEROS)

            garbled_values.append(ciphertext)

        # Randomly permute the table
        self.random.shuffle(garbled_values)

        gg = GarbledGate(
            gate.id,
            gate.inputs,
            garbled_values
        )

        return gg
