#include "rdma-driver.h"

namespace ns3 {

/***********************
 * RdmaDriver
 **********************/
TypeId RdmaDriver::GetTypeId (void)
{
	static TypeId tid = TypeId ("ns3::RdmaDriver")
		.SetParent<Object> ()
		.AddTraceSource ("QpComplete", "A qp completes.",
				MakeTraceSourceAccessor (&RdmaDriver::m_traceQpComplete))
		.AddTraceSource ("PktComplete", "A packet completes.", 
				MakeTraceSourceAccessor (&RdmaDriver::m_tracePktComplete))
		;
	return tid;
}

RdmaDriver::RdmaDriver(){
}

void RdmaDriver::Init(void){
	Ptr<Ipv4> ipv4 = m_node->GetObject<Ipv4> ();
	#if 0
	m_rdma->m_nic.resize(ipv4->GetNInterfaces());
	for (uint32_t i = 0; i < m_rdma->m_nic.size(); i++){
		m_rdma->m_nic[i] = CreateObject<RdmaQueuePairGroup>();
		// share the queue pair group with NIC
		if (ipv4->GetNetDevice(i)->IsQbb()){
			DynamicCast<QbbNetDevice>(ipv4->GetNetDevice(i))->m_rdmaEQ->m_qpGrp = m_rdma->m_nic[i];
		}
	}
	#endif
	for (uint32_t i = 0; i < m_node->GetNDevices(); i++){
		Ptr<QbbNetDevice> dev = NULL;
		if (m_node->GetDevice(i)->IsQbb())
			dev = DynamicCast<QbbNetDevice>(m_node->GetDevice(i));
		m_rdma->m_nic.push_back(RdmaInterfaceMgr(dev));
		m_rdma->m_nic.back().qpGrp = CreateObject<RdmaQueuePairGroup>();
	}
	#if 0
	for (uint32_t i = 0; i < ipv4->GetNInterfaces (); i++){
		if (ipv4->GetNetDevice(i)->IsQbb() && ipv4->IsUp(i)){
			Ptr<QbbNetDevice> dev = DynamicCast<QbbNetDevice>(ipv4->GetNetDevice(i));
			// add a new RdmaInterfaceMgr for this device
			m_rdma->m_nic.push_back(RdmaInterfaceMgr(dev));
			m_rdma->m_nic.back().qpGrp = CreateObject<RdmaQueuePairGroup>();
		}
	}
	#endif
	// RdmaHw do setup
	m_rdma->SetNode(m_node);
	m_rdma->Setup(MakeCallback(&RdmaDriver::QpComplete, this), MakeCallback(&RdmaDriver::PktComplete, this));
}

void RdmaDriver::SetNode(Ptr<Node> node){
	m_node = node;
}

void RdmaDriver::SetRdmaHw(Ptr<RdmaHw> rdma){
	m_rdma = rdma;
}

void RdmaDriver::AddQueuePair(
	uint64_t size, 
	uint16_t pg, 
	Ipv4Address sip, 
	Ipv4Address dip, 
	uint16_t sport, 
	uint16_t dport, 
	uint32_t win, 
	uint64_t baseRtt, 
	Callback<void> notifyAppFinish, 
	uint32_t non_shortest, 
	bool _enable_sack, 
	bool _enable_irn,
	bool _enable_pfc){
	m_rdma->AddQueuePair(size, pg, sip, dip, sport, dport, win, baseRtt, notifyAppFinish, non_shortest, _enable_sack, _enable_irn, _enable_pfc);
}

void RdmaDriver::QpComplete(Ptr<RdmaQueuePair> q){
	m_traceQpComplete(q);
}

void RdmaDriver::PktComplete(Ptr<Packet> p) {
	m_tracePktComplete(p);
}

} // namespace ns3
