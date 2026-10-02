#include "micro_vm.hpp"
#include <iostream>
#include <cstring>
#include <immintrin.h>

namespace civix::vm {

MicroVmKernel::MicroVmKernel() {
    initialize_memory_arena();
}

MicroVmKernel::~MicroVmKernel() = default;

void MicroVmKernel::initialize_memory_arena(size_t arena_bytes) {
    memory_arena_.resize(arena_bytes, 0);
    is_initialized_ = true;
}

uint32_t MicroVmKernel::calculate_crc32(const uint8_t* data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

VmExecutionResult MicroVmKernel::execute_bytecode(const uint8_t* buffer, size_t length) {
    auto start_time = std::chrono::high_resolution_clock::now();
    VmExecutionResult result{true, 0, length, std::chrono::microseconds(0), "EXECUTION_SUCCESS"};

    if (!buffer || length < sizeof(InstructionHeader)) {
        result.success = false;
        result.diagnostic_message = "BUFFER_UNDERFLOW_OR_NULL";
        return result;
    }

    size_t cursor = 0;
    while (cursor + sizeof(InstructionHeader) <= length) {
        const auto* hdr = reinterpret_cast<const InstructionHeader*>(buffer + cursor);

        if (hdr->preamble != 0xAA) {
            result.success = false;
            result.diagnostic_message = "INVALID_PREAMBLE_CORRUPTION";
            break;
        }

        uint16_t payload_len = (hdr->payload_len >> 8) | (hdr->payload_len << 8); // Big-endian decode
        cursor += sizeof(InstructionHeader);

        if (cursor + payload_len > length) {
            result.success = false;
            result.diagnostic_message = "PAYLOAD_TRUNCATED";
            break;
        }

        const uint8_t* payload = buffer + cursor;
        auto op = static_cast<Opcode>(hdr->opcode);

        if (!dispatch_instruction(op, payload, payload_len)) {
            result.success = false;
            result.diagnostic_message = "INSTRUCTION_DISPATCH_FAILURE";
            break;
        }

        cursor += payload_len;
        result.instructions_executed++;
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    result.duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
    return result;
}

bool MicroVmKernel::dispatch_instruction(Opcode op, const uint8_t* payload, uint16_t len) {
    switch (op) {
        case Opcode::OP_NOP:
            return true;
        case Opcode::OP_CUSUM_SEGMENT:
            handle_cusum_segmentation(payload, len);
            return true;
        case Opcode::OP_STATUTORY_INDEX:
            handle_statutory_simd_index(payload, len);
            return true;
        case Opcode::OP_BLE_HEADSET_SYNC:
            handle_ble_mesh_sync(payload, len);
            return true;
        case Opcode::OP_GLASSES_OPTICAL_SYNC:
            handle_optical_zero_copy(payload, len);
            return true;
        case Opcode::OP_PEN_RECORDER_SYNC:
            handle_pen_digitizer_sync(payload, len);
            return true;
        case Opcode::OP_HALT_GATE:
            return false;
        default:
            return true;
    }
}

void MicroVmKernel::handle_cusum_segmentation(const uint8_t* payload, uint16_t len) {
    if (len >= 8) {
        float threshold, drift;
        std::memcpy(&threshold, payload, 4);
        std::memcpy(&drift, payload + 4, 4);
        total_cycles_ += 100;
    }
}

void MicroVmKernel::handle_statutory_simd_index(const uint8_t* payload, uint16_t len) {
    if (len >= 16) {
        // SIMD 128-bit comparison vector
        __m128i query = _mm_loadu_si128(reinterpret_cast<const __m128i*>(payload));
        _mm_storeu_si128(reinterpret_cast<__m128i*>(memory_arena_.data()), query);
        total_cycles_ += 50;
    }
}

void MicroVmKernel::handle_ble_mesh_sync(const uint8_t* payload, uint16_t len) {
    (void)payload;
    (void)len;
    total_cycles_ += 120;
}

void MicroVmKernel::handle_optical_zero_copy(const uint8_t* payload, uint16_t len) {
    (void)payload;
    (void)len;
    total_cycles_ += 250;
}

void MicroVmKernel::handle_pen_digitizer_sync(const uint8_t* payload, uint16_t len) {
    (void)payload;
    (void)len;
    total_cycles_ += 180;
}

} // namespace civix::vm
