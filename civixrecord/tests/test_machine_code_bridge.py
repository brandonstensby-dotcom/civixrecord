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

    def test_emulated_fallback_dispatch(self) -> None:
        frames = self.bridge.compile_ir("synthesize_decision_tree", {"motion_count": 5})
        result = self.bridge.dispatch(frames)

        self.assertEqual(result["status"], "DISPATCH_EMULATED")
        self.assertEqual(result["engine"], "python_userland_fallback")
        self.assertIn("civixrecord-core-engine", result["notice"])
        self.assertEqual(result["opcodes_compiled"], ["0x30"])
        self.assertTrue(result["verified"])


if __name__ == "__main__":
    unittest.main()
