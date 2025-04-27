from pathlib import Path
import json

from yaosfe.gates import Gate, LogicGate, GarbledGate

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
    
    def as_dict(self) -> dict:
        return {
            "input_ids": self.input_ids,
            "output_ids": self.output_ids,
            "gates": [ g.as_dict() for g in self.gates ]
        }

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(
            payload["input_ids"],
            payload["output_ids"],
            [ LogicGate.from_dict(g) for g in payload["gates"] ] 
        )

    def store_in_file(self, filepath: Path):
        with open(filepath, "w") as lc_file:
            lc_file.write(json.dumps(self.as_dict(), indent=4))

    @classmethod
    def load_from_file(cls, filepath: Path):
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Given LogicCircuit file does not exist ({filepath})")

        with open(filepath) as lc_file:
            instance = cls.from_dict(json.loads(lc_file.read()))
        return instance

class GarbledCircuit(Circuit):

    def __init__(self, input_ids: list[int], output_ids: list[int], gates: list[GarbledGate], input_keys: list[bytes]):
        # Just validate that the Gates are of type GarbledGate
        if not all([ isinstance(g, GarbledGate) for g in gates ]):
            raise ValueError("All given gates must be of type GarbledGate for LogicCircuit object")

        super().__init__(input_ids, output_ids, gates)
        self.input_keys = input_keys

    def evaluate(self) -> list[bytes]:
        return super().evaluate(self.input_keys)

    def as_dict(self) -> dict:
        return {
            "input_ids": self.input_ids,
            "output_ids": self.output_ids,
            "garbled_gates": [ g.as_dict() for g in self.gates ],
            "input_keys": [ key.hex() for key in self.input_keys ]
        }

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(
            payload["input_ids"],
            payload["output_ids"],
            [ GarbledGate.from_dict(g) for g in payload["garbled_gates"] ],
            [ bytes.fromhex(key) for key in payload["input_keys"] ]
        )

    def store_in_file(self, filepath: Path):
        with open(filepath, "w") as gc_file:
            gc_file.write(json.dumps(self.as_dict(), indent=4))

    @classmethod
    def load_from_file(cls, filepath: str):

        if not Path(filepath).exists():
            raise FileNotFoundError(f"Given GarbledCircuit file does not exist ({filepath})")

        with open(filepath) as gc_file:
            instance = cls.from_dict(json.loads(gc_file.read()))
        return instance