#include <iostream>
#include <set>
#include <queue>

#include <boost/program_options.hpp>

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

namespace po = boost::program_options;

typedef std::vector<uint8_t> frame_t;

int min(int a, int b){ return a<b ? a : b; }

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
    broadcast_server() {
        server.init_asio();
        server.set_open_handler(bind(&broadcast_server::on_open,this,::_1));
        server.set_close_handler(bind(&broadcast_server::on_close,this,::_1));
        server.set_message_handler(bind(&broadcast_server::on_message,this,::_1,::_2));
    }

    void run(uint16_t port) {
        server.listen(port);
        server.start_accept();

        try {
            server.run();
        } catch (const std::exception & e) {
            std::cout << e.what() << std::endl;
        }
    }

    void on_open(connection_hdl hdl) {
        lock_guard<mutex> guard(connections_lock);
        connections.insert(hdl);
    }

    void on_close(connection_hdl hdl) {
        lock_guard<mutex> guard(connections_lock);
        connections.erase(hdl);
    }

    void on_message(connection_hdl hdl, server_t::message_ptr msg) {
        // We do not care about messages from clients
    }

    // Takes ownership of frame
    void dispatch(frame_t&& frame){
        {
            lock_guard<mutex> guard(frames_lock);
            frames.push(frame);
        }

        {
            lock_guard<mutex> guard(action_lock);
            action.notify_one();
        }
    }

    void process_messages() {
        for(;;) {
            unique_lock<mutex> lock(action_lock);
            while(frames.empty()) action.wait(lock);

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
};


#define BUFFER_SIZE 1000000
#define READ_SIZE 1000

class video_stream_stdin{
private:
    broadcast_server* server;

    std::vector<uint8_t> buffer;
    int buffer_pos;

    std::vector<uint8_t> delimiter;
    int frame_start_pos;

public:
    video_stream_stdin(broadcast_server* server, std::vector<uint8_t> delimiter): 
        server(server), buffer(BUFFER_SIZE), delimiter(delimiter){

        assert(sizeof(uint8_t) == 1);
        assert(int(BUFFER_SIZE / READ_SIZE) * READ_SIZE == BUFFER_SIZE);

        // Reopen stdin in binary mode
        freopen(NULL, "rb", stdin);
    }


    void process_buffer(){
        // Find frames and pass to server->dispatch
        // Frmaes start either at the total beginning of the stream
        // or with delimiter; in other words: delimiter is included
        // at the beginning of every (possibly except for the first frame)
        int found = 0;
        for(int i=frame_start_pos + 1; i<buffer_pos; i++){
            if(buffer[i] == delimiter[found]){
                found++;
            }else{
                found=0;
            }

            if(found == delimiter.size()){
                // Frame: [frame_start_pos, i - delimiter.size() + 1)
                std::cerr << "[" << frame_start_pos << "," << i - delimiter.size() + 1 << ")" << std::endl;

                // Copy frame to new location and hand over to server
                frame_t frame(i - delimiter.size() + 1 - frame_start_pos);
                std::memcpy(buffer.data() + frame_start_pos, frame.data(), frame.size());
                server->dispatch(std::move(frame));

                frame_start_pos = i - delimiter.size() + 1;
                found = 0;
            }
        }
    }

    void main_loop(){
        for(;;){
            buffer_pos = 0;
            frame_start_pos = 0;

            do{
                buffer_pos += fread(buffer.data() + buffer_pos, 1, min(READ_SIZE, BUFFER_SIZE - buffer_pos), stdin);
                process_buffer();
            }while(buffer_pos < BUFFER_SIZE);

            // Is the buffer too small to hold an entire frame?
            assert(frame_start_pos != 0);

            std::memcpy(buffer.data() + frame_start_pos, buffer.data(), BUFFER_SIZE - frame_start_pos);
        }
    }
};

int main(int argc, char* argv[]) {
    std::vector<uint8_t> delimiter;
    int port = -1;

    po::options_description desc("Allowed options");
    desc.add_options()
        ("port", po::value<int>(), "Port")
        ("delimiter", po::value<std::string>(), "delimiter in hex (without 0x)")
    ;

    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);

    if(vm.count("port")){
        port = vm["port"].as<int>();
    }else{
        std::cout << "Need to supply port" << std::endl;
        exit(1);
    }

    if(vm.count("delimiter")){
        std::string delim = vm["delimiter"].as<std::string>();
    }else{
        std::cout << "Need to supply delimiter" << std::endl;
        exit(1);
    }

    try {
        broadcast_server server;
        video_stream_stdin stream(&server, delimiter);

        thread process_thread(bind(&broadcast_server::process_messages, &server));
        thread stdin_thread(bind(&video_stream_stdin::main_loop, &stream));

        server.run(port);
        process_thread.join();
        stdin_thread.join();

    } catch (websocketpp::exception const & e) {
        std::cout << e.what() << std::endl;
    }

    return 0;
}
