# ABLKM v1.0.0 — Reproducibility Artifact

## Overview

This release provides the reproducibility artifact accompanying:

**ABLKM: A Hybrid BB84 QKD and Geometric Indexing Framework for Secure Local Key Registries**

The artifact contains the Python prototype, benchmark implementation and results, IEEE-style paper source/PDF, and an interactive browser-based visualization.

## Contents

- paper/ — IEEE-style paper source and compiled PDF.
- src/ — Python implementation of the BB84 simulation, ABLKM geometric registry, and hybrid workflow.
- experiments/ — benchmark script.
- esults/ — benchmark results and environment information.
- web_demo/ — browser-based conceptual visualization.
- equirements.txt — Python dependencies.
- CITATION.cff — citation metadata.
- .zenodo.json — Zenodo metadata.
- SHA256SUMS.txt — SHA-256 checksums for artifact files.

## Experimental Configuration

The benchmark configuration uses:

- 1024 BB84 qubits
- ABLKM grid dimension: 3D
- Grid parameter: N = 6
- 4 lattice points per angular bucket
- 10 warm-up trials
- 100 measured trials
- 	ime.perf_counter_ns() for timing
- No database or network I/O in the timed operations

The intended target environment is Windows 11 with an Intel Core i7-1165G7 processor, 16 GB RAM, and Python 3.11.

The packaged benchmark results were produced in a separate reference execution environment and should not be interpreted as measurements from the target hardware.

## Security Scope

ABLKM is presented as a geometric indexing and local key-registry mechanism integrated with a software BB84 simulation.

This artifact does **not** claim that the geometric construction itself provides post-quantum cryptographic hardness equivalent to established lattice-based cryptographic schemes. In particular, no security claim based on CVP, SVP, Module-LWE, or related lattice-hardness assumptions is made.

The BB84 component is a software simulation and does not model a complete physical QKD deployment, including optical losses, detector characteristics, authenticated classical communication, full error correction, or a composable security proof.

## Cryptographic Components

The prototype uses:

- HMAC-SHA256 for registry lookup identifiers
- HKDF-SHA256 for key derivation
- AES-256-GCM for authenticated encryption

## Benchmark Interpretation

For the tested single-record workload, the complete ABLKM store/retrieval operations have higher measured overhead than the authenticated dictionary baseline.

The geometric mapping component itself is lightweight; the benchmark is intended to characterize the prototype implementation rather than establish universal performance advantages.

## Web Demonstration

The web_demo/ directory contains a browser-based visualization of the geometric indexing concept.

The web demonstration is for visualization and interaction only. It is **not** a security implementation and does not replace the Python prototype's cryptographic components.

## Version

Release: **v1.0.0**

This is the initial DOI-oriented reproducibility artifact release.

## Reproducibility

See the root README.md and the files under experiments/ and esults/ for instructions and recorded benchmark information.

## Citation

If you use this artifact, please cite the associated paper and this software/reproducibility release.

