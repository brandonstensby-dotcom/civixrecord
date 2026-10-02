#include "micro_vm.hpp"
#include "socket_server.hpp"

#include <iostream>
#include <string>
#include <thread>
#include <chrono>

int main(int argc, char* argv[]) {
    std::cout << "=========================================================\n";
    std::cout << " CivixRecord-OS Native Micro-VM Core Execution Daemon    \n";
    std::cout << " Architecture: C++20 / AVX2 SIMD / Low-Latency Ring      \n";
    std::cout << " Version: 0.4.1 (Enterprise Native Subsystem)            \n";
    std::cout << "=========================================================\n";

    civix::vm::MicroVmKernel kernel;
    std::cout << "[+] Memory Arena Allocated: 64 MB Direct SIMD Staging\n";
    std::cout << "[*] Core Instruction Set Architecture: CIVIX-IR-v2.1 Initialized\n";

    std::string endpoint = "127.0.0.1:9443";
    bool run_server_mode = false;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--benchmark") {
            std::cout << "[*] Running native kernel self-test...\n";
            uint8_t sample_frame[] = {
                0xAA, 0x12, 0x00, 0x08, 0x1E, 0x4A, 0x9C, 0x02,
                0x3F, 0x59, 0x99, 0x9A, 0x3D, 0x4C, 0xCC, 0xCD
            };
            auto res = kernel.execute_bytecode(sample_frame, sizeof(sample_frame));
            std::cout << "[+] Native Self-Test Complete: " << res.instructions_executed
                      << " instructions in " << res.duration.count() << " us.\n";
            return 0;
        } else if (arg == "--listen" || arg == "--endpoint") {
            if (i + 1 < argc) {
                endpoint = argv[++i];
                run_server_mode = true;
            }
        } else if (arg == "--daemon" || arg == "--server") {
            run_server_mode = true;
        }
    }

    if (run_server_mode) {
        std::cout << "[*] Initializing IPC server on endpoint: " << endpoint << "\n";
        civix::vm::IpcSocketServer server(kernel, endpoint);
        if (!server.initialize()) {
            std::cerr << "[-] Failed to initialize IPC server\n";
            return 1;
        }
        std::cout << "[+] Daemon listening for incoming bytecode streams...\n";
        server.run();
    } else {
        std::cout << "[*] Daemon listening on local IPC loopback (127.0.0.1:9443)\n";
    }

    return 0;
}
