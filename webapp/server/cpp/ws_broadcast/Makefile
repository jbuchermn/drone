CXX = g++-8

CXX_FLAGS = -I./lib/websocketpp 
LD_FLAGS = -lboost_system -lboost_program_options


ws_broadcast: main.o
	$(CXX) -o ws_broadcast main.o $(LD_FLAGS) 

%.o: %.cpp
	$(CXX) -c $< $(CXX_FLAGS)
