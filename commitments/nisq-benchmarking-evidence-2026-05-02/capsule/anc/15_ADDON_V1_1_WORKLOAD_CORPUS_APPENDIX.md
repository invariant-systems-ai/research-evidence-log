# Add-on (v1.1) Appendix: Workload Corpus (Public) — QASM Specs + SHA256 IDs

**Purpose:** Define the v1.1 workloads by **content-addressed IDs** so the campaign is independently auditable.

**Hash rule:** Each workload ID is `sha256:<hex>` where the digest is computed over the **exact OpenQASM 2.0 text bytes** (UTF-8, LF newlines, with a trailing newline).

---

## A) Mirror-1Q depth sweep (deterministic, generated)

**Workload kinds:**
- `v11_mirror1q_d1`, `v11_mirror1q_d2`, `v11_mirror1q_d4`, `v11_mirror1q_d8`, `v11_mirror1q_d16`

**Definition:** for depth repeat count \(d\), the circuit is:

1) `qreg q[1]`, `creg c[1]`
2) Repeat the block \(d\) times:
   - `h q[0];`
   - `s q[0];`
   - `t q[0];`
   - `tdg q[0];`
   - `sdg q[0];`
   - `h q[0];`
3) `measure q[0] -> c[0];`

**Canonical example (d=1):**

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
creg c[1];
h q[0];
s q[0];
t q[0];
tdg q[0];
sdg q[0];
h q[0];
measure q[0] -> c[0];
```

**SHA256 IDs:**
- `v11_mirror1q_d1`: `sha256:61eb4f36dad53e25c71f5ccf114a961f818784f7a94be92f852adf0fc23b2e70`
- `v11_mirror1q_d2`: `sha256:3bbb6869525a70d7748e9035e24daa93180157943f28794796ef8a98b35b18e0`
- `v11_mirror1q_d4`: `sha256:1923a5d4cba7010e857020c8d016047b0835d456e0609e37eb0f44ac66706e6b`
- `v11_mirror1q_d8`: `sha256:4d5a0c01b4f31348e3abbc3586d92943f844749f852dc5bd6b9690a63c2687d6`
- `v11_mirror1q_d16`: `sha256:67acd0e767e658ac6cb1f83b1298c04f114fa5d9c0306f0d9fc0d22600d5cd91`

---

## B) GHZ-7 (full QASM)

**Kind:** `v11_ghz7`
**SHA256:** `sha256:a29a527d7442a709f342e4cb5a85f130b10b3c986efa203dd8bbd7ec099401bc`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[7];
creg c[7];
h q[0];
cx q[0],q[1];
cx q[1],q[2];
cx q[2],q[3];
cx q[3],q[4];
cx q[4],q[5];
cx q[5],q[6];
measure q -> c;
```

---

## C) QFT (full QASM)

### C.1 `v11_qft4`

**SHA256:** `sha256:5c46189f4e8ee3ba6ac61487d416a50f17f767d1286cbcd863326af83180e432`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
cu1(pi/2) q[1],q[0];
cu1(pi/4) q[2],q[0];
cu1(pi/8) q[3],q[0];
h q[0];
cu1(pi/2) q[2],q[1];
cu1(pi/4) q[3],q[1];
h q[1];
cu1(pi/2) q[3],q[2];
h q[2];
h q[3];
swap q[0],q[3];
swap q[1],q[2];
measure q -> c;
```

### C.2 `v11_qft5`

**SHA256:** `sha256:e96be77badf359e492cc36f52f31b5d834706dee6d013eb22b7a69d32b5392f3`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[5];
cu1(pi/2) q[1],q[0];
cu1(pi/4) q[2],q[0];
cu1(pi/8) q[3],q[0];
cu1(pi/16) q[4],q[0];
h q[0];
cu1(pi/2) q[2],q[1];
cu1(pi/4) q[3],q[1];
cu1(pi/8) q[4],q[1];
h q[1];
cu1(pi/2) q[3],q[2];
cu1(pi/4) q[4],q[2];
h q[2];
cu1(pi/2) q[4],q[3];
h q[3];
h q[4];
swap q[0],q[4];
swap q[1],q[3];
measure q -> c;
```

---

## D) Grover (full QASM; 1 iteration; mark |11..1>)

### D.1 `v11_grover2`

**SHA256:** `sha256:46784f16b5afbd72fc2a456ef356f0efd7d0ef089c9e90bbe8433cbb161df60b`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
h q[1];
cz q[0],q[1];
h q[0];
x q[0];
h q[1];
x q[1];
cz q[0],q[1];
x q[0];
h q[0];
x q[1];
h q[1];
measure q -> c;
```

### D.2 `v11_grover3`

**SHA256:** `sha256:c2b3293a7f1a0ea05f86305f8e1c41117e32ae901a846a6536f56692cda00fdc`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
h q[1];
h q[2];
h q[2];
ccx q[0],q[1],q[2];
h q[2];
h q[0];
x q[0];
h q[1];
x q[1];
h q[2];
x q[2];
h q[2];
ccx q[0],q[1],q[2];
h q[2];
x q[0];
h q[0];
x q[1];
h q[1];
x q[2];
h q[2];
measure q -> c;
```

---

## E) Fixed-seed random circuits (deterministic generator + SHA256 IDs)

**Workload kinds:** `v11_rand_w{w}_d{d}_s{seed}` where:
- width \(w \in \{4,6\}\)
- depth \(d \in \{8,16\}\)
- seed \(s \in \{1337, 42, 7, 314159\}\)

**Generator definition (exact):**

1) `qreg q[w]`, `creg c[w]`
2) For each layer in `range(d)`:
   - for each qubit \(q\_i\): choose one gate uniformly from {`h`,`s`,`t`} using `random.Random(seed)`
   - apply that 1Q gate to \(q\_i\)
   - choose two distinct qubits \(a,b\) using the same RNG and apply `cx q[a],q[b];`
3) `measure q -> c;`

This generator is designed to be:
- **simple** (reviewer-readable),
- **deterministic** (seeded), and
- restricted to a **Clifford+T-like** gate set plus `cx`.

**SHA256 IDs (generated QASM text):**
- `v11_rand_w4_d8_s1337`: `sha256:ea357da8636b647b4a4c5eec1363be1cbc9b7401def69886b0043f66eff37ad3`
- `v11_rand_w4_d8_s42`: `sha256:5875f8c7fa5335ac688441aa07a066d9ab96831353b085c83b1d211517abd0a1`
- `v11_rand_w4_d8_s7`: `sha256:cdc26b76646463016ed262aba7d58c628876dc8760de88d15e6c3607009f66da`
- `v11_rand_w4_d8_s314159`: `sha256:fba228e74d804d39ee70767dfe6e06ce964298c6040e4266ff4a5abd12ea2deb`
- `v11_rand_w4_d16_s1337`: `sha256:fc7086fa0e6e81b9b108d19e60a48813730f1243ccb1f919b456fe027560e9cf`
- `v11_rand_w4_d16_s42`: `sha256:284f8b885d67faf63d47099ba2de1f74f3560ec0c13f2e0758c2ebcea7543a8b`
- `v11_rand_w4_d16_s7`: `sha256:01c042df1258f98fd50065f68d7350dc5327c5bfd2c6a0dc2afd5de91f1d4ff9`
- `v11_rand_w4_d16_s314159`: `sha256:0381b7e27f3ff6022e79cd32220f793417f0d4185e547c6fa30edac734b48e38`
- `v11_rand_w6_d8_s1337`: `sha256:7e20a68bbdec09ee4e8b4fcadadaea1b90b72ca1fe6686909a0184cdde98c3a3`
- `v11_rand_w6_d8_s42`: `sha256:7abe05f3e24951a153da45b20d227bf433fa0d42c9e8fc1cc0c9959ec278d2a3`
- `v11_rand_w6_d8_s7`: `sha256:893e5f1dde7171d80362463daa6a8f5ab6535e915fbdf1258967a8d95ca0d057`
- `v11_rand_w6_d8_s314159`: `sha256:9d980479f0d6d800d0b9256a46957cf2cbdba3d285b99d7f3bda65324c3186f4`
- `v11_rand_w6_d16_s1337`: `sha256:cfe8c2353efde3e7b6a52d0d866f67f9edc2e5fee5fd2d80d50148ab3dafdac6`
- `v11_rand_w6_d16_s42`: `sha256:e36f96e5c2e0763662b1b9706fd018dd70985d1a3d7630045c04b654070b8b9c`
- `v11_rand_w6_d16_s7`: `sha256:dfa1f848ad5012a14b26c344bffcb8e2b19d97c158c62ee857a5a1fe66be62c4`
- `v11_rand_w6_d16_s314159`: `sha256:9308880a113776697d1eb2b06d1775df8799670f2c50cdc085806d321294f3f0`

---

## F) Fixed-parameter variational workload probes

These workloads are included as fixed executable circuits for evidence-framework testing. They are not variational-optimization experiments, and the shipped evidence does not claim optimizer convergence or algorithmic advantage.

### F.1 `v11_vqe_h2`

**SHA256:** `sha256:603a9eff8483c7a384db7442a6121f68ae873f26fba793cc58064dc57f2ea4bd`

Role: 2-qubit H2 UCCSD-style ansatz at fixed bond length R=1.5 Angstrom. The executable variational angle is the QASM source itself, specifically `rz(0.59)`.

### F.2 `v11_qaoa_maxcut4`

**SHA256:** `sha256:afd7fd1d494f7760929aa51d93fdb9433e1724e5c3cecf40c7c09b800cc296be`

Role: fixed-parameter p=1 QAOA workload on the C4 ring graph. The executable cost and mixer rotations are the QASM source itself, specifically `rz(1.231)` cost rotations and `rx(0.7854)` mixer rotations.

