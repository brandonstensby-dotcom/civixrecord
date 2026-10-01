# CivixRecord-OS

[![CI Status](https://github.com/brandonstensby-dotcom/civixrecord/actions/workflows/ci.yml/badge.svg)](https://github.com/brandonstensby-dotcom/civixrecord/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Architecture: Micro--VM](https://img.shields.io/badge/ISA-CIVIX--IR--v2.1-orange)](https://github.com/brandonstensby-dotcom/civixrecord)

CivixRecord-OS is an open-architecture, cross-platform civic intelligence and meeting automation suite. It automates municipal meeting audio capture, procedural motion extraction, roll-call voting records, and compiles deterministic Mermaid.js decision trees.

---

## Key Features

- **Autonomous Meeting Ingestion:** Connects headless capture bots to Zoom, Microsoft Teams, WebRTC, and municipal YouTube livestreams.
- **Mandatory In-Camera Gate:** Physically disconnects/mutes ingestion when council enters closed executive sessions.
- **Procedural Motion Parser:** Detects motions, movers, seconders, and roll-call votes in real-time.
- **Deterministic Flowcharts:** Synthesizes structured Mermaid.js procedural diagrams from meeting transcripts.
- **Hardware Bridge Interface:** Dispatches dense binary opcodes to high-throughput native micro-VMs or runs cleanly via pure-Python emulation.

---

## Quickstart

### Installation

```bash
git clone https://github.com/brandonstensby-dotcom/civixrecord.git
cd civixrecord
pip install -e .
```

### Run System Diagnostics

```bash
civixrecord doctor
```

### Parse Meeting Motions & Synthesize Flowchart

```bash
civixrecord analyze --transcript sample_transcript.json --output meeting_decision_tree.mmd
```

### Inspect Micro-VM Bridge & Run Benchmarks

```bash
civixrecord bridge --probe
civixrecord bridge --benchmark
```

---

## Ecosystem Architecture & Repository Grid

CivixRecord-OS is structured as a public open-source coordination core with specialized enterprise modules:

```
                                +-----------------------------------+
                                |          civixrecord-os           |
                                |     (Public Coordination Core)    |
                                +-----------------------------------+
                                                  |
                    +-----------------------------+-----------------------------+
                    |                             |                             |
                    v                             v                             v
+-------------------------------+ +-------------------------------+ +-------------------------------+
|    civixrecord-core-engine    | |   civixrecord-mobile-suite    | | civixrecord-desktop-runtime   |
|   (Private Native Micro-VM)   | |  (Private Cross-Platform App) | |  (Private Loopback Drivers)   |
+-------------------------------+ +-------------------------------+ +-------------------------------+
                    |                                                           |
                    +-----------------------------+-----------------------------+
                                                  |
                    +-----------------------------+-----------------------------+
                    |                                                           |
                    v                                                           v
+-------------------------------+                           +-------------------------------+
|   civixrecord-edge-hardware   |                           |     civixrecord-neural-vault  |
|  (Private Sensor Mesh & BLE)  |                           | (Private Statutory Embeddings)|
+-------------------------------+                           +-------------------------------+
```

### Repository Catalog

| Repository | Scope / Visibility | Subsystem | Architecture |
| :--- | :--- | :--- | :--- |
| **`civixrecord`** | **Public (OSS / MIT)** | Public Coordination, CLI, Parsing & Decision Trees | Python 3.12+, Mermaid.js, Playwright |
| **`civixrecord-core-engine`** | **Enterprise Private** | Symbolic Micro-VM Bytecode Dispatcher & Kernel | C++20 / Rust, Shared Memory IPC, SIMD |
| **`civixrecord-mobile-suite`** | **Enterprise Private** | Citizen Stream Client & Real-Time Alert Engine | Flutter 3.24+, WebRTC, iOS / Android |
| **`civixrecord-desktop-runtime`** | **Enterprise Private** | Native Virtual Loopback Audio Sink & GPU Acceleration | Tauri 2.0, Rust, Windows WASAPI, macOS CoreAudio |
| **`civixrecord-neural-vault`** | **Enterprise Private** | Statutory Bylaw Embedding Models & Dialect Weights | PyTorch, ONNX Runtime, Vector Index |
| **`civixrecord-edge-hardware`** | **Enterprise Private** | Multi-Sensor BLE Mesh, Smart Glasses & Pen Digitizers | C/Rust Embedded Firmware, eBPF, Nordic nRF5340 |

---

## Edge Hardware & Multi-Sensor Ingestion (Research Spec)

CivixRecord-OS specifies integration with personal civic capture peripherals via Bluetooth Low Energy (BLE) and optical edge devices:
1. **Bluetooth Headset Arrays (`0x60` `OP_BLE_HEADSET_SYNC`):** High-fidelity dual-microphone noise suppression utilizing the Bluetooth LE Audio LC3 codec.
2. **Smart Glasses Optical Ingestion (`0x61` `OP_GLASSES_OPTICAL_SYNC`):** Head-mounted optical gaze alignment and document capture referencing zero-copy memory transport architecture (*USENIX ATC '25*).
3. **Acoustic Pen Recorders (`0x62` `OP_PEN_RECORDER_SYNC`):** Ultrasonic micro-stylus digitization for synchronizing handwritten councillor meeting notes directly to agenda audio timestamps (*ACM SenSys '24*).

---

## License

CivixRecord-OS is distributed under the [MIT License](LICENSE).
