"""Reproducibility benchmark for the submitted ABLKM prototype.

The benchmark measures operations that are actually implemented by the source:
1. software BB84 simulation + SHA-256 derivation
2. AES-GCM protection/recovery of P_ref using a BB84-derived key
3. ABLKM store (geometric mapping + HMAC + HKDF + AES-GCM)
4. ABLKM retrieval (HMAC + direct registry lookup + HKDF + AES-GCM)
5. authenticated dictionary baseline using the same HMAC/HKDF/AES-GCM primitives,
   but without geometric mapping
6. pure ABLKM geometric mapping (hash-to-point + angle + bucket calculation)

The baseline is a local key-value indexing baseline, not a cryptographic equivalent
of ABLKM. The script suppresses BB84 demo output during timing so console I/O is not
included in the BB84 latency measurement.
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path
from hashlib import sha256

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from qkd_bb84 import execute_bb84
from lattice_crypto_v2 import HardenedLatticeKeyStore, derive_key_id, derive_encryption_key

TRIALS = 100
WARMUPS = 10
QUBITS = 1024
GRID_SIZE = 6
DIM = 3
POINTS_PER_BUCKET = 4
PAYLOAD = "benchmark payload: ABLKM reproducibility test"
REF = (2.4, 3.1, 1.7)
OUT = HERE / "benchmark_results.csv"
ENV = HERE / "benchmark_environment.txt"


def stats(values_ns: list[int]) -> tuple[float, float]:
    vals = [v / 1_000_000.0 for v in values_ns]
    return statistics.mean(vals), statistics.stdev(vals) if len(vals) > 1 else 0.0


def quiet_execute_bb84(qubits: int):
    with contextlib.redirect_stdout(io.StringIO()):
        return execute_bb84(qubits)


def baseline_store(key: str, value: str, ref: tuple[float, ...], registry: dict):
    key_id_hex = derive_key_id(key, ref).hex()
    # Same authenticated identifier as ABLKM, but no lattice point or angular bucket.
    salt = os.urandom(32)
    ikm = sha256(f"baseline|{key}".encode()).digest()
    aes_key = HKDF(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        info=b"ABLKM-baseline-AES256GCM"
    ).derive(ikm)
    nonce = os.urandom(12)
    ct = AESGCM(aes_key).encrypt(nonce, value.encode(), None)
    registry[key_id_hex] = (nonce, ct, salt, aes_key)


def baseline_get(key: str, ref: tuple[float, ...], registry: dict) -> str:
    key_id_hex = derive_key_id(key, ref).hex()
    nonce, ct, _salt, aes_key = registry[key_id_hex]
    return AESGCM(aes_key).decrypt(nonce, ct, None).decode()


def benchmark_bb84():
    for _ in range(WARMUPS):
        quiet_execute_bb84(QUBITS)
    vals = []
    for _ in range(TRIALS):
        t0 = time.perf_counter_ns()
        quiet_execute_bb84(QUBITS)
        vals.append(time.perf_counter_ns() - t0)
    return vals


def benchmark_pref_exchange():
    shared = quiet_execute_bb84(QUBITS)
    payload = json.dumps(REF).encode()
    for _ in range(WARMUPS):
        nonce = os.urandom(12)
        ct = AESGCM(shared).encrypt(nonce, payload, None)
        AESGCM(shared).decrypt(nonce, ct, None)
    vals = []
    for _ in range(TRIALS):
        t0 = time.perf_counter_ns()
        nonce = os.urandom(12)
        ct = AESGCM(shared).encrypt(nonce, payload, None)
        AESGCM(shared).decrypt(nonce, ct, None)
        vals.append(time.perf_counter_ns() - t0)
    return vals


def benchmark_ablkm_store():
    for _ in range(WARMUPS):
        HardenedLatticeKeyStore(GRID_SIZE, DIM, POINTS_PER_BUCKET).store_key("benchmark-key", PAYLOAD)
    vals = []
    for _ in range(TRIALS):
        s = HardenedLatticeKeyStore(GRID_SIZE, DIM, POINTS_PER_BUCKET)
        t0 = time.perf_counter_ns()
        s.store_key("benchmark-key", PAYLOAD)
        vals.append(time.perf_counter_ns() - t0)
    return vals


def benchmark_ablkm_get():
    for _ in range(WARMUPS):
        s = HardenedLatticeKeyStore(GRID_SIZE, DIM, POINTS_PER_BUCKET)
        s.store_key("benchmark-key", PAYLOAD)
        assert s.retrieve_key("benchmark-key") == PAYLOAD
    vals = []
    for _ in range(TRIALS):
        s = HardenedLatticeKeyStore(GRID_SIZE, DIM, POINTS_PER_BUCKET)
        s.store_key("benchmark-key", PAYLOAD)
        t0 = time.perf_counter_ns()
        got = s.retrieve_key("benchmark-key")
        vals.append(time.perf_counter_ns() - t0)
        assert got == PAYLOAD
    return vals


def benchmark_baseline_store():
    for _ in range(WARMUPS):
        r = {}
        baseline_store("benchmark-key", PAYLOAD, REF, r)
    vals = []
    for _ in range(TRIALS):
        r = {}
        t0 = time.perf_counter_ns()
        baseline_store("benchmark-key", PAYLOAD, REF, r)
        vals.append(time.perf_counter_ns() - t0)
    return vals


def benchmark_baseline_get():
    for _ in range(WARMUPS):
        r = {}
        baseline_store("benchmark-key", PAYLOAD, REF, r)
        assert baseline_get("benchmark-key", REF, r) == PAYLOAD
    vals = []
    for _ in range(TRIALS):
        r = {}
        baseline_store("benchmark-key", PAYLOAD, REF, r)
        t0 = time.perf_counter_ns()
        got = baseline_get("benchmark-key", REF, r)
        vals.append(time.perf_counter_ns() - t0)
        assert got == PAYLOAD
    return vals


def benchmark_geometry():
    s = HardenedLatticeKeyStore(GRID_SIZE, DIM, POINTS_PER_BUCKET, ref_coords=REF)
    for _ in range(WARMUPS):
        pt = s._key_to_point("benchmark-key")
        angle = s._point_angle(pt)
        _ = min(int(angle / s.bucket_width), s.num_buckets - 1)
    vals = []
    for _ in range(TRIALS):
        t0 = time.perf_counter_ns()
        pt = s._key_to_point("benchmark-key")
        angle = s._point_angle(pt)
        _ = min(int(angle / s.bucket_width), s.num_buckets - 1)
        vals.append(time.perf_counter_ns() - t0)
    return vals


def main():
    print("Running ABLKM reproducibility benchmark")
    print(f"Trials={TRIALS}, warmups={WARMUPS}, qubits={QUBITS}")
    print(f"ABLKM: grid={GRID_SIZE}, dim={DIM}, points_per_bucket={POINTS_PER_BUCKET}")

    measurements = {
        "BB84 simulation + derivation": benchmark_bb84(),
        "P_ref AES-GCM protection/recovery": benchmark_pref_exchange(),
        "ABLKM geometric mapping": benchmark_geometry(),
        "ABLKM store": benchmark_ablkm_store(),
        "ABLKM retrieval": benchmark_ablkm_get(),
        "Baseline secure-dictionary store": benchmark_baseline_store(),
        "Baseline secure-dictionary retrieval": benchmark_baseline_get(),
    }

    rows = []
    for name, vals in measurements.items():
        mean, sd = stats(vals)
        row = {"operation": name, "trials": TRIALS, "warmups": WARMUPS,
               "mean_ms": f"{mean:.6f}", "std_ms": f"{sd:.6f}"}
        rows.append(row)
        print(f"{name:42s}: {mean:.4f} ms ± {sd:.4f} ms")

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    ENV.write_text("\n".join([
        f"python={platform.python_version()}",
        f"platform={platform.platform()}",
        f"processor={platform.processor()}",
        f"trials={TRIALS}", f"warmups={WARMUPS}", f"qubits={QUBITS}",
        f"grid_size={GRID_SIZE}", f"dim={DIM}", f"points_per_bucket={POINTS_PER_BUCKET}",
        "timer=time.perf_counter_ns",
        "bb84_stdout_suppressed=True",
    ]) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT}")
    print(f"Wrote {ENV}")


if __name__ == "__main__":
    main()
