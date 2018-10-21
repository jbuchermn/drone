#include "broadcast_server.h"

broadcast_server::broadcast_server() {
    server.set_reuse_addr(true);
    server.init_asio();
    server.clear_access_channels(websocketpp::log::alevel::frame_header | websocketpp::log::alevel::frame_payload);
    server.set_open_handler(bind(&broadcast_server::on_open,this,::_1));
    server.set_close_handler(bind(&broadcast_server::on_close,this,::_1));
    server.set_message_handler(bind(&broadcast_server::on_message,this,::_1,::_2));
}

void broadcast_server::run(uint16_t port) {
    server.listen(port);
    server.start_accept();

    try {
        server.run();
    } catch (const std::exception & e) {
        std::cout << e.what() << std::endl;
    }
}

void broadcast_server::on_open(connection_hdl hdl) {
    lock_guard<mutex> guard(connections_lock);
    connections.insert(hdl);
}

void broadcast_server::on_close(connection_hdl hdl) {
    lock_guard<mutex> guard(connections_lock);
    connections.erase(hdl);
}

void broadcast_server::on_message(connection_hdl hdl, server_t::message_ptr msg) {
    // We do not care about messages from clients
}

void broadcast_server::dispatch(frame_t&& frame){
    {
        lock_guard<mutex> guard(frames_lock);
        frames.push(frame);
    }

    {
        lock_guard<mutex> guard(action_lock);
        action.notify_one();
    }
}

void broadcast_server::process_messages() {
    for(;;) {
        unique_lock<mutex> lock(action_lock);
        while(frames.empty()) action.wait(lock);

    while(frames.size() > 3) frames.pop();

        frame_t frame;
        {
            lock_guard<mutex> guard(frames_lock);
            frame = std::move(frames.front());
            frames.pop();
        }

        lock_guard<mutex> guard(connections_lock);
        for (auto it = connections.begin(); it != connections.end(); ++it) {
            server.send(*it, frame.data(), frame.size(), websocketpp::frame::opcode::binary);
        }
    }
}

