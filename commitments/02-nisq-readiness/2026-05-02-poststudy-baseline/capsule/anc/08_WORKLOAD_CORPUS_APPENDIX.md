# Appendix: Workload Corpus (Public) — QASM + SHA256 IDs

**Why this exists:** This paper references **workloads by content** (OpenQASM text + SHA256 hash), not by external paths.

For each workload we include:
- the **full QASM** (copy/paste runnable),
- a **SHA256** over the exact bytes,
- a short **semantic description**.

---

## Workload A1 — Bell-2Q

**Description:** Prepare Bell pair and measure in Z basis.

**SHA256 (QASM bytes below):** `sha256:2fb143875ed170f0535a9227c3f6bece9ac82278de05a5a9513aec75dc9ada33`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q -> c;
```

---

## Workload A2 — GHZ-3Q

**Description:** Prepare 3-qubit GHZ state and measure in Z basis.

**SHA256 (QASM bytes below):** `sha256:af9200346cd403c8b67db2a89b266117404b2a001a5c0fddea5d6ff656321a08`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0],q[1];
cx q[1],q[2];
measure q -> c;
```

---

## Workload A3 — GHZ-5Q

**Description:** Prepare 5-qubit GHZ state and measure in Z basis.

**SHA256 (QASM bytes below):** `sha256:283bcd9325f1c87bdc13015c04c9b74933544e0ceb279ec0aaf7fbfbf90d3c35`

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[5];
h q[0];
cx q[0],q[1];
cx q[1],q[2];
cx q[2],q[3];
cx q[3],q[4];
measure q -> c;
```

---

## Workload A4 — Mirror-1Q

**Description:** Single-qubit “mirror” circuit (unitary forward + inverse) returning to |0⟩.

**SHA256 (QASM bytes below):** `sha256:61eb4f36dad53e25c71f5ccf114a961f818784f7a94be92f852adf0fc23b2e70`

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

---

## Notes

- The canonical workload IDs for publication are the SHA256 values above, computed over the exact OpenQASM bytes in each code block.

