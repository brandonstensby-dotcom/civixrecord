#pragma once

#include "isa_opcodes.hpp"
#include <vector>
#include <memory>
#include <string>
#include <cstdint>
#include <chrono>

namespace civix::vm {

#pragma pack(push, 1)
struct InstructionHeader {
    uint8_t preamble;         // 0xAA
    uint8_t opcode;           // Opcode byte
    uint16_t payload_len;     // Big-endian length
    uint32_t crc32;           // Big-endian CRC32
};
#pragma pack(pop)

struct VmExecutionResult {
    bool success;
    uint32_t instructions_executed;
    uint64_t bytes_processed;
    std::chrono::microseconds duration;
    std::string diagnostic_message;
};

class MicroVmKernel {
public:
    MicroVmKernel();
    ~MicroVmKernel();

    void initialize_memory_arena(size_t arena_bytes = 64 * 1024 * 1024);
    VmExecutionResult execute_bytecode(const uint8_t* buffer, size_t length);

private:
    uint32_t calculate_crc32(const uint8_t* data, size_t length);
    bool dispatch_instruction(Opcode op, const uint8_t* payload, uint16_t len);

    // Subsystem hardware handlers
    void handle_cusum_segmentation(const uint8_t* payload, uint16_t len);
    void handle_statutory_simd_index(const uint8_t* payload, uint16_t len);
    void handle_ble_mesh_sync(const uint8_t* payload, uint16_t len);
    void handle_optical_zero_copy(const uint8_t* payload, uint16_t len);
    void handle_pen_digitizer_sync(const uint8_t* payload, uint16_t len);

    std::vector<uint8_t> memory_arena_;
    bool is_initialized_{false};
    uint64_t total_cycles_{0};
};

} // namespace civix::vm
