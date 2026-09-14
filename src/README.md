# Python prototype

The Python implementation is the security-relevant prototype described in the paper.

- `qkd_bb84.py`: software simulation of BB84 key establishment.
- `lattice_crypto_v2.py`: ABLKM geometric indexing plus HMAC-SHA256, HKDF-SHA256, and AES-256-GCM.
- `hybrid_qkd_ablkm.py`: end-to-end demonstration using simulated parameter transfer.

This prototype does **not** constitute a hardware QKD implementation or a post-quantum cryptographic primitive. The BB84 implementation is a software simulation and does not model a complete optical QKD stack, error correction, authenticated classical-channel protocol, or composable security proof.
