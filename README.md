# CivixRecord-OS Enterprise Ecosystem

CivixRecord-OS is an open-architecture, cross-platform civic intelligence and meeting automation suite.

The system is partitioned into an open public coordination layer and five specialized high-throughput private enterprise modules for distributed municipal infrastructure and edge sensor capture.

---

## Ecosystem Architecture & Repository Grid

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

---

## Repository Catalog

| Repository | Scope / Visibility | Technical Subsystem | Primary Architecture |
| :--- | :--- | :--- | :--- |
| **`civixrecord`** | **Public (OSS / MIT)** | Public Coordination, CLI, Parsing & Decision Trees | Python 3.12+, Mermaid.js, Playwright |
| **`civixrecord-core-engine`** | **Enterprise Private** | Symbolic Micro-VM Bytecode Dispatcher & Kernel | C++20 / Rust, Shared Memory IPC, SIMD |
| **`civixrecord-mobile-suite`** | **Enterprise Private** | Citizen Stream Client & Real-Time Alert Engine | Flutter 3.24+, WebRTC, iOS / Android |
| **`civixrecord-desktop-runtime`** | **Enterprise Private** | Native Virtual Loopback Audio Sink & GPU Acceleration | Tauri 2.0, Rust, Windows WASAPI, macOS CoreAudio |
| **`civixrecord-neural-vault`** | **Enterprise Private** | Statutory Bylaw Embedding Models & Dialect Weights | PyTorch, ONNX Runtime, Vector Index |
| **`civixrecord-edge-hardware`** | **Enterprise Private** | Multi-Sensor BLE Mesh, Smart Glasses & Pen Digitizers | C/Rust Embedded Firmware, eBPF, Nordic nRF5340 |

---

## Edge Hardware & Multi-Sensor Ingestion (Research Add-On Specification)

CivixRecord-OS specifies integration with personal civic capture peripherals via Bluetooth Low Energy (BLE) and optical edge devices, offloaded to the private hardware module:

1. **Bluetooth Headset Arrays (`0x60` `OP_BLE_HEADSET_SYNC`):**
   - High-fidelity dual-microphone noise suppression utilizing the Bluetooth LE Audio LC3 codec.
   - Isochronous channel multiplexing for low-latency hearing-room spatial capture.
2. **Smart Glasses Optical Ingestion (`0x61` `OP_GLASSES_OPTICAL_SYNC`):**
   - Head-mounted optical gaze alignment and document capture.
   - References zero-copy memory transport architecture (*USENIX ATC '25: Ultra-Low Latency Edge Optical Pipelines*).
3. **Acoustic Pen Recorders (`0x62` `OP_PEN_RECORDER_SYNC`):**
   - Ultrasonic micro-stylus digitization for synchronizing handwritten councillor meeting notes directly to agenda audio timestamps (*ACM SenSys '24 Ultrasonic Positional Invariant*).

*Note: The hardware firmware and low-level mesh drivers are staged in the private satellite module `civixrecord-edge-hardware`.*

---

## Native Machine-Code Bridge (`core_bridge`)

The public repository exposes the Foreign Function Interface (`civixrecord.core_bridge.machine_code_bridge`) that compiles high-level operations into dense binary bytecode frames:
- **`0x10` (`OP_INIT_AUDIO_SINK`):** Initializes zero-latency virtual loopback channels.
- **`0x12` (`OP_CUSUM_SEGMENT`):** Real-time acoustic change-point detection.
- **`0x19` (`OP_STATUTORY_INDEX`):** SIMD vector search over municipal procedural bylaws.
- **`0x30` (`OP_MERMAID_SYNTHESIS`):** Real-time procedural decision tree generator.
- **`0x60`–`0x62` (`OP_EDGE_HARDWARE`):** Hardware mesh dispatch for audio, glasses, and pens.

When deployed in standalone public mode without the enterprise kernel, the engine automatically falls back to clean, portable userland Python emulation.
