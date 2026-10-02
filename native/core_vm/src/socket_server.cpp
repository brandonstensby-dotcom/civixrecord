#include "socket_server.hpp"

#include <algorithm>
#include <chrono>
#include <cstring>
#include <iostream>

#if defined(_WIN32)
#if defined(__has_include)
#if __has_include(<afunix.h>)
#include <afunix.h>
#define CIVIX_HAVE_AF_UNIX 1
#endif
#endif
#else
#include <sys/stat.h>
#define CIVIX_HAVE_AF_UNIX 1
#endif

namespace civix::vm {

namespace {

inline uint16_t to_big_endian16(uint16_t val) noexcept {
    return static_cast<uint16_t>((val >> 8) | (val << 8));
}

inline uint32_t to_big_endian32(uint32_t val) noexcept {
    return ((val >> 24) & 0x000000FF) |
           ((val >> 8)  & 0x0000FF00) |
           ((val << 8)  & 0x00FF0000) |
           ((val << 24) & 0xFF000000);
}

inline uint64_t to_big_endian64(uint64_t val) noexcept {
    return ((val >> 56) & 0x00000000000000FFULL) |
           ((val >> 40) & 0x000000000000FF00ULL) |
           ((val >> 24) & 0x0000000000FF0000ULL) |
           ((val >> 8)  & 0x00000000FF000000ULL) |
           ((val << 8)  & 0x000000FF00000000ULL) |
           ((val << 24) & 0x0000FF0000000000ULL) |
           ((val << 40) & 0x00FF000000000000ULL) |
           ((val << 56) & 0xFF00000000000000ULL);
}

} // anonymous namespace

IpcSocketServer::IpcSocketServer(MicroVmKernel& kernel, const std::string& endpoint)
    : kernel_(kernel) {
    configure_endpoint_parsing(endpoint);
}

IpcSocketServer::~IpcSocketServer() {
    stop();
#if defined(_WIN32)
    if (wsa_initialized_) {
        WSACleanup();
        wsa_initialized_ = false;
    }
#endif
}

bool IpcSocketServer::configure_endpoint_parsing(const std::string& endpoint) {
    config_.endpoint = endpoint;

    if (endpoint.rfind("unix:", 0) == 0) {
        config_.protocol = TransportProtocol::UnixDomainSocket;
        config_.unix_socket_path = endpoint.substr(5);
        return true;
    }

    if (!endpoint.empty() && (endpoint[0] == '/' || endpoint.find(".ipc") != std::string::npos || endpoint.find(".sock") != std::string::npos)) {
        config_.protocol = TransportProtocol::UnixDomainSocket;
        config_.unix_socket_path = endpoint;
        return true;
    }

    config_.protocol = TransportProtocol::TcpLoopback;
    auto colon_pos = endpoint.find(':');
    if (colon_pos != std::string::npos) {
        config_.host = endpoint.substr(0, colon_pos);
        try {
            config_.port = static_cast<uint16_t>(std::stoi(endpoint.substr(colon_pos + 1)));
        } catch (...) {
            config_.port = 9443;
        }
    } else {
        try {
            config_.port = static_cast<uint16_t>(std::stoi(endpoint));
            config_.host = "127.0.0.1";
        } catch (...) {
            config_.host = endpoint;
            config_.port = 9443;
        }
    }

    return true;
}

bool IpcSocketServer::initialize() {
#if defined(_WIN32)
    if (!wsa_initialized_) {
        WSADATA wsa_data;
        int res = WSAStartup(MAKEWORD(2, 2), &wsa_data);
        if (res != 0) {
            std::cerr << "[-] WSAStartup failed with error: " << res << "\n";
            return false;
        }
        wsa_initialized_ = true;
    }
#endif

    return setup_listener_socket();
}

bool IpcSocketServer::make_socket_nonblocking(socket_handle_t sock) {
#if defined(_WIN32)
    u_long mode = 1;
    return ioctlsocket(sock, FIONBIO, &mode) == 0;
#else
    int flags = fcntl(sock, F_GETFL, 0);
    if (flags == -1) {
        return false;
    }
    return fcntl(sock, F_SETFL, flags | O_NONBLOCK) == 0;
#endif
}

void IpcSocketServer::close_socket_handle(socket_handle_t& sock) {
    if (sock != CIVIX_INVALID_SOCKET) {
#if defined(_WIN32)
        closesocket(sock);
#else
        close(sock);
#endif
        sock = CIVIX_INVALID_SOCKET;
    }
}

bool IpcSocketServer::setup_listener_socket() {
    close_socket_handle(listener_sock_);

    if (config_.protocol == TransportProtocol::TcpLoopback) {
        listener_sock_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (listener_sock_ == CIVIX_INVALID_SOCKET) {
            std::cerr << "[-] Failed to create TCP socket\n";
            return false;
        }

        int opt = 1;
#if defined(_WIN32)
        setsockopt(listener_sock_, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<const char*>(&opt), sizeof(opt));
#else
        setsockopt(listener_sock_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

        sockaddr_in saddr{};
        saddr.sin_family = AF_INET;
        saddr.sin_port = htons(config_.port);
        if (inet_pton(AF_INET, config_.host.c_str(), &saddr.sin_addr) <= 0) {
            saddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        }

        if (bind(listener_sock_, reinterpret_cast<sockaddr*>(&saddr), sizeof(saddr)) == CIVIX_SOCKET_ERROR) {
            std::cerr << "[-] Failed to bind TCP socket to " << config_.host << ":" << config_.port << "\n";
            close_socket_handle(listener_sock_);
            return false;
        }
    } else {
#if defined(CIVIX_HAVE_AF_UNIX)
        listener_sock_ = socket(AF_UNIX, SOCK_STREAM, 0);
        if (listener_sock_ == CIVIX_INVALID_SOCKET) {
            std::cerr << "[-] Failed to create Unix domain socket\n";
            return false;
        }

#if !defined(_WIN32)
        unlink(config_.unix_socket_path.c_str());
#endif

        sockaddr_un uaddr{};
        uaddr.sun_family = AF_UNIX;
        std::strncpy(uaddr.sun_path, config_.unix_socket_path.c_str(), sizeof(uaddr.sun_path) - 1);

        if (bind(listener_sock_, reinterpret_cast<sockaddr*>(&uaddr), sizeof(uaddr)) == CIVIX_SOCKET_ERROR) {
            std::cerr << "[-] Failed to bind Unix domain socket to " << config_.unix_socket_path << "\n";
            close_socket_handle(listener_sock_);
            return false;
        }
#if !defined(_WIN32)
        chmod(config_.unix_socket_path.c_str(), 0666);
#endif
#else
        std::cerr << "[-] Unix domain sockets not supported on this platform build\n";
        return false;
#endif
    }

    if (listen(listener_sock_, config_.backlog) == CIVIX_SOCKET_ERROR) {
        std::cerr << "[-] Failed to listen on socket\n";
        close_socket_handle(listener_sock_);
        return false;
    }

    if (!make_socket_nonblocking(listener_sock_)) {
        std::cerr << "[-] Failed to set non-blocking mode on listener socket\n";
        close_socket_handle(listener_sock_);
        return false;
    }

    return true;
}

bool IpcSocketServer::start_background() {
    if (is_running_.load()) {
        return true;
    }

    if (!initialize()) {
        return false;
    }

    should_terminate_.store(false);
    is_running_.store(true);

    worker_thread_ = std::make_unique<std::thread>(&IpcSocketServer::run, this);
    return true;
}

void IpcSocketServer::run() {
    is_running_.store(true);

    while (!should_terminate_.load()) {
        poll_step(config_.poll_timeout_ms);
    }

    is_running_.store(false);
}

void IpcSocketServer::poll_step(int timeout_ms) {
    if (listener_sock_ == CIVIX_INVALID_SOCKET) {
        return;
    }

    fd_set read_fds;
    FD_ZERO(&read_fds);
    FD_SET(listener_sock_, &read_fds);

    timeval tv{};
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    int nfds = static_cast<int>(listener_sock_ + 1);
    int select_res = select(nfds, &read_fds, nullptr, nullptr, &tv);

    if (select_res > 0 && FD_ISSET(listener_sock_, &read_fds)) {
        socket_handle_t client_sock = accept(listener_sock_, nullptr, nullptr);
        if (client_sock != CIVIX_INVALID_SOCKET) {
            metrics_.connections_accepted++;
            handle_accepted_client(client_sock);
        }
    }
}

void IpcSocketServer::handle_accepted_client(socket_handle_t client_sock) {
    std::vector<uint8_t> buffer;
    buffer.reserve(65536);
    uint8_t chunk[4096];

    // Read with bounded non-blocking loop
    int read_attempts = 0;
    constexpr int max_attempts = 15;

    while (read_attempts < max_attempts) {
        fd_set c_fds;
        FD_ZERO(&c_fds);
        FD_SET(client_sock, &c_fds);

        timeval c_tv{};
        c_tv.tv_sec = 0;
        c_tv.tv_usec = 10000; // 10ms slice

        int sel = select(static_cast<int>(client_sock + 1), &c_fds, nullptr, nullptr, &c_tv);
        if (sel > 0 && FD_ISSET(client_sock, &c_fds)) {
#if defined(_WIN32)
            int n = recv(client_sock, reinterpret_cast<char*>(chunk), sizeof(chunk), 0);
#else
            ssize_t n = recv(client_sock, chunk, sizeof(chunk), 0);
#endif
            if (n > 0) {
                buffer.insert(buffer.end(), chunk, chunk + n);
                metrics_.bytes_received += static_cast<uint64_t>(n);
                if (buffer.size() >= config_.max_payload_bytes) {
                    break;
                }
            } else if (n == 0) {
                // Client closed writer side
                break;
            } else {
                break;
            }
        } else {
            if (!buffer.empty()) {
                // Done reading current burst
                break;
            }
            read_attempts++;
        }
    }

    if (!buffer.empty()) {
        process_and_execute_stream(client_sock, buffer.data(), buffer.size());
    } else {
        send_ack_packet(client_sock, 0x02, 0, 0, 0); // PROTO_ERROR underflow
    }

    close_socket_handle(client_sock);
}

bool IpcSocketServer::process_and_execute_stream(socket_handle_t client_sock,
                                                 const uint8_t* buffer,
                                                 size_t length) {
    VmExecutionResult result = kernel_.execute_bytecode(buffer, length);

    uint8_t status = result.success ? 0x00 : 0x01;
    auto duration_us = static_cast<uint32_t>(result.duration.count());
    auto inst_count = static_cast<uint16_t>(result.instructions_executed);

    if (result.success) {
        metrics_.frames_executed += result.instructions_executed;
    } else {
        metrics_.errors_encountered++;
    }

    send_ack_packet(client_sock, status, inst_count, duration_us, result.bytes_processed);
    return result.success;
}

void IpcSocketServer::send_ack_packet(socket_handle_t client_sock,
                                      uint8_t status,
                                      uint16_t inst_count,
                                      uint32_t duration_us,
                                      uint64_t bytes_proc) {
    IpcAckPacket ack{};
    ack.preamble = 0xAA;
    ack.status_code = status;
    ack.instructions_count = to_big_endian16(inst_count);
    ack.duration_us = to_big_endian32(duration_us);
    ack.bytes_processed = to_big_endian64(bytes_proc);

#if defined(_WIN32)
    int sent = send(client_sock, reinterpret_cast<const char*>(&ack), sizeof(ack), 0);
#else
    ssize_t sent = send(client_sock, &ack, sizeof(ack), 0);
#endif

    if (sent > 0) {
        metrics_.bytes_transmitted += static_cast<uint64_t>(sent);
    }
}

void IpcSocketServer::stop() {
    should_terminate_.store(true);
    if (worker_thread_ && worker_thread_->joinable()) {
        worker_thread_->join();
        worker_thread_.reset();
    }
    close_socket_handle(listener_sock_);
    is_running_.store(false);

    if (config_.protocol == TransportProtocol::UnixDomainSocket) {
#if !defined(_WIN32)
        unlink(config_.unix_socket_path.c_str());
#endif
    }
}

} // namespace civix::vm
