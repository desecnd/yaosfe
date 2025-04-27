from unittest import TestCase

from yaosfe.yao import Garbler, LogicCircuit, LogicGate
from yaosfe.examples import LC_ADD_1BIT, LC_ADD_2BIT, LC_ADD_3BIT
from yaosfe.util import gen_nbit_inputs

class TestLogicGates(TestCase):

    def run_binary_gate_test(self, truth_table: list[int]):
        garbler = Garbler(seed=42)

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
            gc = garbler.garble(lc, input_bits)
            output_keys = gc.evaluate()
            output_bits = garbler.decrypt(gc.output_ids, output_keys)
            self.assertEqual(output_bits[0], truth_table[i])
        
    def run_unitary_gate_test(self, truth_table: list[int]):
        garbler = Garbler(seed=42)

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
            gc = garbler.garble(lc, input_bits)
            output_keys = gc.evaluate()
            output_bits = garbler.decrypt(gc.output_ids, output_keys)
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


class TestExampleCircuits(TestCase):

    def run_nbit_adder_test(self, lc: LogicCircuit):
        garbler = Garbler(seed=42)

        n_bits = len(lc.input_ids) // 2
        # Sum of two n-bit numbers is (n-bits + 1)-bit number
        self.assertEqual(len(lc.output_ids), n_bits + 1)

        # Iterate over all possible inputs
        for i, input_bits in enumerate(gen_nbit_inputs(2 * n_bits)):
            # Split bits into left chunk and right chunk
            left = (i >> n_bits) & ((1 << n_bits) - 1)
            right = i & ((1 << n_bits) - 1)

            # Calculte the result: sum of two n-bit numbers
            result = left + right
            
            # Result must be padded to n-bits + 1 bits, we inverse the bits 
            # because we are starting from the right-most bits (i = 0) and go left,
            # but the result is stored in the opposite way 
            result_bits = [ (result & (1 << i)) >> i for i in range(n_bits + 1) ][::-1]

            # Evaluate plain (not-garbled) logic circuit
            # and make sure that the result is the same
            output_bits = lc.evaluate(input_bits)
            self.assertEqual(output_bits, result_bits)

            # Garble the circuit and check the result
            gc = garbler.garble(lc, input_bits)
            output_keys = gc.evaluate()
            output_bits = garbler.decrypt(lc.output_ids, output_keys)
            self.assertEqual(output_bits, result_bits)

    def test_1bit_adder(self):
        self.run_nbit_adder_test(LC_ADD_1BIT)

    def test_2bit_adder(self):
        self.run_nbit_adder_test(LC_ADD_2BIT)

    def test_3bit_adder(self):
        self.run_nbit_adder_test(LC_ADD_3BIT)

    def run_3bit_avg_test(self, lc: LogicCircuit):
        garbler = Garbler(seed=42)

        # Average of two 3-bit numbers is 3-bit wide 
        self.assertEqual(len(lc.output_ids), 3)

        # Iterate over all possible inputs
        for i, input_bits in enumerate(gen_nbit_inputs(6)):
            # Split bits into left chunk and right chunk
            left = (i >> 3) & ((1 << 3) - 1)
            right = i & ((1 << 3) - 1)

            # Calculte the result: sum of two n-bit numbers
            result = (left + right)//2
            
            # Result must be padded to n-bits bits, we inverse the bits 
            # because we are starting from the right-most bits (i = 0) and go left,
            # but the result is stored in the opposite way 
            result_bits = [ (result & (1 << i)) >> i for i in range(3) ][::-1]

            # Evaluate plain (not-garbled) logic circuit
            # and make sure that the result is the same
            output_bits = lc.evaluate(input_bits)
            self.assertEqual(output_bits, result_bits)

            # Garble the circuit and check the result
            gc = garbler.garble(lc, input_bits)
            output_keys = gc.evaluate()
            output_bits = garbler.decrypt(lc.output_ids, output_keys)
            self.assertEqual(output_bits, result_bits)
    