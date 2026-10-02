"""
Unit Test Suite for CivixRecord-OS Machine Code Bridge & Micro-VM Dispatcher
Hermetic verification ensuring binary serialization, CRC integrity, and fallback emulation.
"""

import unittest
from civixrecord.core_bridge.machine_code_bridge import (
    MachineCodeBridge,
    MicroVmOpcode,
    BytecodeFrame,
)


class TestMachineCodeBridge(unittest.TestCase):

    def setUp(self) -> None:
        self.bridge = MachineCodeBridge(kernel_endpoint="/tmp/non_existent_mock_socket.ipc")

    def test_bytecode_frame_binary_serialization(self) -> None:
        payload = b"\x00\x00\x3E\x80"
        frame = BytecodeFrame(
            opcode=MicroVmOpcode.OP_INIT_AUDIO_SINK,
            payload_len=len(payload),
            payload=payload,
            crc32_checksum=0x12345678,
        )
        serialized = frame.serialize()

        self.assertEqual(len(serialized), 8 + len(payload))
        self.assertEqual(serialized[0], 0xAA)  # Sync magic byte
        self.assertEqual(serialized[1], 0x10)  # OP_INIT_AUDIO_SINK
        self.assertEqual(serialized[8:], payload)

    def test_compile_audio_processing_ir(self) -> None:
        frames = self.bridge.compile_ir("process_audio_stream", {"sample_rate": 48000, "threshold": 0.90})

        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0].opcode, MicroVmOpcode.OP_INIT_AUDIO_SINK)
        self.assertEqual(frames[1].opcode, MicroVmOpcode.OP_CUSUM_SEGMENT)

    def test_compile_statutory_bylaw_ir(self) -> None:
        frames = self.bridge.compile_ir("verify_statutory_bylaw", {"bylaw_id": "BL-PROC-2026"})

        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].opcode, MicroVmOpcode.OP_STATUTORY_INDEX)
        self.assertEqual(frames[0].payload_len, 16)

    def test_compile_edge_hardware_ir(self) -> None:
        # Test Bluetooth headset LC3 compilation
        headset_frames = self.bridge.compile_ir("sync_edge_hardware", {"device_type": "headset"})
        self.assertEqual(len(headset_frames), 1)
        self.assertEqual(headset_frames[0].opcode, MicroVmOpcode.OP_BLE_HEADSET_SYNC)
        self.assertEqual(headset_frames[0].payload_len, 6)

        # Test Smart Glasses optical sync compilation
        glasses_frames = self.bridge.compile_ir("sync_edge_hardware", {"device_type": "smart_glasses", "fps": 60})
        self.assertEqual(len(glasses_frames), 1)
        self.assertEqual(glasses_frames[0].opcode, MicroVmOpcode.OP_GLASSES_OPTICAL_SYNC)
        self.assertEqual(glasses_frames[0].payload_len, 8)

        # Test Acoustic Pen recorder compilation
        pen_frames = self.bridge.compile_ir("sync_edge_hardware", {"device_type": "pen_recorder", "dpi": 2400})
        self.assertEqual(len(pen_frames), 1)
        self.assertEqual(pen_frames[0].opcode, MicroVmOpcode.OP_PEN_RECORDER_SYNC)
        self.assertEqual(pen_frames[0].payload_len, 4)

    def test_emulated_fallback_dispatch(self) -> None:
        frames = self.bridge.compile_ir("synthesize_decision_tree", {"motion_count": 5})
        result = self.bridge.dispatch(frames)

        self.assertEqual(result["status"], "DISPATCH_EMULATED")
        self.assertEqual(result["engine"], "python_userland_fallback")
        self.assertIn("civixrecord-core-engine", result["notice"])
        self.assertEqual(result["opcodes_compiled"], ["0x30"])
        self.assertTrue(result["verified"])

    def test_live_socket_ipc_dispatch(self) -> None:
        import socket
        import threading
        import struct

        # Spin up a loopback socket server simulating the native Micro-VM IPC server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(5)
        port = server.getsockname()[1]
        server.settimeout(2.0)

        running = True
        def serve_clients():
            while running:
                try:
                    conn, _ = server.accept()
                    data = conn.recv(1024)
                    if data:
                        # 16-byte IpcAckPacket: [0xAA, status=0, inst_count=1, duration_us=120, bytes_proc=len(data)]
                        ack = struct.pack(">BBHIQ", 0xAA, 0x00, 1, 120, len(data))
                        conn.sendall(ack)
                    conn.close()
                except (socket.timeout, OSError):
                    break

        th = threading.Thread(target=serve_clients, daemon=True)
        th.start()

        live_bridge = MachineCodeBridge(kernel_endpoint=f"127.0.0.1:{port}")
        frames = live_bridge.compile_ir("sync_edge_hardware", {"device_type": "smart_glasses", "fps": 60})
        result = live_bridge.dispatch(frames)
        running = False
        try:
            # trigger accept to unblock
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", port))
        except Exception:
            pass
        th.join(timeout=1.0)
        server.close()

        self.assertEqual(result["status"], "DISPATCH_HARDWARE_ACCELERATED")
        self.assertEqual(result["engine"], "native_symbolic_micro_vm")
        self.assertEqual(result["frames_executed"], 1)
        self.assertTrue(result["verified"])
        self.assertTrue(result["kernel_ack"].startswith("aa00"))


if __name__ == "__main__":
    unittest.main()
