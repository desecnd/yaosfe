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

    def __repr__(self) -> str:
        header = f"{self.__class__.__name__}({self.id})"
        inputs = f"<{','.join(str(x) for x in self.inputs)}>"
        values = f"[{''.join(str(x) for x in self.values)}]"
        return header + inputs + values

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "inputs": self.inputs,
            "values": self.values
        }

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(payload["id"], payload["inputs"], payload["values"])

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

    def __repr__(self) -> str:
        header = f"{self.__class__.__name__}({self.id})"
        inputs = f"<{','.join(str(x) for x in self.inputs)}>"
        values = f"[{','.join(x.hex() for x in self.values)}]"
        return header + inputs + values

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "inputs": self.inputs,
            "values": [ b.hex() for b in self.values ]
        }

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(
            payload["id"],
            payload["inputs"],
            [ bytes.fromhex(x) for x in payload["values"] ]
        )
