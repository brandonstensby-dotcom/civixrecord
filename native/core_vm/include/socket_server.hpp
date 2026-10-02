#pragma once

#include "micro_vm.hpp"

#include <atomic>
#include <cstdint>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#if defined(_WIN32)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
using socket_handle_t = SOCKET;
constexpr socket_handle_t CIVIX_INVALID_SOCKET = INVALID_SOCKET;
constexpr int CIVIX_SOCKET_ERROR = SOCKET_ERROR;
#else
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
using socket_handle_t = int;
constexpr socket_handle_t CIVIX_INVALID_SOCKET = -1;
constexpr int CIVIX_SOCKET_ERROR = -1;
#endif

namespace civix::vm {

enum class TransportProtocol {
    TcpLoopback,
    UnixDomainSocket
};

struct IpcServerConfig {
    std::string endpoint{"127.0.0.1:9443"};
    std::string host{"127.0.0.1"};
    uint16_t port{9443};
    std::string unix_socket_path{"/var/run/civixrecord/core_engine.ipc"};
    TransportProtocol protocol{TransportProtocol::TcpLoopback};
    size_t max_payload_bytes{4 * 1024 * 1024}; // 4 MB safety limit
    int backlog{16};
    int poll_timeout_ms{20};
};

struct IpcServerMetrics {
    uint64_t connections_accepted{0};
    uint64_t frames_executed{0};
    uint64_t bytes_received{0};
    uint64_t bytes_transmitted{0};
    uint64_t errors_encountered{0};
};

#pragma pack(push, 1)
struct IpcAckPacket {
    uint8_t preamble;           // 0xAA sync byte
    uint8_t status_code;        // 0x00 = OK, 0x01 = EXEC_ERROR, 0x02 = PROTO_ERROR
    uint16_t instructions_count;// Big-endian executed instructions
    uint32_t duration_us;       // Big-endian execution duration in microseconds
    uint64_t bytes_processed;   // Big-endian processed payload bytes
};
#pragma pack(pop)

class IpcSocketServer {
public:
    explicit IpcSocketServer(MicroVmKernel& kernel, const std::string& endpoint = "127.0.0.1:9443");
    ~IpcSocketServer();

    IpcSocketServer(const IpcSocketServer&) = delete;
    IpcSocketServer& operator=(const IpcSocketServer&) = delete;

    bool initialize();
    bool start_background();
    void run();
    void stop();

    void poll_step(int timeout_ms);

    [[nodiscard]] bool is_running() const noexcept { return is_running_.load(); }
    [[nodiscard]] const IpcServerConfig& config() const noexcept { return config_; }
    [[nodiscard]] const IpcServerMetrics& metrics() const noexcept { return metrics_; }

private:
    bool configure_endpoint_parsing(const std::string& endpoint);
    bool setup_listener_socket();
    bool make_socket_nonblocking(socket_handle_t sock);
    void close_socket_handle(socket_handle_t& sock);
    void handle_accepted_client(socket_handle_t client_sock);
    bool process_and_execute_stream(socket_handle_t client_sock, const uint8_t* buffer, size_t length);
    void send_ack_packet(socket_handle_t client_sock, uint8_t status, uint16_t inst_count,
                         uint32_t duration_us, uint64_t bytes_proc);

    MicroVmKernel& kernel_;
    IpcServerConfig config_;
    IpcServerMetrics metrics_{};
    std::atomic<bool> is_running_{false};
    std::atomic<bool> should_terminate_{false};
    socket_handle_t listener_sock_{CIVIX_INVALID_SOCKET};
    std::unique_ptr<std::thread> worker_thread_{nullptr};

#if defined(_WIN32)
    bool wsa_initialized_{false};
#endif
};

} // namespace civix::vm
