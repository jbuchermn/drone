#include <iostream>

#include "broadcast_server.h"
#include "video_stream_stdin.h"

#include <boost/program_options.hpp>

namespace po = boost::program_options;


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
        bool first = true;
		for(auto s: delim){
            uint8_t tmp = 0;
	    	if(s >= '0' and s<= '9'){
				tmp = s - '0';
			}else if(s >= 'a' and s <= 'f'){
				tmp = s - 'a' + 10;
			}else if(s >= 'A' and s <= 'F'){
				tmp = s - 'A' + 10;
			}else{
				std::cout << "Unsupported: " << s << std::endl;
				exit(1);
			}

            if(first){
                delimiter.push_back(16 * tmp);
            }else{
                delimiter.back() += tmp;
            }

            first = !first;
		}
    }else{
        std::cout << "Need to supply delimiter" << std::endl;
        exit(1);
    }

    std::cout << "Starting WS server on port " << port << ", delimiter = ";
    for(auto v: delimiter){
        std::cout << int(v) << " ";
    }
    std::cout << std::endl;

    try {
        broadcast_server server;
        // video_stream_stdin stream(&server, delimiter);
        video_stream_stdin stream(delimiter);

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
