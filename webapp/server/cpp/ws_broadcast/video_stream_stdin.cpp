#include <iostream>
#include <cstring>
#include <cassert>

#include "video_stream_stdin.h"

int min(int a, int b){ return a<b ? a : b; }

#define BUFFER_SIZE 10000000
#define READ_SIZE 1000

// video_stream_stdin::video_stream_stdin(broadcast_server* server, std::vector<uint8_t> delimiter): 
//     server(server), buffer(BUFFER_SIZE), delimiter(delimiter){
// 
//     assert(sizeof(uint8_t) == 1);
//     assert(int(BUFFER_SIZE / READ_SIZE) * READ_SIZE == BUFFER_SIZE);
// 
//     // Reopen stdin in binary mode
//     freopen(NULL, "rb", stdin);
// }

video_stream_stdin::video_stream_stdin(std::vector<uint8_t> delimiter): 
    buffer(BUFFER_SIZE), delimiter(delimiter){

    assert(sizeof(uint8_t) == 1);
    assert(int(BUFFER_SIZE / READ_SIZE) * READ_SIZE == BUFFER_SIZE);

    // Reopen stdin in binary mode
    freopen(NULL, "rb", stdin);
}


void video_stream_stdin::process_buffer(){
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
            // Copy frame to new location and hand over to server
            frame_t frame(i - delimiter.size() + 1 - frame_start_pos);
            std::memcpy(frame.data(), buffer.data() + frame_start_pos, frame.size());
            // server->dispatch(std::move(frame));

            frame_start_pos = i - delimiter.size() + 1;
            found = 0;
        }
    }
}

void video_stream_stdin::main_loop(){
    for(;;){
        buffer_pos = 0;
        frame_start_pos = 0;

        do{
            buffer_pos += fread(buffer.data() + buffer_pos, 1, min(READ_SIZE, BUFFER_SIZE - buffer_pos), stdin);
            process_buffer();
        }while(buffer_pos < BUFFER_SIZE);

        // Is the buffer too small to hold an entire frame?
        assert(frame_start_pos != 0);

        std::memcpy(buffer.data(), buffer.data() + frame_start_pos, BUFFER_SIZE - frame_start_pos);
    }
}
