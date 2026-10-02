#pragma once

#include <cstdint>
#include <string_view>

namespace civix::vm {

enum class Opcode : uint8_t {
    OP_NOP                  = 0x00,
    OP_INIT_AUDIO_SINK      = 0x10,
    OP_CUSUM_SEGMENT        = 0x12,
    OP_NEURAL_TOKENIZE      = 0x18,
    OP_STATUTORY_INDEX      = 0x19,
    OP_PARLIAMENTARY_STATE  = 0x24,
    OP_MERMAID_SYNTHESIS    = 0x30,
    OP_CRYPTO_SEAL_BUNDLE   = 0x40,
    OP_YOUTUBE_DISPATCH     = 0x55,
    OP_BLE_HEADSET_SYNC     = 0x60,
    OP_GLASSES_OPTICAL_SYNC = 0x61,
    OP_PEN_RECORDER_SYNC    = 0x62,
    OP_HALT_GATE            = 0xFF
};

constexpr std::string_view opcode_to_string(Opcode op) {
    switch (op) {
        case Opcode::OP_NOP: return "OP_NOP";
        case Opcode::OP_INIT_AUDIO_SINK: return "OP_INIT_AUDIO_SINK";
        case Opcode::OP_CUSUM_SEGMENT: return "OP_CUSUM_SEGMENT";
        case Opcode::OP_NEURAL_TOKENIZE: return "OP_NEURAL_TOKENIZE";
        case Opcode::OP_STATUTORY_INDEX: return "OP_STATUTORY_INDEX";
        case Opcode::OP_PARLIAMENTARY_STATE: return "OP_PARLIAMENTARY_STATE";
        case Opcode::OP_MERMAID_SYNTHESIS: return "OP_MERMAID_SYNTHESIS";
        case Opcode::OP_CRYPTO_SEAL_BUNDLE: return "OP_CRYPTO_SEAL_BUNDLE";
        case Opcode::OP_YOUTUBE_DISPATCH: return "OP_YOUTUBE_DISPATCH";
        case Opcode::OP_BLE_HEADSET_SYNC: return "OP_BLE_HEADSET_SYNC";
        case Opcode::OP_GLASSES_OPTICAL_SYNC: return "OP_GLASSES_OPTICAL_SYNC";
        case Opcode::OP_PEN_RECORDER_SYNC: return "OP_PEN_RECORDER_SYNC";
        case Opcode::OP_HALT_GATE: return "OP_HALT_GATE";
        default: return "OP_UNKNOWN";
    }
}

} // namespace civix::vm
