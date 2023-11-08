GUROBI_LIB=/opt/gurobi951/linux64/lib/
GUROBI_INCLUDE=/opt/gurobi951/linux64/include/
TARGET=max_th
$(TARGET): lp_max_th.cc
	g++ lp_max_th.cc -w -g -O3 -o $(TARGET) -std=c++11 -I $(GUROBI_INCLUDE) -L $(GUROBI_LIB) -lgurobi_c++ -lgurobi95
clean:
	rm $(TARGET)