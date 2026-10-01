# Architecture Specification: Distributed Offload & Micro-VM IPC

## Overview
CivixRecord-OS offloads dense compute pipelines to dedicated LAN compute nodes and native local micro-VMs.

### Subsystem Topology
1. **Public Dispatcher (`civixrecord`):** Lightweight client handling WebRTC session handshake, audio packetization, and transcript streaming.
2. **Native Symbolic Micro-VM (`civixrecord-core-engine`):** High-throughput C++20 / Rust kernel executing low-latency acoustic change-point detection (`0x12` `OP_CUSUM_SEGMENT`) and vector similarity indexing (`0x19` `OP_STATUTORY_INDEX`).
3. **Hardware Mesh (`civixrecord-edge-hardware`):** BLE audio and optical frame capture multiplexing.

### Foreign Function Interface Protocol
- **Binary Frame Preamble:** `0xAA`
- **Header:** `[0xAA][Opcode: 1 Byte][Payload Length: 2 Bytes Big-Endian][CRC32: 4 Bytes Big-Endian]`
- **Payload:** Variable length raw bytes.
- **IPC Transports:**
  - Unix Domain Socket (`/var/run/civixrecord/core_engine.ipc`) on POSIX environments.
  - Localhost loopback TCP socket (`127.0.0.1:9443`) on Windows platforms.
