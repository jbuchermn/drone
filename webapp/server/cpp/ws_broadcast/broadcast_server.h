#include <queue>
#include <set>

#include <websocketpp/config/asio_no_tls.hpp>
#include <websocketpp/server.hpp>
#include <websocketpp/common/thread.hpp>

typedef websocketpp::server<websocketpp::config::asio> server_t;

using websocketpp::connection_hdl;
using websocketpp::lib::placeholders::_1;
using websocketpp::lib::placeholders::_2;
using websocketpp::lib::bind;

using websocketpp::lib::thread;
using websocketpp::lib::mutex;
using websocketpp::lib::lock_guard;
using websocketpp::lib::unique_lock;
using websocketpp::lib::condition_variable;

typedef std::vector<uint8_t> frame_t;

class broadcast_server {
private:
    server_t server;

    std::set<connection_hdl, std::owner_less<connection_hdl> > connections;
    mutex connections_lock;

    std::queue<frame_t> frames;
    mutex frames_lock;

    condition_variable action;
    mutex action_lock;

public:
    broadcast_server();

    void run(uint16_t port);
    void on_open(connection_hdl hdl);
    void on_close(connection_hdl hdl);
    void on_message(connection_hdl hdl, server_t::message_ptr msg);

    // Takes ownership of frame
    void dispatch(frame_t&& frame);
    void process_messages();
};
