CXX = g++

CXX_FLAGS = -I./lib/websocketpp 
LD_FLAGS = -lboost_system -lboost_program_options -lpthread


ws_broadcast: main.o broadcast_server.o video_stream_stdin.o
	$(CXX) -o ws_broadcast main.o broadcast_server.o video_stream_stdin.o $(LD_FLAGS) 

%.o: %.cpp
	$(CXX) -c $< $(CXX_FLAGS)
