from unittest import TestCase

from yao import *

def gen_nbit_inputs(n_bits: int):
    """Generate all binary values made out of n_bits as list of int type bits"""

    for i in range(1 << n_bits):
        bits = [ int(bool(i & (1 << b))) for b in range(n_bits - 1, -1, -1) ]
        yield bits

class TestLogicGates(TestCase):

    def setup_class(cls):
        cls.garbler = Garbler(seed=42)

    def run_binary_gate_test(self, truth_table: list[int]):
        # Method suited only for binary gates
        self.assertEqual(len(truth_table), 4)

        # Prepare binary logic gate with [0,1] ids as input and 2 as output idx
        gate = LogicGate(2, [0, 1], truth_table)
        lc = LogicCircuit([0, 1], [2], [gate])

        # Iterate over all 2-bit inputs (4 values: 00, 01, 10, 11)
        for i, input_bits in enumerate(gen_nbit_inputs(2)):
            # Test binary circuit evaluation is as expected
            output_bits = lc.evaluate(input_bits)
            self.assertEqual(output_bits[0], truth_table[i])

            # Test garbled circuit output against truth table
            gc = self.garbler.garble(lc, input_bits)
            output_keys = gc.evaluate()
            output_bits = self.garbler.decrypt(gc.output_ids, output_keys)
            self.assertEqual(output_bits[0], truth_table[i])
        
    def run_unitary_gate_test(self, truth_table: list[int]):
        # Method suited only for unit 1-bit gates
        self.assertEqual(len(truth_table), 2)

        # Prepare unitary logic gate with 0 idx as input and 1 as output idx
        gate = LogicGate(1, [0], truth_table)
        lc = LogicCircuit([0], [1], [gate])

        # Iterate over all 1-bit inputs (2 values: 0, 1)
        for i, input_bits in enumerate(gen_nbit_inputs(1)):
            # Test binary circuit evaluation is as expected
            output_bits = lc.evaluate(input_bits)
            self.assertEqual(output_bits[0], truth_table[i])

            # Test garbled circuit output against truth table
            gc = self.garbler.garble(lc, input_bits)
            output_keys = gc.evaluate()
            output_bits = self.garbler.decrypt(gc.output_ids, output_keys)
            self.assertEqual(output_bits[0], truth_table[i])

    def test_gate_NOT(self):
        self.run_unitary_gate_test([1, 0])

    def test_gate_ID(self):
        self.run_unitary_gate_test([0, 1])

    def test_gate_AND(self):
        self.run_binary_gate_test([0, 0, 0, 1])
    
    def test_gate_OR(self):
        self.run_binary_gate_test([0, 1, 1, 1])

    def test_gate_XOR(self):
        self.run_binary_gate_test([0, 1, 1, 0])
