import argparse
from pathlib import Path

from yaosfe.gates import GarbledGate
from yaosfe.circuits import GarbledCircuit, LogicCircuit
from yaosfe.garbler import Garbler
from yaosfe.util import bits_to_str

def print_error(message: str):
    print(f"\x1b[31m[!] Error:\x1b[0m {message}")

def print_info(message: str):
    print(f"\x1b[34m[.] Info:\x1b[0m {message}")

def print_ok(message: str):
    print(f"\x1b[32m[+] Ok:\x1b[0m {message}")

def print_run(message: str):
    print(f"\x1b[33m[%] Run:\x1b[0m {message}")

def print_error_and_exit(message: str):
    print_error(message)
    exit(1)

def run_garbler(args):
    print_run("Garbler")

    lc_path = Path(args.logic_circuit)
    input_str = args.input_bits
    verify_output = args.verify
    output_path = args.output

    # Load LogicCircuit
    try:
        lc = LogicCircuit.load_from_file(lc_path)
    except FileExistsError:
        print_error_and_exit(f"Given LogicCircuit file does not exist ({lc_path})")

    # Compare number of bits
    input_bits = [ int(b) for b in input_str ]
    if len(input_bits) != len(lc.input_ids):
        print_error_and_exit("Length of input_bits and circuit input_ids do not match")

    garbler = Garbler()
    gc = garbler.garble(lc, input_bits)
    gc.store_in_file(output_path)
    print_info(f"Garbled circuit stored under: {output_path}")

    print(f"Input evaluated keys for ids: {lc.output_ids} (in order)")
    output_keys = []
    for idx in lc.output_ids:
        key_hex = input()
        key_bytes = bytes.fromhex(key_hex)
        assert len(key_bytes) == GarbledGate.KEY_SIZE
        output_keys.append(key_bytes)

    output_bits = garbler.decrypt(lc.output_ids, output_keys)
    output_str = bits_to_str(output_bits)
    print(f"Result: {output_str}")

    if verify_output:
        bits = lc.evaluate(input_bits)
        if bits == output_bits:
            print_ok(f"Verify => Output OK: {bits_to_str(bits)}")
        else:
            print_error(f"Verify => Output does not match: {bits_to_str(bits)}")

def run_evaluator(args):
    print_run("Evaluator")

    gc_filepath = args.garbled_circuit

    try:
        gc = GarbledCircuit.load_from_file(gc_filepath)
    except FileNotFoundError as e:
        print_error_and_exit(e)

    outputs: bytes = gc.evaluate()
    outputs = [ b.hex() for b in outputs ]
    print(f"Outputs evaluated for ids: {gc.output_ids} (in order)")
    print('\n'.join(outputs))


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(required=True)

    parser_garbler = subparsers.add_parser("garbler", help="Garble the logic circuit")
    parser_garbler.add_argument("logic_circuit", )
    parser_garbler.add_argument("input_bits")
    parser_garbler.add_argument("-o", "--output", default="gc_out.json")
    parser_garbler.add_argument("-v", "--verify", action="store_true", default=False)
    parser_garbler.set_defaults(func=run_garbler)

    parser_evaluate = subparsers.add_parser("evaluator", help="Evaluate a given circuit")
    parser_evaluate.add_argument("garbled_circuit")
    parser_evaluate.set_defaults(func=run_evaluator)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()