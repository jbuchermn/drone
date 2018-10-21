#include <vector>

// #include "broadcast_server.h"

typedef std::vector<uint8_t> frame_t;

class video_stream_stdin{
private:
    // broadcast_server* server;

    std::vector<uint8_t> buffer;
    int buffer_pos;

    std::vector<uint8_t> delimiter;
    int frame_start_pos;

private:
    void process_buffer();

public:
    // video_stream_stdin(broadcast_server* server, std::vector<uint8_t> delimiter);
    video_stream_stdin(std::vector<uint8_t> delimiter);

    void main_loop();
};
