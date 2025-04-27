# Secure Function Evaluation with Yao Garbled Circuits

Following is an educational project for the _Cryptographic Protocols_ course on Adam Mickiewicz University in Poznan, to better understand idea behind Yao's _Garbled Circuits_.

### Secure Function Evaluation

In Secure Function Evaluation, a logical circuit encoded in custom `.json` format (see: [examples](./examples)) can be **garbled** by part A, and send to part B. Garbled Circuit can be evaluated by part B with encrypted inputs, calculating the encrypted outputs without knowning they real value. After receiving the outputs, part A can decrypt them to obtain the evaluated plaintext bits.

### Garbled Circuits

To prepare the circuit, garbler (part A) randomly generates **encryption keys** which are tied with each "wire" binary value (pair of keys for value `0` and value `1`). For binary gates (eg. AND, OR, XOR) this requires 6 keys: 2x2 keys for the input bits and 2 keys for the output bit of the gate. In Garbling process `LogicGate` is transformed into `GarbledGate` by substituting each tripple of the bits: `(A:in, B:in, C:out)` by encrypting plaintext `C || 00...0` with `AES` initialized with `A||B` as key and operating in `ECB` mode. Additionally the gates ciphtertext entries are randomly **shuffled** to make the reverse engineering more difficult.

### Limitations

Garbled circuit prepared in this manner can only operate on logic boolean gates - they can't encode conditional statements - therefore only pure-evaluation type of circuits are supported.

### Usage

Software was prepared as a python package `yaosfe` with [uv](https://docs.astral.sh/uv/) tool.

Example usage (requires two instances open to operate - one for garbler, one for evaluator):

1. Run the garbling process: select the `logic_circuit` path and pass the `input_bits`
```bash
# Garble the 3bit ADDER circuit with A=101 and B=110 as inputs
$ uv run yao garbler examples/add_3bit.json 101110
[%] Run: Garbler
[.] Info: Garbled circuit stored under: gc_out.json
Input evaluated keys for ids: [16, 17, 12, 7] (in order)
# <Wait for the input>
```

2. Run the evaluator with generated `garbled_circuit`:

```bash
# Run the evaluator for generated file, see the generated output
$ uv run yao evaluator gc_out.json
[%] Run: Evaluator
Outputs evaluated for ids: [16, 17, 12, 7] (in order)
8568af5f587c32725419ad1f8bc662d0
0b9bf3c7f4655facead2ae1b7051747d
ced29bb0671610aad6766189f23dad3b
e0230af8742b4ab0c1aca97b68a9c97b
```

3. Paste the obtained result from `evaluator` to see the plaintext value:

```bash
...

Input evaluated keys for ids: [16, 17, 12, 7] (in order)
# <Paste>
8568af5f587c32725419ad1f8bc662d0
0b9bf3c7f4655facead2ae1b7051747d
ced29bb0671610aad6766189f23dad3b
e0230af8742b4ab0c1aca97b68a9c97b
Result: 1011
```

We can verify the output is correct as `101 ~ 5` + `110 ~ 6` = `1011 ~ 11`. 

### Unit Tests

Correctness checks for example circuits are included in `tests` directory, and can be executed with `pytest`:

```
$ pytest .
======================================================== test session starts ========================================================
platform linux -- Python 3.10.12, pytest-8.3.4, pluggy-1.5.0
rootdir: /.../yaosfe
configfile: pyproject.toml
collected 8 items

tests/test_all.py ........                                                                                                    [100%]

========================================================= 8 passed in 0.19s =========================================================
```

### Sources 

- [1] https://github.com/ojroques/garbled-circuit
- [2] https://web.mit.edu/sonka89/www/papers/2017ygc.pdf
- [3] https://eprint.iacr.org/2012/265.pdf
- [4] https://crypto.stanford.edu/cs355/18sp/lec6.pdf
- [5] https://users-cs.au.dk/orlandi/crycom/5-GarbledCircuits.pdf
- [6] https://eprint.iacr.org/2013/426.pdf
