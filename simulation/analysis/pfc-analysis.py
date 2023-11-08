from signal import pause
from sys import path


class Pfc:
    def __init__(self, type, timestamp, switch_id, port_id, queue_id):
        self.type = type
        self.timestamp = timestamp
        self.switch_id = switch_id
        self.port_id = port_id
        self.queue_id = queue_id
    
    def __str__(self):
        return "type: {}, timestamp: {}, switch_id: {}, port_id, queue_id:{}".format(
            self.type,
            self.timestamp,
            self.switch_id,
            self.port_id,
            self.queue_id
        )

class Exp:
    def __init__(self, flows, completed_flows, pfcs, pauses, resumes, is_deadlock):
        self.flows = flows
        self.completed_flows = completed_flows
        # pfcs is a list of Pfc objects 
        self.pfcs = pfcs
        self.pauses = pauses
        self.resumes = resumes
        self.is_deadlock = is_deadlock

if __name__ == "__main__":
    pfcs_thresholds = [5 * i for i in range(0, 11)]
    hosts = [host for host in range(1, 13)]
    path_to_flow_file_fmt = "../mix/failure-exps/d2-deadlock/traffic/%d/flow.txt"
    path_to_pfc_file_fmt = "../mix/failure-exps/d2-deadlock/output/12/%d/%d/pfc.txt"
    path_to_fct_file_fmt = "../mix/failure-exps/d2-deadlock/output/12/%d/%d/fct.txt"
    
    deadlock_recorder = {}
    for pfc_th in pfcs_thresholds:
        deadlock_recorder[pfc_th] = {}
        for host in hosts:
            deadlock_recorder[pfc_th][host] = None
            flow_f = open(path_to_flow_file_fmt % (host), mode='r')
            pfc_f = open(path_to_pfc_file_fmt % (pfc_th, host), mode='r')
            fct_f = open(path_to_fct_file_fmt % (pfc_th, host) , mode='r')

            
            flows = int(flow_f.read().splitlines()[0])
            completed_flows = len(fct_f.read().splitlines())
            pfcs = []
            pauses = 0
            resumes = 0
            is_deadlock = False
            for line in pfc_f.read().splitlines():
                data = line.split(' ')
                if data[0] == 'PAUSE': pauses+= 1
                elif data[0] == "RESUME": resumes += 1

                pfcs.append(
                    Pfc(
                        type=data[0],
                        timestamp=int(data[1]),
                        switch_id=int(data[2]),
                        port_id=int(data[3]),
                        queue_id=int(data[4])
                ))
            is_deadlock = (flows > completed_flows) and (pauses - resumes) > 5
            # print("th:{} h: {}".format(pfc_th, host), flows, completed_flows, pauses, resumes, is_deadlock)
            deadlock_recorder[pfc_th][host] = Exp(flows, completed_flows, pfcs, pauses, resumes, is_deadlock)
    for pfc_th in pfcs_thresholds:
        print("\hline")
        print(pfc_th, end=' & ')
        for host in hosts:
            if deadlock_recorder[pfc_th][host].is_deadlock is True:
                print("\CheckmarkBold", end='')
            else:
                print("\XSolidBrush", end='')
            if host < len(hosts):
                print(" & ", end='')
            else:
                print(' ', end='')
        print('\\\\')
    print('\hline')
