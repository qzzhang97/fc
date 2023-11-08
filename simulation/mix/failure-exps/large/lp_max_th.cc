#include "gurobi_c++.h"

#include <vector>
#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <memory>
#include <fstream>
#include <set>
#include <unordered_map>
#include <algorithm>
#include <float.h>

#include <unistd.h>

#define FOR_EACH(vec) {\
      for (int l = 0; l < vec.size(); l++) { \
          if (l == vec.size() - 1) { if (vec[l] == INF) std::cout << "INF"; else std::cout << vec[l];} \
          else { if (vec[l] == INF) std::cout << "INF "; else std::cout << vec[l] << " "; } } \
          std::cout << "\n";\
      }

class Edge {
public:
  Edge(int from, int to);
  bool operator==(const Edge& other) const;
  bool operator!=(const Edge& other) const;
  std::string toString() const;
  
  bool operator<(const Edge& other) const{
    return  from_ < other.from_ 
            || from_ == other.from_ && to_ < other.to_;
  }
private:
  int from_;
  int to_;
};

Edge::Edge(int from, int to) 
  : from_(from), to_(to) {}

bool Edge::operator==(const Edge& other) const {
  return from_ == other.from_ && to_ == other.to_;
}

bool Edge::operator!=(const Edge& other) const {
  return !operator==(other);
}

std::string Edge::toString() const{
  std::string edge = "(" + std::to_string(from_) + "," + std::to_string(to_) + ")";
  return edge;
}

void ReadPath(
  const std::string& path_file, 
  std::unordered_map<int, 
    std::unordered_map<int, 
      std::vector<std::vector<int> > > >& path_pairs
) {
  // printf("ReadPath...\n");
  int source_destination_pairs, switches, to_hosts, total_hosts;
	std::ifstream ifs;

	ifs.open(path_file);
	ifs >> source_destination_pairs >> to_hosts >> switches;
	total_hosts = switches * to_hosts;
	// printf("ToRs=%d, to_hosts=%d, total_hosts=%d\n", switches, to_hosts, total_hosts);
	for (int i = 0; i < source_destination_pairs; i++) {
		int src, dst, num_paths;
		ifs >> src >> dst >> num_paths;
    // std::cout << "num_paths: " << num_paths << "\n";
		std::vector<std::vector<int> > paths;
		for (int j = 0; j < num_paths; j++) {
			std::vector<int> path;
			int path_nodes, n;
			ifs >> path_nodes;
			for (int k = 0; k < path_nodes; k++) {
				ifs >> n;
				path.push_back(n);
			}
			paths.push_back(path);
		}
		path_pairs[src][dst] = paths;
	}
	ifs.close();
}


//  g++ lp.cc -std=c++11 -I /home/qz/gurobi912/linux64/include/ -L /home/qz/gurobi912/linux64/lib/ -lgurobi_c++ -lgurobi91
double Throughput(
  std::vector<std::vector<double> >& traffic_matrix,
  std::unordered_map<int, 
    std::unordered_map<int, 
      std::vector<std::vector<int> > > >& path_pairs,
  const std::string& weight_ofile
) {
  int switches = traffic_matrix.size();
  printf("switches=%d\n", switches);
  // Edges
  std::set<Edge> edges;
  for (int src = 0; src < switches; src++) {
    for (int dst = 0; dst < switches; dst++) {
      if (src == dst) continue;
      for (auto &path : path_pairs[src][dst]) {
        for (int i = 0; i < path.size() - 1; i++) {
          edges.insert(Edge(path[i], path[i + 1]));
        }
      }
    }
  }

  /*********************
   * Gurobi Model
   ********************/
  GRBEnv *env = new GRBEnv();
  GRBModel model = GRBModel(*env);

  GRBVar throughput = model.addVar(0.0, DBL_MAX, 0.0, GRB_CONTINUOUS, "throughput");
  
  std::unordered_map<int, std::unordered_map<int, GRBVar * > > flow_vars;
  for (int i = 0; i < switches; i++) {
    for (int j = 0; j < switches; j++) {
      if ( path_pairs[i][j].size() == 0) continue;
      int path_num = path_pairs[i][j].size();
      
      flow_vars[i][j] = model.addVars(path_num, GRB_CONTINUOUS);
      
      // Set attribute of variables
      for (int k = 0; k < path_num; k++) {
        flow_vars[i][j][k].set(GRB_DoubleAttr_LB, 0.0);
        flow_vars[i][j][k].set(GRB_DoubleAttr_UB, DBL_MAX);
      }
    }
  }

  // add constraints
  for (int i = 0; i < switches; i++) { // src_host
    for (int j = 0; j < switches; j++) { // dst_host
      if (i == j) continue;
      GRBLinExpr constr = 0;
      // printf("%d -> %d paths: %d tm val: %.2f\n", i, j, path_pairs[i][j].size(), traffic_matrix[i][j]);
      for (int k = 0; k < path_pairs[i][j].size(); k++) {
        constr += flow_vars[i][j][k];
      }
      constr -= throughput * traffic_matrix[i][j];
      model.addConstr(constr, GRB_EQUAL, 0);
    }
  }

  /**
   * The sum of flow traverse to a single link cannot exceeds bandwidth
   */
  for (auto & e : edges) {
    GRBLinExpr constr = 0;
    for (int i = 0; i < switches; i++) { // src_host
      for (int j = 0; j < switches; j++) { // dst_host
        if (path_pairs[i][j].size() == 0) continue;
        const auto &paths = path_pairs[i][j];
       
        for (int k = 0; k < paths.size(); k++) { // i -> j has path num's path
          bool has_edge = false;
          for (int l = 0; l < paths[k].size() - 1; l++) {
            // edge: paths[k][l]->paths[k][l+1]
            Edge edge_compared(paths[k][l], paths[k][l+1]);
            if (e == edge_compared) {
              has_edge = true;
              break;
            }
          }
          // has Edge
          if (has_edge) {
            constr += flow_vars[i][j][k];
          }
        }

      }
    }
    model.addConstr(constr, GRB_LESS_EQUAL, 1);
  }
  
  model.setObjective(1 * throughput, GRB_MAXIMIZE);
  model.set(GRB_IntParam_OutputFlag, 0);
  // simplex use less memory
  // model.set(GRB_IntParam_Method, 0);
  // std::cout << "Optimizing...\n";
  double th = 0.0;
  try {
    model.optimize();
    if(model.get(GRB_IntAttr_Status) != GRB_OPTIMAL){
      std::cout << "not optimal " << std::endl;
    } else {
      th = model.get(GRB_DoubleAttr_ObjVal);
      // printf("%s throughput: %.6f\n", label.c_str(), model.get(GRB_DoubleAttr_ObjVal));
    }
  } catch (GRBException e) {
    std::cout << "Error code = " << e.getErrorCode() << std::endl;
    std::cout << e.getMessage() << std::endl;
  }

  //
  std::cout << "Write weight...\n";
  std::ofstream ofs;
  ofs.open(weight_ofile.c_str(), std::ios::out);
  ofs << (switches - 1) * switches << "\n";
  for (int i = 0; i < switches; i++) {
    for (int j = 0; j < switches; j++) {
      if (i == j) continue;
      int path_num = path_pairs[i][j].size();
      // format is: [src dst path_num w1 w2 ,...] 
      ofs << i << " " << j << " " << path_num << " ";
      for (int k = 0; k < path_num; k++) {
        double solution_value = flow_vars[i][j][k].get(GRB_DoubleAttr_X);
        // if (solution_value > 1e-17 && solution_value < 1e-10) solution_value = 0.0;
        // write weight
        if (traffic_matrix[i][j] == 0) {

          if (k == path_num - 1) {
            ofs << 1.0 << "\n";
          } else {
            ofs << 0.0  << " ";
          }
        } else {
          if (k == path_num - 1) {
            ofs << solution_value / (th * traffic_matrix[i][j]) << "\n";
          } else {
            ofs << solution_value / (th * traffic_matrix[i][j])  << " ";
          }
        }
      }
    }
  }
  ofs.close();

  // Prevent memory leaks
  for (int i = 0; i < switches; i++)
    for (int j = 0; j < switches; j++)
      if (flow_vars[i][j] != NULL) {
        delete[] flow_vars[i][j];
      }

  delete env;
  return th;
}


// std::vector<std::vector<double> > a2a_traffic_matrix, worst_traffic_matrix;
// std::unordered_map<int, 
//   std::unordered_map<int, 
//     std::vector<std::vector<int> > > > ecmp_path_pairs, disjoint_path_pairs, edst_path_pairs, path_pairs;
void ReadTM(std::vector<std::vector<double > > &tm, const std::string& tm_file) {
  tm.clear();
  std::ifstream ifs;
  ifs.open(tm_file.c_str());

  int switches;
  ifs >> switches;
  std::cout << "switches=" << switches << "\n";
  tm.resize(switches, std::vector<double>(switches, 0.0));
  for (int i = 0; i < switches; i++) {
    for (int j = 0; j < switches; j++) {
      ifs >> tm[i][j];
    }
  }
  ifs.close();
}

void weight_calculation() {
  char * patterns[3] = {"a2a", "worst", "random"};
  // char * patterns[5] = {"random_1", "random_2", "random_3", "random_4", "random_5"};
  int rates[3] = {30, 70, 100};
  char str_buf[256];
  
  std::unordered_map<int, 
    std::unordered_map<int, 
      std::vector<std::vector<int> > > > edst_path_pairs, disjoint_path_pairs, ecmp_path_pairs;

  std::string edst_path_file = "topo/edst/path.txt";
  std::string disjoint_path_file = "topo/disjoint/path.txt";
  std::string ecmp_path_file = "topo/ecmp/path.txt";

  ReadPath(edst_path_file, edst_path_pairs);
  ReadPath(disjoint_path_file, disjoint_path_pairs);
  ReadPath(ecmp_path_file, ecmp_path_pairs);

  int switches = 56, to_hosts = 4;
  int loop_ctrl = 3;
  std::vector<std::vector<double > > tm;
  for (int i = 0; i < loop_ctrl; i++) {

    for (int j = 0; j < loop_ctrl; j++) {
      sprintf(str_buf, "tm/%s_%d", patterns[i], rates[j]);
      std::string tm_file(str_buf);
      ReadTM(tm, tm_file);
      sprintf(str_buf, "traffic/%s/%d/edst_weight.txt", patterns[i], rates[j]);
      std::string edst_weight_ofile(str_buf);
      sprintf(str_buf, "traffic/%s/%d/disjoint_weight.txt", patterns[i], rates[j]);
      std::string disjoint_weight_ofile(str_buf);
      sprintf(str_buf, "traffic/%s/%d/ecmp_weight.txt", patterns[i], rates[j]);
      std::string ecmp_weight_ofile(str_buf);
      std::cout << "Calculating...\n";
      // Throughput(tm, edst_path_pairs, edst_weight_ofile);
      // Throughput(tm, disjoint_path_pairs, disjoint_weight_ofile);
      Throughput(tm, ecmp_path_pairs, ecmp_weight_ofile);
    }

  }
}


int main(int argc, char **argv) {
  std::cout << "PID: " << getpid() << "\n";
  //
  weight_calculation();
  return 0;
}