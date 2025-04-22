import random
from Crypto.Cipher import AES

class Gate:
    """Generic Gate Object"""

    def __init__(self, id: int, inputs: list[int], values: list):
        self._id = id
        self.inputs = inputs
        self.values = values

        if len(self.inputs) not in [1, 2]:
            raise ValueError("Only gates of size 1 or 2 are supported.")

        if max(self.inputs) >= self.id:
            raise ValueError("Gate can only contain inputs with smaller ids")

        if len(self.values) != 2 ** len(self.inputs):
            raise ValueError("Number of gate values must be equal to power of 2 of possible inputs")

    @property
    def id(self) -> int:
        return self._id

    def evaluate(self, input_values: list):
        raise NotImplementedError

class LogicGate(Gate):

    def __init__(self, id: int, inputs: list[int], values: list[int]):
        super().__init__(id, inputs, values)

        if not all([(value in [0, 1]) for value in values]):
            raise ValueError("Gate values must be given in binary: 0 or 1")


    def evaluate(self, input_values: list[int]) -> int:

        if not all([(value in [0, 1]) for value in input_values]):
            raise ValueError("Gate values must be given in binary: 0 or 1")

        if len(input_values) != len(self.inputs):
            raise ValueError("Lengths of inputs and input values do not match")

        # Use `int` type conversion from binary - Concatenate the individual
        # bits into one large number
        truth_table_idx = int(''.join(str(x) for x in input_values), 2)

        return self.values[truth_table_idx]


class GarbledGate(Gate):

    # Garbling Parameters
    KEY_SIZE = 16
    PAD_ZEROS = b"\x00" * KEY_SIZE

    def __init__(self, id: int, inputs: list[int], values: list[bytes]):
        super().__init__(id, inputs, values)

        if not all([isinstance(value, bytes) for value in values]):
            raise ValueError("GarbledGate values must be ciphertexts stored as bytes object")

    def evaluate(self, input_keys: list[bytes]) -> bytes:

        if len(input_keys) not in [1, 2]:
            raise ValueError("Incorrect length of input_keys given")

        # Use key twice if NOT gate, otherwise merge the keys into one larger key
        dec_key = input_keys[0] * 2 if len(input_keys) == 1 else b"".join(input_keys)
        aes = AES.new(dec_key, AES.MODE_ECB)

        # Four values corresponding to AES(k1||k2, k3||PAD) ciphertexts
        output_key = None
        for ciphertext in self.values:
            plaintext = aes.decrypt(ciphertext)

            # Correct decryption will end with 0x00 * 16
            if plaintext.endswith(self.PAD_ZEROS):
                output_key = plaintext[:self.KEY_SIZE]
        else:
            ValueError("Cannot find valid plaintext from AES decryption")

        return output_key

class Circuit:

    def __init__(self, input_ids: list[int], output_ids: list[int], gates: list[Gate]):
        self.input_ids = input_ids
        self.output_ids = output_ids
        self.gates = gates

        all_ids = sorted(input_ids + [ g.id for g in gates ])
        n = len(all_ids)

        if all_ids != list(range(n)):
            raise ValueError("Gate ids and input_ids should be unique, disjoint and provide exactly n values")

        if not all([i in all_ids for i in output_ids]):
            raise ValueError("Output ids are not in all used ids range")

        self.n = n
        self.gate_by_idx: list[Gate] = [ None ] * n

        for g in self.gates:
            self.gate_by_idx[g.id] = g

    def evaluate(self, input_values: list) -> list:

        if len(input_values) != len(self.input_ids):
            raise ValueError("Lengths of input_ids and input values do not match")

        wire_value: list = [ None ] * self.n

        for i, value in zip(self.input_ids, input_values):
            wire_value[i] = value

        # Iterate over all possible wires
        for i in range(self.n):
            # If already calculated -> skip
            if wire_value[i] is not None:
                continue

            gate: Gate = self.gate_by_idx[i]

            # Iterate over previously calculated ids
            gate_input_values = [ wire_value[j] for j in gate.inputs ]
            assert None not in gate_input_values
            
            result = gate.evaluate(gate_input_values)
            wire_value[i] = result

        output_values = [ wire_value[i] for i in self.output_ids ]

        return output_values

class LogicCircuit(Circuit):

    def __init__(self, input_ids: list[int], output_ids: list[int], gates: list[LogicGate]):
        # Just validate that the Gates are of type LogicGate
        if not all([ isinstance(g, LogicGate) for g in gates ]):
            raise ValueError("All given gates must be of type LogicGate for LogicCircuit object")

        super().__init__(input_ids, output_ids, gates)
    
    def evaluate(self, input_bits: list[int]) -> list[int]:
        return super().evaluate(input_bits)

class GarbledCircuit(Circuit):

    def __init__(self, input_ids: list[int], output_ids: list[int], gates: list[GarbledGate], input_keys: list[bytes]):
        # Just validate that the Gates are of type GarbledGate
        if not all([ isinstance(g, GarbledGate) for g in gates ]):
            raise ValueError("All given gates must be of type GarbledGate for LogicCircuit object")

        super().__init__(input_ids, output_ids, gates)
        self.input_keys = input_keys

    def evaluate(self) -> list[bytes]:
        return super().evaluate(self.input_keys)

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
