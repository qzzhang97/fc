/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License version 2 as
* published by the Free Software Foundation;
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

#undef PGO_TRAINING
#define PATH_TO_PGO_CONFIG "path_to_pgo_config"

#include <iostream>
#include <fstream>
#include <unordered_map>
#include <time.h> 
#include "ns3/core-module.h"
#include "ns3/qbb-helper.h"
#include "ns3/point-to-point-helper.h"
#include "ns3/applications-module.h"
#include "ns3/internet-module.h"
#include "ns3/global-route-manager.h"
#include "ns3/ipv4-static-routing-helper.h"
#include "ns3/packet.h"
#include "ns3/error-model.h"
#include <ns3/rdma.h>
#include <ns3/rdma-client.h>
#include <ns3/rdma-client-helper.h>
#include <ns3/rdma-driver.h>
#include <ns3/switch-node.h>
#include <ns3/sim-setting.h>
#include <ns3/rdma-flow.h>

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <execinfo.h>
#include <signal.h>


#include "ns3/random-variable-stream.h"
#include "ns3/int-header.h"

#include <set>



using namespace ns3;
using namespace std;

NS_LOG_COMPONENT_DEFINE("GENERIC_SIMULATION");

uint32_t cc_mode = 1; // DCQCN
bool enable_qcn = true, use_dynamic_pfc_threshold = true;
uint32_t packet_payload_size = 1000, l2_chunk_size = 0, l2_ack_interval = 0;
double pause_time = 5, simulator_stop_time = 3.01;
std::string data_rate, link_delay, topology_file, flow_file, trace_file, trace_output_file;
std::string fct_output_file = "fct.txt";
std::string pfc_output_file = "pfc.txt";
std::string pkt_output_file = "packet.txt";
std::string root_output_file = "root.txt";
std::string victim_output_file = "victim.txt";
std::string tx_bytes_ouput_file = "tx_bytes.txt";
bool enable_pfc = true;
bool enable_sack = false;
bool enable_irn = false;

// LOAD BALANCING CONFIG
bool enable_weighted_hash = false;
bool enable_uniform_hash = false;
std::string weight_file = "weight.txt";
bool enable_lp = false;



double alpha_resume_interval = 55, rp_timer, ewma_gain = 1 / 16;
double rate_decrease_interval = 4;
uint32_t fast_recovery_times = 5;
std::string rate_ai, rate_hai, min_rate = "100Mb/s";
std::string dctcp_rate_ai = "1000Mb/s";

bool clamp_target_rate = false, l2_back_to_zero = false;
double error_rate_per_link = 0.0;
uint32_t has_win = 1;
uint32_t global_t = 1;
uint32_t mi_thresh = 5;
bool var_win = false, fast_react = true;
bool multi_rate = true;
bool sample_feedback = false;
double pint_log_base = 1.05;
double pint_prob = 1.0;
double u_target = 0.95;
uint32_t int_multi = 1;
bool rate_bound = true;

uint32_t ack_high_prio = 0;
uint64_t link_down_time = 0;
uint32_t link_down_A = 0, link_down_B = 0;

uint32_t enable_trace = 1;

uint32_t buffer_size = 16;

uint32_t qlen_dump_interval = 100000000, qlen_mon_interval = 100;
uint64_t qlen_mon_start = 2000000000, qlen_mon_end = 2100000000;
string qlen_mon_file;

unordered_map<uint64_t, uint32_t> rate2kmax, rate2kmin;
unordered_map<uint64_t, double> rate2pmax;

/************************************************
 * Runtime varibles
 ***********************************************/
std::ifstream topof, flowf, tracef;

NodeContainer n;

uint64_t nic_rate;

uint64_t maxRtt, maxBdp;

struct Interface{
	uint32_t idx;
	bool up;
	uint64_t delay;
	uint64_t bw;

	Interface() : idx(0), up(false){}
};
map<Ptr<Node>, map<Ptr<Node>, Interface> > nbr2if;
// Mapping destination to next hop for each node: <node, <dest, <nexthop0, ...> > >
map<Ptr<Node>, map<Ptr<Node>, vector<Ptr<Node> > > > nextHop;
map<Ptr<Node>, map<Ptr<Node>, uint64_t> > pairDelay;
map<Ptr<Node>, map<Ptr<Node>, uint64_t> > pairTxDelay;
map<uint32_t, map<uint32_t, uint64_t> > pairBw;
map<Ptr<Node>, map<Ptr<Node>, uint64_t> > pairBdp;
map<uint32_t, map<uint32_t, uint64_t> > pairRtt;

std::vector<Ipv4Address> serverAddress;

// maintain port number for each host pair
std::unordered_map<uint32_t, unordered_map<uint32_t, uint16_t> > portNumder;
void SetHpccLineRates(std::set<uint64_t>& lineRates) {
	for (auto rate : lineRates) {
		std::cout << "rate: " << rate << "\n";
	}
	NS_ASSERT_MSG(lineRates.size() <= 8, "lineRates.size must less than 8");
	IntHop::lineRateValues[0] = 1111;
	int idx = 0;
	for (auto rate : lineRates) {
		IntHop::lineRateValues[idx++] = rate;
	}
	/**
	for (int i = 0; i < 8; i ++) {
		std::cout << "hpcc rate: " << IntHop::lineRateValues[i] << "\n";
	}
	**/
}

#define INF 0xffffff
#define FOR_EACH(vec) {for (int i = 0; i < vec.size(); i++) { std::cout << vec[i] << " "; } std::cout << "\n";}

std::string path_file;
std::unordered_map<uint32_t, 
	std::unordered_map<uint32_t, 
		std::vector<std::vector<int> > > > sw_paths; // sw id start from zero
int switches, host_per_switch, total_hosts;


void ReadPath(const std::string& path_file="path.txt") {
	std::ifstream ifs;
	ifs.open(path_file);
	int pairs = 0;
	ifs >> pairs >> host_per_switch >> switches;
	total_hosts = switches * host_per_switch;
	printf("ToRs %d, hosts_per_ToR %d, total hosts %d\n", switches, host_per_switch, total_hosts);
	for (int i = 0; i < pairs; i++) {
		int src, dst, num_paths;
		ifs >> src >> dst >> num_paths;
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
		sw_paths[src][dst] = paths;
	}
	return;
}


void InstallPath(int hostA, int hostB, NodeContainer &n) {
  	// 0 host, 1 switch
	// printf("%d->%d\n", hostA, hostB);
	Ptr<Node> src_host = n.Get(hostA);
	Ptr<Node> dst_host = n.Get(hostB);
	// std::cout << "A"
	// std::cout << "dst_host ptr: " << dst_host << "\n";
	NS_ASSERT_MSG(src_host->GetNodeType()== 0, "hostA node type must be 0");
	NS_ASSERT_MSG(dst_host->GetNodeType()== 0, "hostB node type must be 0");
	Ipv4Address srcAddr = src_host->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal();
	Ipv4Address dstAddr = dst_host->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal();
		
	int src_tor = hostA / host_per_switch;
	int dst_tor = hostB / host_per_switch;
	if (src_tor == dst_tor) {
		return;
	}
	const auto &ksps = sw_paths[src_tor][dst_tor];
	if (ksps.size() == 0) {
		return;
	}
	NS_ASSERT_MSG(ksps.size() != 0, "Virtual up-down path can not be zero!!!");

	int hosts = switches * host_per_switch;
	int minimum_path_len = ksps[0].size();
	int max_path_len = ksps[ksps.size() - 1].size();
	// std::cout << "max path len: " << max_path_len << "\n";
	for (auto &path : ksps) {
		for (int i = 0; i < path.size(); i++) {
			int sw_id = hosts + path[i];
			Ptr<Node> sw =  n.Get(sw_id);
			NS_ASSERT_MSG(sw->GetNodeType()== 1, "sw node type must be 1");
			if (i == 0) {
				src_host->GetObject<RdmaDriver>()->m_rdma->AddTableEntry(dstAddr, nbr2if[src_host][sw].idx);
				//
				int sw_id2 = hosts + path[i + 1];
				Ptr<Node> sw2 =  n.Get(sw_id2);
				NS_ASSERT_MSG(sw->GetNodeType()== 1, "sw node type must be 1");
				DynamicCast<SwitchNode>(sw)->AddXpanderTableEntry(srcAddr, dstAddr, nbr2if[sw][sw2].idx , path.size() - i );
				DynamicCast<SwitchNode>(sw)->AddRRGTableEntry(srcAddr, dstAddr, nbr2if[sw][sw2].idx);
			} else if (i == path.size() - 1) {
				DynamicCast<SwitchNode>(sw)->AddXpanderTableEntry(srcAddr, dstAddr, nbr2if[sw][dst_host].idx, path.size() - i);
				DynamicCast<SwitchNode>(sw)->AddRRGTableEntry(srcAddr, dstAddr, nbr2if[sw][dst_host].idx);
			} else { // sw 2 sw connection
				int sw_id2 = hosts + path[i + 1];
				Ptr<Node> sw2 =  n.Get(sw_id2);
				NS_ASSERT_MSG(sw->GetNodeType()== 1, "sw node type must be 1");
				DynamicCast<SwitchNode>(sw)->AddXpanderTableEntry(srcAddr, dstAddr, nbr2if[sw][sw2].idx, path.size() - i);
				DynamicCast<SwitchNode>(sw)->AddRRGTableEntry(srcAddr, dstAddr, nbr2if[sw][sw2].idx);
			}
		}
	}
}

/**
 * python2 waf --run "scratch/fc mix/failure-exps/deadlock/config/up-down/config.txt"
 */

void SetMultiPathForAllHosts() {
	//
	ReadPath(path_file);
	printf("Read Path Over!!!\n");
	
	clock_t begint, endt;
	begint = clock();
	for (int i = 0; i < total_hosts; i++) {
		for (int j = 0; j < total_hosts; j++) {
			InstallPath(i, j, n);
		}
		// if (i % 300 == 0) printf("%d\n", i);
	}
	endt = clock();
	printf("Set Routes: %ds.\n", (endt - begint) / CLOCKS_PER_SEC);
	// SetHostPerSwitch(n);
}

/*********************
 * Set WCMP Weights.
 *********************/
std::unordered_map<int, std::unordered_map<int, std::vector<double> > > rtWeights; // map src_sid dst_sid to weight entries

struct LinkFlow {
	int from;
	int to;
	double flow;
	double wcmp_weight;
	LinkFlow(int _from, int _to, double _flow): from(_from), to(_to), flow(_flow) {}
    std::string toString() {
        return std::to_string(from) + ", " + std::to_string(to) + ", " + std::to_string(flow) + ", " + std::to_string(wcmp_weight);
    }

};

struct LinkFlowCompare {
	bool operator()(LinkFlow* lhs, LinkFlow* rhs) {
		return lhs->from < rhs->from || lhs->from == rhs->from && lhs->to < rhs->to;
	}
};

void CalWcmpWeight(int hostA, int hostB) {
	int src_tor = hostA / host_per_switch;
	int dst_tor = hostB / host_per_switch;
	if (src_tor == dst_tor) {
		return;
	}
	const auto &ksps = sw_paths[src_tor][dst_tor];
	const auto &weights = rtWeights[src_tor][dst_tor];
	NS_ASSERT_MSG(ksps.size() > 0 && ksps.size() == weights.size(), "the size of weights must equal to that of ksps");

	std::unordered_map<int, std::vector< LinkFlow * > > sid_map_egress_weights;
	std::unordered_map<int, std::unordered_map<int, LinkFlow * > > quick_find_link_flow;
	
    std::set<LinkFlow *, LinkFlowCompare> link_flows; 
	// initialize
	for (int i = 0; i < ksps.size(); i++) {
		const auto &path = ksps[i];
		for (int j = 0; j < path.size() - 1; j++) {
			LinkFlow* link_flow = new LinkFlow(path[j], path[j + 1], 0);
            if (link_flows.find(link_flow) != link_flows.end()) {
                // std::cout << "[Duplicate Edge]" + link_flow->toString() << "\n";
                delete link_flow;
                continue;
            }
			link_flows.insert(link_flow);
		}
	}

    for (auto link_flow: link_flows ) {
        sid_map_egress_weights[link_flow->from].push_back(link_flow);
        quick_find_link_flow[link_flow->from][link_flow->to] = link_flow;
    }

    // cal flows
    for (int i = 0; i < ksps.size(); i++) {
		const auto &path = ksps[i];
		for (int j = 0; j < path.size() - 1; j++) {
            LinkFlow *tempFlow = new LinkFlow(path[j], path[j+1], 0);
            auto finded_it = link_flows.find(tempFlow);

            if (finded_it != link_flows.end()) {
                quick_find_link_flow[path[j]][path[j+1]]->flow += weights[i];
            }
            delete tempFlow;
        }
    }

    for (auto pair : sid_map_egress_weights) {
        int sid = pair.first;
        double flow_sum = 0;
        for (auto link_flow_ptr : pair.second) {
            flow_sum += link_flow_ptr->flow;
        }
        for (auto link_flow_ptr : pair.second) {
            link_flow_ptr->wcmp_weight = link_flow_ptr->flow / flow_sum;
        }
    }

	/*** INSTALL WEIGHT [src_addr][dst_addr]***/
	Ptr<Node> src_host = n.Get(hostA);
	Ptr<Node> dst_host = n.Get(hostB);
	NS_ASSERT_MSG(src_host->GetNodeType()== 0, "hostA node type must be 0");
	NS_ASSERT_MSG(dst_host->GetNodeType()== 0, "hostB node type must be 0");
	Ipv4Address srcAddr = src_host->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal();
	Ipv4Address dstAddr = dst_host->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal();
	
	
	int hosts = total_hosts;
	int minimum_path_len = ksps[0].size();
	int max_path_len = ksps[ksps.size() - 1].size();

	for (auto pair : sid_map_egress_weights) {
		int real_sid = pair.first + total_hosts;
		Ptr<Node> sw =  n.Get(real_sid);
		for (auto link_flow : pair.second) {
			int sid_from = link_flow->from + total_hosts;
			int sid_to = link_flow->to + total_hosts;
			Ptr<Node> sw_from =  n.Get(sid_from);
			Ptr<Node> sw_to =  n.Get(sid_to);
			DynamicCast<SwitchNode>(sw)->AddRtWeight(srcAddr, dstAddr, nbr2if[sw_from][sw_to].idx, link_flow->wcmp_weight);
		}
	}

	// dst switch
	int sw_id = dst_tor + total_hosts;
	Ptr<Node> sw =  n.Get(sw_id);
	DynamicCast<SwitchNode>(sw)->AddRtWeight(srcAddr, dstAddr, nbr2if[sw][dst_host].idx, 1);

	for (auto link_flow : link_flows) {
        // std::cout << link_flow->toString() << "\n";
        delete link_flow;
    }
	
}


void InstallWeight(int hostA, int hostB) {
	CalWcmpWeight(hostA, hostB);
}

void SetWcmpWeightForAllHosts() {
	//
	std::ifstream ifs;
	ifs.open(weight_file.c_str());
	int total_entries;
	ifs >> total_entries; 
	for (int i = 0; i < total_entries; i++) {
		int src_sw, dst_sw, path_num;
		ifs >> src_sw >> dst_sw >> path_num;
		for (int j = 0; j < path_num; j++) {
			double weight;
			ifs >> weight;
			rtWeights[src_sw][dst_sw].push_back(weight);
		}
	}
	ifs.close();
    std::cout << "total hosts: " << total_hosts << "\n";
	for (int i = 0; i < total_hosts; i++) {
		if (total_hosts % 20 == 0) {
			std::cout << "total hosts=" << i << "\n";
		}
		for (int j = 0; j < total_hosts; j++) {
			InstallWeight(i, j);
		}
	}

}


/********* Schedule Flow *********/
struct FlowInput{
	uint32_t src, dst, pg, maxPacketCount, port, dport;
	double start_time;
	uint32_t idx;
	uint32_t non_shortest;
};

FlowInput flow_input = {0};
uint32_t flow_num;

void ReadFlowInput(){
	if (flow_input.idx < flow_num){
		flowf >> flow_input.src >> flow_input.dst >> flow_input.pg >> flow_input.dport >> flow_input.maxPacketCount >> flow_input.start_time >> flow_input.non_shortest;
		// std::cout << "[Read Flow]Time=" << Simulator::Now().GetTimeStep() << " flow: "<< flow_input.idx << "\n";
	}		
	NS_ASSERT(n.Get(flow_input.src)->GetNodeType() == 0 && n.Get(flow_input.dst)->GetNodeType() == 0);
}
void ScheduleFlowInputs(){
	// std::cout << "[Schedule Flow]Time=" << Simulator::Now().GetTimeStep() << " flow: "<< flow_input.idx << "\n";
	while (flow_input.idx < flow_num && Seconds(flow_input.start_time) == Simulator::Now()){
		uint32_t sport = portNumder[flow_input.src][flow_input.dst]++; // get a new port number 
		// port = 10086;
		RdmaClientHelper clientHelper(flow_input.pg, 
			serverAddress[flow_input.src], 
			serverAddress[flow_input.dst], 
			sport, 
			flow_input.dport, 
			flow_input.maxPacketCount, 
			has_win?(global_t==1?maxBdp:pairBdp[n.Get(flow_input.src)][n.Get(flow_input.dst)]):0, 
			global_t==1?maxRtt:pairRtt[flow_input.src][flow_input.dst],
			flow_input.non_shortest,
			enable_sack,
			enable_irn,
			enable_pfc
		);
		ApplicationContainer appCon = clientHelper.Install(n.Get(flow_input.src));
		appCon.Start(Time(0));

		// get the next flow input
		// std::cout << "Flow input.idx=" << flow_input.idx << "\n";
		flow_input.idx++;
		ReadFlowInput();
	}

	// schedule the next time to run this function
	if (flow_input.idx < flow_num){
		Simulator::Schedule(Seconds(flow_input.start_time) -Simulator::Now(), ScheduleFlowInputs);
	}else { // no more flows, close the file
		flowf.close();
	}
}

Ipv4Address node_id_to_ip(uint32_t id){
	return Ipv4Address(0x0b000001 + ((id / 256) * 0x00010000) + ((id % 256) * 0x00000100));
}

uint32_t ip_to_node_id(Ipv4Address ip){
	return (ip.Get() >> 8) & 0xffff;
}

void SwitchDoClearing(NodeContainer &n, Ptr<RdmaQueuePair> q) {
	// 
	for (int i = 0; i < n.GetN(); i++) {
		if (n.Get(i)->GetNodeType() == 1) // switch
			DynamicCast<SwitchNode>(n.Get(i))->ClearFlowRecord(q);
	}
}

void qp_finish(FILE* fout, Ptr<RdmaQueuePair> q){
	// switches will clean the completed flow info in their cache.
	// 
	// std::cout << "qp finish\n";
	SwitchDoClearing(n, q);
	uint32_t sid = ip_to_node_id(q->sip), did = ip_to_node_id(q->dip);
	uint64_t base_rtt = pairRtt[sid][did], b = pairBw[sid][did];
	uint32_t total_bytes = q->m_size + ((q->m_size-1) / packet_payload_size + 1) * (CustomHeader::GetStaticWholeHeaderSize() - IntHeader::GetStaticSize()); // translate to the minimum bytes required (with header but no INT)
	uint64_t standalone_fct = base_rtt + total_bytes * 8000000000lu / b;
	// sip, dip, sport, dport, size (B), start_time, fct (ns), standalone_fct (ns)
	fprintf(fout, "%u %u %u %u %lu %lu %lu %lu\n", ip_to_node_id(q->sip), ip_to_node_id(q->dip), q->sport, q->dport, q->m_size, q->startTime.GetTimeStep(), (Simulator::Now() - q->startTime).GetTimeStep(), standalone_fct);
	fflush(fout);

	// remove rxQp from the receiver
	// printf("[Delete Debug]: snode: %d dnode: %d sport: %d dport: %d flow_size: %d start_t: %d\n", 
	//  sid, did, q->sport, q->dport, q->m_size, q->startTime.GetTimeStep(), q->startTime.GetTimeStep());

	Ptr<Node> dstNode = n.Get(did);
	Ptr<RdmaDriver> rdma = dstNode->GetObject<RdmaDriver> ();
	rdma->m_rdma->DeleteRxQp(q->sip.Get(), q->m_pg, q->sport);
}

void get_pfc(FILE* fout, Ptr<QbbNetDevice> dev, uint32_t type){
	fprintf(fout, "%lu %u %u %u %u\n", Simulator::Now().GetTimeStep(), dev->GetNode()->GetId(), dev->GetNode()->GetNodeType(), dev->GetIfIndex(), type);
}

void get_pause(FILE *fout, uint32_t nodeId, uint32_t inDev, uint32_t qIndex) {
	fprintf(fout, "PAUSE %lu %u %u %u\n", Simulator::Now().GetTimeStep(), nodeId, inDev, qIndex);
	fflush(fout);
}

void get_resume(FILE *fout, uint32_t nodeId, uint32_t inDev, uint32_t qIndex) {
	fprintf(fout, "RESUME %lu %u %u %u\n", Simulator::Now().GetTimeStep(), nodeId, inDev, qIndex);
	fflush(fout);
}

void get_root(FILE *fout, Ptr<RdmaFlow> flow, uint32_t nodeId) {
	fprintf(fout, "ROOT %lu %u %u %u %u %u %u %u\n", Simulator::Now().GetTimeStep(),nodeId, flow->indev, flow->outdev, ip_to_node_id(Ipv4Address(flow->sip)), ip_to_node_id(Ipv4Address(flow->dip)), flow->sport, flow->dport);
	fflush(fout);
}

void get_victim(FILE *fout, Ptr<RdmaFlow> flow, uint32_t nodeId) {
	fprintf(fout, "VICTIM %lu %u %u %u %u %u %u %u\n", Simulator::Now().GetTimeStep(), nodeId,flow->indev, flow->outdev, ip_to_node_id(Ipv4Address(flow->sip)),ip_to_node_id(Ipv4Address(flow->dip)), flow->sport, flow->dport);
	fflush(fout);
}


void pkt_finish(FILE *fout, Ptr<Packet> p) {
	bool hasL2 = true;
	CustomHeader hdr((hasL2?CustomHeader::L2_Header:0) | CustomHeader::L3_Header | CustomHeader::L4_Header);
	p->PeekHeader(hdr);
	uint16_t sport = hdr.udp.sport;
	uint16_t dport = hdr.udp.dport;
	Ipv4Address ip(hdr.sip);
	fprintf(fout, "%u  %u %u 1000 %lu\n", ip_to_node_id(ip), ip_to_node_id(Ipv4Address(hdr.dip)), sport, Simulator::Now().GetTimeStep());
	fflush(fout);
}

void GetPortTxBytes(FILE *fout, NodeContainer &n) {
    for (int i = 0; i < n.GetN(); ++i) {
        if(n.Get(i)->GetNodeType () == 1) {
            DynamicCast<SwitchNode>(n.Get(i))->DumpPortTxBytes(fout);
        }   
    }
}

struct QlenDistribution{
	vector<uint32_t> cnt; // cnt[i] is the number of times that the queue len is i KB

	void add(uint32_t qlen){
		uint32_t kb = qlen / 1000;
		if (cnt.size() < kb+1)
			cnt.resize(kb+1);
		cnt[kb]++;
	}
};
map<uint32_t, map<uint32_t, QlenDistribution> > queue_result;
void monitor_buffer(FILE* qlen_output, NodeContainer *n){
	for (uint32_t i = 0; i < n->GetN(); i++){
		if (n->Get(i)->GetNodeType() == 1){ // is switch
			Ptr<SwitchNode> sw = DynamicCast<SwitchNode>(n->Get(i));
			if (queue_result.find(i) == queue_result.end())
				queue_result[i];
			for (uint32_t j = 1; j < sw->GetNDevices(); j++){
				uint32_t size = 0;
				for (uint32_t k = 0; k < SwitchMmu::qCnt; k++)
					size += sw->m_mmu->egress_bytes[j][k];
				queue_result[i][j].add(size);
			}
		}
	}
	if (Simulator::Now().GetTimeStep() % qlen_dump_interval == 0){
		fprintf(qlen_output, "time: %lu\n", Simulator::Now().GetTimeStep());
		for (auto &it0 : queue_result)
			for (auto &it1 : it0.second){
				fprintf(qlen_output, "%u %u", it0.first, it1.first);
				auto &dist = it1.second.cnt;
				for (uint32_t i = 0; i < dist.size(); i++)
					fprintf(qlen_output, " %u", dist[i]);
				fprintf(qlen_output, "\n");
			}
		fflush(qlen_output);
	}
	if (Simulator::Now().GetTimeStep() < qlen_mon_end)
		Simulator::Schedule(NanoSeconds(qlen_mon_interval), &monitor_buffer, qlen_output, n);
}

void CalculateRoute(Ptr<Node> host){
	// queue for the BFS.
	vector<Ptr<Node> > q;
	// Distance from the host to each node.
	map<Ptr<Node>, int> dis;
	map<Ptr<Node>, uint64_t> delay;
	map<Ptr<Node>, uint64_t> txDelay;
	map<Ptr<Node>, uint64_t> bw;
	// init BFS.
	q.push_back(host);
	dis[host] = 0;
	delay[host] = 0;
	txDelay[host] = 0;
	bw[host] = 0xfffffffffffffffflu;
	// BFS.
	for (int i = 0; i < (int)q.size(); i++){
		Ptr<Node> now = q[i];
		int d = dis[now];
		for (auto it = nbr2if[now].begin(); it != nbr2if[now].end(); it++){
			// skip down link
			if (!it->second.up)
				continue;
			Ptr<Node> next = it->first;
			// If 'next' have not been visited.
			if (dis.find(next) == dis.end()){
				dis[next] = d + 1;
				delay[next] = delay[now] + it->second.delay;
				txDelay[next] = txDelay[now] + packet_payload_size * 1000000000lu * 8 / it->second.bw;
				bw[next] = std::min(bw[now], it->second.bw);
				// we only enqueue switch, because we do not want packets to go through host as middle point
				if (next->GetNodeType() == 1)
					q.push_back(next);
			}
			// if 'now' is on the shortest path from 'next' to 'host'.
			if (d + 1 == dis[next]){
				nextHop[next][host].push_back(now);
			}
		}
	}
	for (auto it : delay)
		pairDelay[it.first][host] = it.second;
	for (auto it : txDelay)
		pairTxDelay[it.first][host] = it.second;
	for (auto it : bw)
		pairBw[it.first->GetId()][host->GetId()] = it.second;
}

void CalculateRoutes(NodeContainer &n){
	for (int i = 0; i < (int)n.GetN(); i++){
		Ptr<Node> node = n.Get(i);
		if (node->GetNodeType() == 0)
			CalculateRoute(node);
	}
}

void SetRoutingEntries(){
	// For each node.
	for (auto i = nextHop.begin(); i != nextHop.end(); i++){
		Ptr<Node> node = i->first;
		auto &table = i->second;
		for (auto j = table.begin(); j != table.end(); j++){
			// The destination node.
			Ptr<Node> dst = j->first;
			// The IP address of the dst.
			Ipv4Address dstAddr = dst->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal();
			// The next hops towards the dst.
			vector<Ptr<Node> > nexts = j->second;
			for (int k = 0; k < (int)nexts.size(); k++){
				Ptr<Node> next = nexts[k];
				uint32_t interface = nbr2if[node][next].idx;
				if (node->GetNodeType() == 1)
					DynamicCast<SwitchNode>(node)->AddTableEntry(dstAddr, interface);
				else{
					node->GetObject<RdmaDriver>()->m_rdma->AddTableEntry(dstAddr, interface);
				}
			}
		}
	}
}

// take down the link between a and b, and redo the routing
void TakeDownLink(NodeContainer n, Ptr<Node> a, Ptr<Node> b){
	if (!nbr2if[a][b].up)
		return;
	// take down link between a and b
	nbr2if[a][b].up = nbr2if[b][a].up = false;
	nextHop.clear();
	CalculateRoutes(n);
	// clear routing tables
	for (uint32_t i = 0; i < n.GetN(); i++){
		if (n.Get(i)->GetNodeType() == 1)
			DynamicCast<SwitchNode>(n.Get(i))->ClearTable();
		else
			n.Get(i)->GetObject<RdmaDriver>()->m_rdma->ClearTable();
	}
	DynamicCast<QbbNetDevice>(a->GetDevice(nbr2if[a][b].idx))->TakeDown();
	DynamicCast<QbbNetDevice>(b->GetDevice(nbr2if[b][a].idx))->TakeDown();
	// reset routing table
	SetRoutingEntries();

	// redistribute qp on each host
	for (uint32_t i = 0; i < n.GetN(); i++){
		if (n.Get(i)->GetNodeType() == 0)
			n.Get(i)->GetObject<RdmaDriver>()->m_rdma->RedistributeQp();
	}
}

uint64_t get_nic_rate(NodeContainer &n){
	for (uint32_t i = 0; i < n.GetN(); i++)
		if (n.Get(i)->GetNodeType() == 0) // host
			return DynamicCast<QbbNetDevice>(n.Get(i)->GetDevice(1))->GetDataRate().GetBitRate();
}

int read_conf(int argc, char *argv[]){

#ifndef PGO_TRAINING
	if (argc > 1)
#else
	if (true)
#endif
	{
		//Read the configuration file
		std::ifstream conf;
#ifndef PGO_TRAINING
		conf.open(argv[1]);
#else
		conf.open(PATH_TO_PGO_CONFIG);
#endif
		while (!conf.eof())
		{
			std::string key;
			conf >> key;

			//std::cout << conf.cur << "\n";

			if (key.compare("ENABLE_QCN") == 0)
			{
				uint32_t v;
				conf >> v;
				enable_qcn = v;
				if (enable_qcn)
					std::cout << "ENABLE_QCN\t\t\t" << "Yes" << "\n";
				else
					std::cout << "ENABLE_QCN\t\t\t" << "No" << "\n";
			} else if (key.compare("PATH_FILE") == 0) 
			{
				std::string v;
				conf >> v;
				path_file = v;
				std::cout << "PATH_FILE\t\t\t" << v << "\n";
			}	
			else if (key.compare("ENABLE_PFC") == 0) 
			{
				uint32_t v;
				conf >> v;
				enable_pfc = v;
				if (enable_pfc)
					std::cout << "ENABLE_PFC\t\t\t" << "Yes" << "\n";
				else
					std::cout << "ENABLE_PFC\t\t\t" << "NO" << "\n";
			}	
			else if (key.compare("ENABLE_SACK") == 0) 
			{
				uint32_t v;
				conf >> v;
				enable_sack = v;
				if (enable_sack)
					std::cout << "ENABLE_SACK\t\t\t" << "Yes" << "\n";
				else
					std::cout << "ENABLE_SACK\t\t\t" << "NO" << "\n";
			}
			else if (key.compare("ENABLE_IRN") == 0) 
			{
				uint32_t v;
				conf >> v;
				enable_irn = v;
				if (enable_irn)
					std::cout << "ENABLE_IRN\t\t\t" << "Yes" << "\n";
				else
					std::cout << "ENABLE_IRN\t\t\t" << "NO" << "\n";
			}
      else if (key.compare("ENABLE_WEIGHTED_HASH") == 0)
			{
				uint32_t v;
				conf >> v;
				enable_weighted_hash = v;
				if (enable_weighted_hash)
					std::cout << "ENABLE_WEIGHTED_HASH\t\t\t" << "Yes" << "\n";
				else
					std::cout << "ENABLE_WEIGHTED_HASH\t\t\t" << "NO" << "\n";
			}
		else if (key.compare("ENABLE_UNIFORM_HASH") == 0)
			{
				uint32_t v;
				conf >> v;
				enable_uniform_hash = v;
				if (enable_uniform_hash)
					std::cout << "ENABLE_UNIFORM_HASH\t\t\t" << "Yes" << "\n";
				else
					std::cout << "ENABLE_UNIFORM_HASH\t\t\t" << "NO" << "\n";
			}
		else if (key.compare("ENABLE_LP") == 0)
			{
				uint32_t v;
				conf >> v;
				enable_lp = v;
				if (enable_lp)
					std::cout << "ENABLE_LP\t\t\t" << "Yes" << "\n";
				else
					std::cout << "ENABLE_LP\t\t\t" << "NO" << "\n";
			}
      else if (key.compare("WEIGHT_FILE") == 0)
			{
				std::string v;
				conf >> v;
				weight_file = v;
				std::cout << "WEIGHT_FILE\t\t\t" << weight_file << "\n";
			}
			else if (key.compare("USE_DYNAMIC_PFC_THRESHOLD") == 0)
			{
				uint32_t v;
				conf >> v;
				use_dynamic_pfc_threshold = v;
				if (use_dynamic_pfc_threshold)
					std::cout << "USE_DYNAMIC_PFC_THRESHOLD\t" << "Yes" << "\n";
				else
					std::cout << "USE_DYNAMIC_PFC_THRESHOLD\t" << "No" << "\n";
			}
			else if (key.compare("CLAMP_TARGET_RATE") == 0)
			{
				uint32_t v;
				conf >> v;
				clamp_target_rate = v;
				if (clamp_target_rate)
					std::cout << "CLAMP_TARGET_RATE\t\t" << "Yes" << "\n";
				else
					std::cout << "CLAMP_TARGET_RATE\t\t" << "No" << "\n";
			}
			else if (key.compare("PAUSE_TIME") == 0)
			{
				double v;
				conf >> v;
				pause_time = v;
				std::cout << "PAUSE_TIME\t\t\t" << pause_time << "\n";
			}
			else if (key.compare("DATA_RATE") == 0)
			{
				std::string v;
				conf >> v;
				data_rate = v;
				std::cout << "DATA_RATE\t\t\t" << data_rate << "\n";
			}
			else if (key.compare("LINK_DELAY") == 0)
			{
				std::string v;
				conf >> v;
				link_delay = v;
				std::cout << "LINK_DELAY\t\t\t" << link_delay << "\n";
			}
			else if (key.compare("PACKET_PAYLOAD_SIZE") == 0)
			{
				uint32_t v;
				conf >> v;
				packet_payload_size = v;
				std::cout << "PACKET_PAYLOAD_SIZE\t\t" << packet_payload_size << "\n";
			}
			else if (key.compare("L2_CHUNK_SIZE") == 0)
			{
				uint32_t v;
				conf >> v;
				l2_chunk_size = v;
				std::cout << "L2_CHUNK_SIZE\t\t\t" << l2_chunk_size << "\n";
			}
			else if (key.compare("L2_ACK_INTERVAL") == 0)
			{
				uint32_t v;
				conf >> v;
				l2_ack_interval = v;
				std::cout << "L2_ACK_INTERVAL\t\t\t" << l2_ack_interval << "\n";
			}
			else if (key.compare("L2_BACK_TO_ZERO") == 0)
			{
				uint32_t v;
				conf >> v;
				l2_back_to_zero = v;
				if (l2_back_to_zero)
					std::cout << "L2_BACK_TO_ZERO\t\t\t" << "Yes" << "\n";
				else
					std::cout << "L2_BACK_TO_ZERO\t\t\t" << "No" << "\n";
			}
			else if (key.compare("TOPOLOGY_FILE") == 0)
			{
				std::string v;
				conf >> v;
				topology_file = v;
				std::cout << "TOPOLOGY_FILE\t\t\t" << topology_file << "\n";
			}
			else if (key.compare("FLOW_FILE") == 0)
			{
				std::string v;
				conf >> v;
				flow_file = v;
				std::cout << "FLOW_FILE\t\t\t" << flow_file << "\n";
			}
			else if (key.compare("TRACE_FILE") == 0)
			{
				std::string v;
				conf >> v;
				trace_file = v;
				std::cout << "TRACE_FILE\t\t\t" << trace_file << "\n";
			}
			else if (key.compare("TRACE_OUTPUT_FILE") == 0)
			{
				std::string v;
				conf >> v;
				trace_output_file = v;
				if (argc > 2)
				{
					trace_output_file = trace_output_file + std::string(argv[2]);
				}
				std::cout << "TRACE_OUTPUT_FILE\t\t" << trace_output_file << "\n";
			}else if (key.compare("PKT_OUTPUT_FILE") == 0) 
			{
				/***********
				 *qizhou.zqz add.
				 ***********/
				std::string v;
				conf >> v;
				pkt_output_file = v;
				std::cout << "PKT_OUTPUT_FILE\t\t" << pkt_output_file << "\n";
			}
			else if (key.compare("ROOT_OUTPUT_FILE") == 0) 
			{
				std::string v;
				conf >> v;
				root_output_file = v;
				std::cout << "ROOT_OUTPUT_FILE\t\t" << root_output_file << "\n";
			}else if (key.compare("VICTIM_OUTPUT_FILE") == 0) 
			{
				std::string v;
				conf >> v;
				victim_output_file = v;
				std::cout << "VICTIM_OUTPUT_FILE\t\t" << victim_output_file << "\n";
			}else if (key.compare("TX_BYTES_OUTPUT_FILE") == 0) 
			{
				std::string v;
				conf >> v;
				tx_bytes_ouput_file = v;
				std::cout << "TX_BYTES_OUTPUT_FILE\t\t\t\t" << tx_bytes_ouput_file << "\n";
			}
			else if (key.compare("SIMULATOR_STOP_TIME") == 0)
			{
				double v;
				conf >> v;
				simulator_stop_time = v;
				std::cout << "SIMULATOR_STOP_TIME\t\t" << simulator_stop_time << "\n";
			}
			else if (key.compare("ALPHA_RESUME_INTERVAL") == 0)
			{
				double v;
				conf >> v;
				alpha_resume_interval = v;
				std::cout << "ALPHA_RESUME_INTERVAL\t\t" << alpha_resume_interval << "\n";
			}
			else if (key.compare("RP_TIMER") == 0)
			{
				double v;
				conf >> v;
				rp_timer = v;
				std::cout << "RP_TIMER\t\t\t" << rp_timer << "\n";
			}
			else if (key.compare("EWMA_GAIN") == 0)
			{
				double v;
				conf >> v;
				ewma_gain = v;
				std::cout << "EWMA_GAIN\t\t\t" << ewma_gain << "\n";
			}
			else if (key.compare("FAST_RECOVERY_TIMES") == 0)
			{
				uint32_t v;
				conf >> v;
				fast_recovery_times = v;
				std::cout << "FAST_RECOVERY_TIMES\t\t" << fast_recovery_times << "\n";
			}
			else if (key.compare("RATE_AI") == 0)
			{
				std::string v;
				conf >> v;
				rate_ai = v;
				std::cout << "RATE_AI\t\t\t\t" << rate_ai << "\n";
			}
			else if (key.compare("RATE_HAI") == 0)
			{
				std::string v;
				conf >> v;
				rate_hai = v;
				std::cout << "RATE_HAI\t\t\t" << rate_hai << "\n";
			}
			else if (key.compare("ERROR_RATE_PER_LINK") == 0)
			{
				double v;
				conf >> v;
				error_rate_per_link = v;
				std::cout << "ERROR_RATE_PER_LINK\t\t" << error_rate_per_link << "\n";
			}
			else if (key.compare("CC_MODE") == 0){
				conf >> cc_mode;
				//
				// cc_mode = 3;
				std::cout << "CC_MODE\t\t" << cc_mode << '\n';
			}else if (key.compare("RATE_DECREASE_INTERVAL") == 0){
				double v;
				conf >> v;
				rate_decrease_interval = v;
				std::cout << "RATE_DECREASE_INTERVAL\t\t" << rate_decrease_interval << "\n";
			}else if (key.compare("MIN_RATE") == 0){
				conf >> min_rate;
				std::cout << "MIN_RATE\t\t" << min_rate << "\n";
			}else if (key.compare("FCT_OUTPUT_FILE") == 0){
				conf >> fct_output_file;
				std::cout << "FCT_OUTPUT_FILE\t\t" << fct_output_file << '\n';
			}else if (key.compare("HAS_WIN") == 0){
				conf >> has_win;
				std::cout << "HAS_WIN\t\t" << has_win << "\n";
			}else if (key.compare("GLOBAL_T") == 0){
				conf >> global_t;
				std::cout << "GLOBAL_T\t\t" << global_t << '\n';
			}else if (key.compare("MI_THRESH") == 0){
				conf >> mi_thresh;
				std::cout << "MI_THRESH\t\t" << mi_thresh << '\n';
			}else if (key.compare("VAR_WIN") == 0){
				uint32_t v;
				conf >> v;
				var_win = v;
				std::cout << "VAR_WIN\t\t" << v << '\n';
			}else if (key.compare("FAST_REACT") == 0){
				uint32_t v;
				conf >> v;
				fast_react = v;
				std::cout << "FAST_REACT\t\t" << v << '\n';
			}else if (key.compare("U_TARGET") == 0){
				conf >> u_target;
				std::cout << "U_TARGET\t\t" << u_target << '\n';
			}else if (key.compare("INT_MULTI") == 0){
				conf >> int_multi;
				std::cout << "INT_MULTI\t\t\t\t" << int_multi << '\n';
			}else if (key.compare("RATE_BOUND") == 0){
				uint32_t v;
				conf >> v;
				rate_bound = v;
				std::cout << "RATE_BOUND\t\t" << rate_bound << '\n';
			}else if (key.compare("ACK_HIGH_PRIO") == 0){
				conf >> ack_high_prio;
				std::cout << "ACK_HIGH_PRIO\t\t" << ack_high_prio << '\n';
			}else if (key.compare("DCTCP_RATE_AI") == 0){
				conf >> dctcp_rate_ai;
				std::cout << "DCTCP_RATE_AI\t\t\t\t" << dctcp_rate_ai << "\n";
			}else if (key.compare("PFC_OUTPUT_FILE") == 0){
				conf >> pfc_output_file;
				std::cout << "PFC_OUTPUT_FILE\t\t\t\t" << pfc_output_file << '\n';
			}else if (key.compare("LINK_DOWN") == 0){
				conf >> link_down_time >> link_down_A >> link_down_B;
				std::cout << "LINK_DOWN\t\t\t\t" << link_down_time << ' '<< link_down_A << ' ' << link_down_B << '\n';
			}else if (key.compare("ENABLE_TRACE") == 0){
				conf >> enable_trace;
				std::cout << "ENABLE_TRACE\t\t\t\t" << enable_trace << '\n';
			}else if (key.compare("KMAX_MAP") == 0){
				int n_k ;
				conf >> n_k;
				std::cout << "KMAX_MAP\t\t\t\t";
				for (int i = 0; i < n_k; i++){
					uint64_t rate;
					uint32_t k;
					conf >> rate >> k;
					rate2kmax[rate] = k;
					std::cout << ' ' << rate << ' ' << k;
				}
				std::cout<<'\n';
			}else if (key.compare("KMIN_MAP") == 0){
				int n_k ;
				conf >> n_k;
				std::cout << "KMIN_MAP\t\t\t\t";
				for (int i = 0; i < n_k; i++){
					uint64_t rate;
					uint32_t k;
					conf >> rate >> k;
					rate2kmin[rate] = k;
					std::cout << ' ' << rate << ' ' << k;
				}
				std::cout<<'\n';
			}else if (key.compare("PMAX_MAP") == 0){
				int n_k ;
				conf >> n_k;
				std::cout << "PMAX_MAP\t\t\t\t";
				for (int i = 0; i < n_k; i++){
					uint64_t rate;
					double p;
					conf >> rate >> p;
					rate2pmax[rate] = p;
					std::cout << ' ' << rate << ' ' << p;
				}
				std::cout<<'\n';
			}else if (key.compare("BUFFER_SIZE") == 0){
				conf >> buffer_size;
				std::cout << "BUFFER_SIZE\t\t\t\t" << buffer_size << '\n';
			}else if (key.compare("QLEN_MON_FILE") == 0){
				conf >> qlen_mon_file;
				std::cout << "QLEN_MON_FILE\t\t\t\t" << qlen_mon_file << '\n';
			}else if (key.compare("QLEN_MON_START") == 0){
				conf >> qlen_mon_start;
				std::cout << "QLEN_MON_START\t\t\t\t" << qlen_mon_start << '\n';
			}else if (key.compare("QLEN_MON_END") == 0){
				conf >> qlen_mon_end;
				std::cout << "QLEN_MON_END\t\t\t\t" << qlen_mon_end << '\n';
			}else if (key.compare("MULTI_RATE") == 0){
				int v;
				conf >> v;
				multi_rate = v;
				std::cout << "MULTI_RATE\t\t\t\t" << multi_rate << '\n';
			}else if (key.compare("SAMPLE_FEEDBACK") == 0){
				int v;
				conf >> v;
				sample_feedback = v;
				std::cout << "SAMPLE_FEEDBACK\t\t\t\t" << sample_feedback << '\n';
			}else if(key.compare("PINT_LOG_BASE") == 0){
				conf >> pint_log_base;
				std::cout << "PINT_LOG_BASE\t\t\t\t" << pint_log_base << '\n';
			}else if (key.compare("PINT_PROB") == 0){
				conf >> pint_prob;
				std::cout << "PINT_PROB\t\t\t\t" << pint_prob << '\n';
			}
			fflush(stdout);
		}
		conf.close();
	}
	else
	{
		std::cout << "Error: require a config file\n";
		fflush(stdout);
		return -1;
	}

	return 0;

}

/****************
 * SEGSEV HANDLER
 ****************/

#define BACKTRACE_SIZE   16

void dump(void)
{
	int j, nptrs;
	void *buffer[BACKTRACE_SIZE];
	char **strings;

	nptrs = backtrace(buffer, BACKTRACE_SIZE);

	printf("backtrace() returned %d addresses\n", nptrs);

	strings = backtrace_symbols(buffer, nptrs);
	if (strings == NULL) {
			perror("backtrace_symbols");
			exit(EXIT_FAILURE);
	}

	for (j = 0; j < nptrs; j++)
			printf("  [%02d] %s\n", j, strings[j]);

	free(strings);
}

void signal_handler(int signo)
{
	printf("\n=========>>>catch signal %d <<<=========\n", signo);

	printf("Dump stack start...\n");
	dump();
	printf("Dump stack end...\n");

	signal(signo, SIG_DFL); //对该信号进行默认处理 
	raise(signo);           // 向自身发信号 
}

int main(int argc, char *argv[])
{
	signal(SIGSEGV, signal_handler);  //为SIGSEGV信号安装新的处理函数 

	// LogComponentEnable("GENERIC_SIMULATION", LOG_LEVEL_ALL);
	clock_t begint, endt;
	begint = clock();

	// read configuration file
	if(read_conf(argc, argv) < 0) {
		std::cout << "Error occurred in reading configuration file.\n";
	}

	bool dynamicth = use_dynamic_pfc_threshold;

	Config::SetDefault("ns3::QbbNetDevice::PauseTime", UintegerValue(pause_time));
	Config::SetDefault("ns3::QbbNetDevice::QcnEnabled", BooleanValue(enable_qcn));
	Config::SetDefault("ns3::QbbNetDevice::DynamicThreshold", BooleanValue(dynamicth));
	Config::SetDefault("ns3::QbbNetDevice::QbbEnabled", BooleanValue(enable_pfc));
	Config::SetDefault("ns3::QbbNetDevice::EnableSack", BooleanValue(enable_sack));

	// set int_multi
	IntHop::multi = int_multi;
	// IntHeader::mode
	if (cc_mode == 7) // timely, use ts
		IntHeader::mode = IntHeader::TS;
	else if (cc_mode == 3) // hpcc, use int
		IntHeader::mode = IntHeader::NORMAL;
	else if (cc_mode == 10) // hpcc-pint
		IntHeader::mode = IntHeader::PINT;
	else // others, no extra header
		IntHeader::mode = IntHeader::NONE;

	// Set Pint
	if (cc_mode == 10){
		Pint::set_log_base(pint_log_base);
		IntHeader::pint_bytes = Pint::get_n_bytes();
		printf("PINT bits: %d bytes: %d\n", Pint::get_n_bits(), Pint::get_n_bytes());
	}

	//SeedManager::SetSeed(time(NULL));

	topof.open(topology_file.c_str());
	flowf.open(flow_file.c_str());
	tracef.open(trace_file.c_str());
	uint32_t node_num, switch_num, link_num, trace_num;
	uint32_t ports_every_switch;
	topof >> node_num >> switch_num >> link_num >> ports_every_switch;
	flowf >> flow_num;
	tracef >> trace_num;
	printf("Flows: %d Links: %d Switches: %d Trace nodes: %d ports every switch=%d\n", flow_num, link_num, switch_num, trace_num, ports_every_switch);
	
	//n.Create(node_num);

	std::vector<uint32_t> node_type(node_num, 0);
	for (uint32_t i = 0; i < switch_num; i++)
	{
		uint32_t sid;
		topof >> sid;
		node_type[sid] = 1;
	}
	for (uint32_t i = 0; i < node_num; i++){
		if (node_type[i] == 0)
			n.Add(CreateObject<Node>());
		else{
			Ptr<SwitchNode> sw = CreateObject<SwitchNode>();
			n.Add(sw);
			sw->SetAttribute("EcnEnabled", BooleanValue(enable_qcn));
			sw->SetAttribute("EnablePfc", BooleanValue(enable_pfc));
		}
		// std::cout << "create node\n";
	}


	NS_LOG_INFO("Create nodes.");


	// In this function it will create netdevice
	InternetStackHelper internet;
	internet.Install(n);
	
	//
	// Assign IP to each server
	//
	for (uint32_t i = 0; i < node_num; i++){
		if (n.Get(i)->GetNodeType() == 0){ // is server
			serverAddress.resize(i + 1);
			serverAddress[i] = node_id_to_ip(i);
		}
	}
	std::cout << "assgin ip\n";

	NS_LOG_INFO("Create channels.");

	//
	// Explicitly create the channels required by the topology.
	//

	Ptr<RateErrorModel> rem = CreateObject<RateErrorModel>();
	Ptr<UniformRandomVariable> uv = CreateObject<UniformRandomVariable>();
	rem->SetRandomVariable(uv);
	uv->SetStream(50);
	rem->SetAttribute("ErrorRate", DoubleValue(error_rate_per_link));
	rem->SetAttribute("ErrorUnit", StringValue("ERROR_UNIT_PACKET"));

	FILE *pfc_file = fopen(pfc_output_file.c_str(), "w");

	// std::cout << "what call\n";
  // create net device
  for (uint32_t i = 0; i < node_num; i++) {
    if (n.Get(i)->GetNodeType() == 1) { // switch
      Ptr<Node> node = n.Get(i);
      for (uint32_t j = 0; j < ports_every_switch; j++) {
        Ptr<QbbNetDevice> dev =  CreateObject<QbbNetDevice> ();
        dev->SetAddress (Mac48Address::Allocate ());
				node->AddDevice (dev);
      }
    }
  }

	int cc = 0;
	for (uint32_t i = 0; i < node_num; i++) {
		Ptr<Node> node = n.Get(i);
		if (node->GetNodeType() == 0) { // host
			Ptr<QbbNetDevice> dev =  CreateObject<QbbNetDevice> ();
			dev->SetAddress (Mac48Address::Allocate ());
			node->AddDevice (dev);
			cc++;
			// std::cout << " i = " << i << " NDevs = " << node->GetNDevices() << "\n";
		}
	}

	QbbHelper qbb;
	Ipv4AddressHelper ipv4; // qbb-helper call AddDevice(), AddDevice() call SetIfIndex()
	std::set<uint64_t> rates;
	for (uint32_t i = 0; i < link_num; i++)
	{
		uint32_t src, dst;
		uint32_t port1, port2;
		std::string data_rate, link_delay;
		double error_rate;
		topof >> src >> dst >> data_rate >> link_delay >> error_rate >> port1 >> port2;
		Ptr<Node> snode = n.Get(src), dnode = n.Get(dst);

		uint64_t rateInGbps = std::atof(data_rate.c_str()) * 1e9;
		if (!rates.count(rateInGbps)) {
			rates.insert(rateInGbps);
		}
		qbb.SetDeviceAttribute("DataRate", StringValue(data_rate));
		qbb.SetChannelAttribute("Delay", StringValue(link_delay));
		
		// link error rate
		if (error_rate > 0)
		{
			Ptr<RateErrorModel> rem = CreateObject<RateErrorModel>();
			Ptr<UniformRandomVariable> uv = CreateObject<UniformRandomVariable>();
			rem->SetRandomVariable(uv);
			uv->SetStream(50);
			rem->SetAttribute("ErrorRate", DoubleValue(error_rate));
			rem->SetAttribute("ErrorUnit", StringValue("ERROR_UNIT_PACKET"));
			qbb.SetDeviceAttribute("ReceiveErrorModel", PointerValue(rem));
		}
		else
		{
			qbb.SetDeviceAttribute("ReceiveErrorModel", PointerValue(rem));
		}

		fflush(stdout);

		// Assigne server IP
		// Note: this should be before the automatic assignment below (ipv4.Assign(d)),
		// because we want our IP to be the primary IP (first in the IP address list),
		// so that the global routing is based on our IP
		// std::cout << i << " instll rrg\n";
		NetDeviceContainer d = qbb.InstallRRG(snode, dnode, port1 + 1, port2 + 1);
		if (snode->GetNodeType() == 0){ // The node type of switch is 1.
			Ptr<Ipv4> ipv4 = snode->GetObject<Ipv4>();
			ipv4->AddInterface(d.Get(0));
			ipv4->AddAddress(1, Ipv4InterfaceAddress(serverAddress[src], Ipv4Mask(0xff000000)));
		}
		if (dnode->GetNodeType() == 0){
			Ptr<Ipv4> ipv4 = dnode->GetObject<Ipv4>();
			ipv4->AddInterface(d.Get(1));
			ipv4->AddAddress(1, Ipv4InterfaceAddress(serverAddress[dst], Ipv4Mask(0xff000000)));
		}

		// used to create a graph of the topology
		nbr2if[snode][dnode].idx = DynamicCast<QbbNetDevice>(d.Get(0))->GetIfIndex();
		nbr2if[snode][dnode].up = true;
		nbr2if[snode][dnode].delay = DynamicCast<QbbChannel>(DynamicCast<QbbNetDevice>(d.Get(0))->GetChannel())->GetDelay().GetTimeStep();
		nbr2if[snode][dnode].bw = DynamicCast<QbbNetDevice>(d.Get(0))->GetDataRate().GetBitRate();
		nbr2if[dnode][snode].idx = DynamicCast<QbbNetDevice>(d.Get(1))->GetIfIndex();
		nbr2if[dnode][snode].up = true;
		nbr2if[dnode][snode].delay = DynamicCast<QbbChannel>(DynamicCast<QbbNetDevice>(d.Get(1))->GetChannel())->GetDelay().GetTimeStep();
		nbr2if[dnode][snode].bw = DynamicCast<QbbNetDevice>(d.Get(1))->GetDataRate().GetBitRate();

		// This is just to set up the connectivity between nodes. The IP addresses are useless
		char ipstring[16];
		sprintf(ipstring, "10.%d.%d.0", i / 254 + 1, i % 254 + 1);
		ipv4.SetBase(ipstring, "255.255.255.0");
		ipv4.Assign(d);

		// setup PFC trace
		// DynamicCast<QbbNetDevice>(d.Get(0))->TraceConnectWithoutContext("QbbPfc", MakeBoundCallback (&get_pfc, pfc_file, DynamicCast<QbbNetDevice>(d.Get(0))));
		// DynamicCast<QbbNetDevice>(d.Get(1))->TraceConnectWithoutContext("QbbPfc", MakeBoundCallback (&get_pfc, pfc_file, DynamicCast<QbbNetDevice>(d.Get(1))));
	}
	std::cout << "SET HPCC LINE RATES\n";
	SetHpccLineRates(rates);

	nic_rate = get_nic_rate(n);
	FILE* root_file = fopen(root_output_file.c_str(), "w");
	FILE* victim_file = fopen(victim_output_file.c_str(), "w");
	// config switch
	bool rate40G = false;
	for (uint32_t i = 0; i < node_num; i++){
		if (n.Get(i)->GetNodeType() == 1){ // is switch
			Ptr<SwitchNode> sw = DynamicCast<SwitchNode>(n.Get(i));
			uint32_t shift = 3; // by default 1/8
			for (uint32_t j = 1; j < sw->GetNDevices(); j++){
				Ptr<QbbNetDevice> dev = DynamicCast<QbbNetDevice>(sw->GetDevice(j));
				// set ecn
				uint64_t rate = dev->GetDataRate().GetBitRate();
				if (rate == 40000000000 && !rate40G) {
					rate40G = true;
				}
				double kmin = 0;
				double kmax = 0;
				double pmax = 0;
				if (cc_mode == 1) { // DCQCN, as recommended in DCQCN paper
					kmin = static_cast<double>(rate) / 40000000000 * 5;
					kmax = static_cast<double>(rate) / 40000000000 * 200;
					pmax = 0.01;
				} else if (cc_mode == 3) { // HPCC
					kmin = static_cast<double>(rate) / 25000000000 * 100;
					kmax = static_cast<double>(rate) / 25000000000 * 400;
					pmax = 0.2;
				} else if (cc_mode == 8) { // DCTCP
					kmax = kmin = static_cast<double>(rate) / 10000000000 * 30;
					pmax = 1;
				}
				sw->m_mmu->ConfigEcn(j, kmin, kmax, pmax/*rate2kmin[rate], rate2kmax[rate], rate2pmax[rate]*/);
				// set pfc
				uint64_t delay = DynamicCast<QbbChannel>(dev->GetChannel())->GetDelay().GetTimeStep();
				uint32_t headroom = rate * delay / 8 / 1000000000 * 3 + 1024 * 5;
				sw->m_mmu->ConfigHdrm(j, headroom);
				
				// set pfc alpha, proportional to link bw
				sw->m_mmu->pfc_a_shift[j] = shift;
				while (rate > nic_rate && sw->m_mmu->pfc_a_shift[j] > 0){
					sw->m_mmu->pfc_a_shift[j]--;
					rate /= 2;
				}
			}
			sw->m_mmu->ConfigNPort(sw->GetNDevices()-1);
			sw->m_mmu->ConfigBufferSize(buffer_size* 1024 * 1024);
			sw->m_mmu->node_id = sw->GetId();
			// config pfc threshold
			if (rate40G) {
				// std::cout << "kmin = " << kmin << " kmax=" << kmax << " pmax=" << pmax << "\n"; 
				sw->m_mmu->SetFixedPfcThreshold(512 * 1024);
				// std::cout << "config rate40G: " << i << "\n"; 
			} else {
				sw->m_mmu->SetFixedPfcThreshold(20 * 1024);
				// std::cout << "config rate1G: " << i << "\n"; 
			}
			sw->TraceConnectWithoutContext("GetRoot", MakeBoundCallback(&get_root, root_file));
			sw->TraceConnectWithoutContext("GetVictim", MakeBoundCallback(&get_victim, root_file));
			sw->TraceConnectWithoutContext("GetPause", MakeBoundCallback(&get_pause, pfc_file));
			sw->TraceConnectWithoutContext("GetResume", MakeBoundCallback(&get_resume, pfc_file));
			sw->SetWeightedHash(enable_weighted_hash);
			sw->SetUniformHash(enable_uniform_hash);
			sw->SetLp(enable_lp);
		}
	}

	#if ENABLE_QP
	FILE *fct_output = fopen(fct_output_file.c_str(), "w");
	FILE *pkt_output = fopen(pkt_output_file.c_str(), "w");
	//
	// install RDMA driver
	//
	for (uint32_t i = 0; i < node_num; i++){
		if (n.Get(i)->GetNodeType() == 0){ // is server
			// create RdmaHw
			Ptr<RdmaHw> rdmaHw = CreateObject<RdmaHw>();
			rdmaHw->SetAttribute("ClampTargetRate", BooleanValue(clamp_target_rate));
			rdmaHw->SetAttribute("AlphaResumInterval", DoubleValue(alpha_resume_interval));
			rdmaHw->SetAttribute("RPTimer", DoubleValue(rp_timer));
			rdmaHw->SetAttribute("FastRecoveryTimes", UintegerValue(fast_recovery_times));
			rdmaHw->SetAttribute("EwmaGain", DoubleValue(ewma_gain));
			rdmaHw->SetAttribute("RateAI", DataRateValue(DataRate(rate_ai)));
			rdmaHw->SetAttribute("RateHAI", DataRateValue(DataRate(rate_hai)));
			rdmaHw->SetAttribute("L2BackToZero", BooleanValue(l2_back_to_zero));
			rdmaHw->SetAttribute("L2ChunkSize", UintegerValue(l2_chunk_size));
			rdmaHw->SetAttribute("L2AckInterval", UintegerValue(l2_ack_interval));
			rdmaHw->SetAttribute("CcMode", UintegerValue(cc_mode));
			rdmaHw->SetAttribute("RateDecreaseInterval", DoubleValue(rate_decrease_interval));
			rdmaHw->SetAttribute("MinRate", DataRateValue(DataRate(min_rate)));
			rdmaHw->SetAttribute("Mtu", UintegerValue(packet_payload_size));
			rdmaHw->SetAttribute("MiThresh", UintegerValue(mi_thresh));
			rdmaHw->SetAttribute("VarWin", BooleanValue(var_win));
			rdmaHw->SetAttribute("FastReact", BooleanValue(fast_react));
			rdmaHw->SetAttribute("MultiRate", BooleanValue(multi_rate));
			rdmaHw->SetAttribute("SampleFeedback", BooleanValue(sample_feedback));
			rdmaHw->SetAttribute("TargetUtil", DoubleValue(u_target));
			rdmaHw->SetAttribute("RateBound", BooleanValue(rate_bound));
			rdmaHw->SetAttribute("DctcpRateAI", DataRateValue(DataRate(dctcp_rate_ai)));
			rdmaHw->SetAttribute("EnableSack", BooleanValue(enable_sack));
			rdmaHw->SetPintSmplThresh(pint_prob);
			// create and install RdmaDriver
			Ptr<RdmaDriver> rdma = CreateObject<RdmaDriver>();
			Ptr<Node> node = n.Get(i);
			rdma->SetNode(node);
			rdma->SetRdmaHw(rdmaHw);

			node->AggregateObject (rdma);
			rdma->Init();
			rdma->TraceConnectWithoutContext("QpComplete", MakeBoundCallback (qp_finish, fct_output));
			rdma->TraceConnectWithoutContext("PktComplete", MakeBoundCallback (pkt_finish, pkt_output));
		}
	}
	#endif

	// set ACK priority on hosts
	if (ack_high_prio)
		RdmaEgressQueue::ack_q_idx = 0;
	else
		RdmaEgressQueue::ack_q_idx = 3;

  // Install K-shortest Path
	clock_t st, ed;
	st = clock();
	CalculateRoutes(n);
	SetRoutingEntries();
	ed = clock();
	std::cout << "Bfs for routing calculate: " << (ed - st) / CLOCKS_PER_SEC << "s" << "\n";
	//
	// get BDP and delay
	//
	maxRtt = maxBdp = 0;
	for (uint32_t i = 0; i < node_num; i++){
		if (n.Get(i)->GetNodeType() != 0)
			continue;
		for (uint32_t j = 0; j < node_num; j++){
			if (n.Get(j)->GetNodeType() != 0)
				continue;
			uint64_t delay = pairDelay[n.Get(i)][n.Get(j)];
			uint64_t txDelay = pairTxDelay[n.Get(i)][n.Get(j)];
			uint64_t rtt = delay * 2 + txDelay;
			uint64_t bw = pairBw[i][j];
			uint64_t bdp = rtt * bw / 1000000000/8; 
			pairBdp[n.Get(i)][n.Get(j)] = bdp;
			pairRtt[i][j] = rtt;
			if (bdp > maxBdp)
				maxBdp = bdp;
			if (rtt > maxRtt)
				maxRtt = rtt;
		}
	}
	printf("maxRtt=%lu maxBdp=%lu\n", maxRtt, maxBdp);

	//
	// setup switch CC
	//
	for (uint32_t i = 0; i < node_num; i++){
		if (n.Get(i)->GetNodeType() == 1){ // switch
			Ptr<SwitchNode> sw = DynamicCast<SwitchNode>(n.Get(i));
			sw->SetAttribute("CcMode", UintegerValue(cc_mode));
			sw->SetAttribute("MaxRtt", UintegerValue(maxRtt));
		}
	}
	// std::cout << "setup CC over\n";

	//
	// add trace
	//

	NodeContainer trace_nodes;
	for (uint32_t i = 0; i < trace_num; i++)
	{
		uint32_t nid;
		tracef >> nid;
		if (nid >= n.GetN()){
			continue;
		}
		trace_nodes = NodeContainer(trace_nodes, n.Get(nid));
	}
	std::cout << "setup trace\n";

	FILE *trace_output = fopen(trace_output_file.c_str(), "w");
	if (enable_trace)
		qbb.EnableTracing(trace_output, trace_nodes);

	// dump link speed to trace file
	// {
	// 	SimSetting sim_setting;
	// 	for (auto i: nbr2if){
	// 		for (auto j : i.second){
	// 			uint16_t node = i.first->GetId();
	// 			uint8_t intf = j.second.idx;
	// 			uint64_t bps = DynamicCast<QbbNetDevice>(i.first->GetDevice(j.second.idx))->GetDataRate().GetBitRate();
	// 			sim_setting.port_speed[node][intf] = bps;
	// 		}
	// 	}
	// 	sim_setting.win = maxBdp;
	// 	// sim_setting.Serialize(trace_output);
	// }

	std::cout << "dump link\n";
	clock_t c1, c2;
	c1 = clock();
	// Ipv4GlobalRoutingHelper::PopulateRoutingTables();
	c2 = clock();
	std::cout << "PopulateRoutingTables: " << (c2 - c1) / CLOCKS_PER_SEC << "s\n";

	NS_LOG_INFO("Create Applications.");

	Time interPacketInterval = Seconds(0.0000005 / 2);

	// maintain port number for each host
	for (uint32_t i = 0; i < node_num; i++){
		if (n.Get(i)->GetNodeType() == 0)
			for (uint32_t j = 0; j < node_num; j++){
				if (n.Get(j)->GetNodeType() == 0)
					portNumder[i][j] = 10000; // each host pair use port number from 10000
			}
	}

	//
	std::cout << "Read Flow...\n";
	flow_input.idx = 0;
	if (flow_num > 0){
		ReadFlowInput();
		Simulator::Schedule(Seconds(flow_input.start_time)-Simulator::Now(), ScheduleFlowInputs);
	}

	topof.close();
	tracef.close();

	// schedule link down
	if (link_down_time > 0){
		Simulator::Schedule(Seconds(2) + MicroSeconds(link_down_time), &TakeDownLink, n, n.Get(link_down_A), n.Get(link_down_B));
	}

	// schedule buffer monitor
	FILE* qlen_output = fopen(qlen_mon_file.c_str(), "w");
	Simulator::Schedule(NanoSeconds(qlen_mon_start), &monitor_buffer, qlen_output, &n);

	FILE* tx_bytes = fopen(tx_bytes_ouput_file.c_str(), "w");
	
	std::cout << "Setting MultiPaths\n";
	// SetMultiPathForAllHosts();
	
	if (enable_lp) {
		std::cout << "Set Wcmp Weight\n";
		ReadPath(path_file); // add by zsz
		SetWcmpWeightForAllHosts();
	}

	//
	// Now, do the actual simulation.
	//
	std::cout << "Running Simulation.\n";
	fflush(stdout);
	NS_LOG_INFO("Run Simulation.");
	Simulator::Stop(Seconds(simulator_stop_time));
	Simulator::Run();
	std::cout << "Run simu-time=" << Simulator::Now().GetTimeStep() << "\n";
	
	// Get Port Tx Bytes Status
	// Simulator::Destroy() will destroy switch object
    GetPortTxBytes(tx_bytes, n);

	Simulator::Destroy();
	NS_LOG_INFO("Done.");
	fclose(trace_output);
	fclose(tx_bytes);
	endt = clock();
	std::cout << (double)(endt - begint) / CLOCKS_PER_SEC << "\n";
}
