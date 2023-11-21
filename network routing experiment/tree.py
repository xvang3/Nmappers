# Template aken from University of New South Wales WebCMS3
# Adapted to fit needs of project
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, Host
from mininet.topolib import TreeTopo
from mininet.cli import CLI
from mininet.log import setLogLevel
import os

# Configuration Variables
DEPTH = 2
FANOUT = 3
LOG_DIR = "/home/dlnash/mininet/mininet/logs"
SERVER_LOG = os.path.join(LOG_DIR, 'servers.log')
CLIENT_LOG = os.path.join(LOG_DIR, 'clients.log')

def start_iperf_server(host):
    host.cmd('iperf -s -u &>> {} &'.format(SERVER_LOG))

def start_iperf_client(client, server_ip, duration=15, bandwidth='10M'):
    client.cmd('iperf -c {} -u -t {} -b {} &>> {} &'.format(server_ip, duration, bandwidth, CLIENT_LOG))

def setup_network():
    # Create log directory
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Create a tree topology
    topo = TreeTopo(depth=DEPTH, fanout=FANOUT)

    # Create the network from the topology
    net = Mininet(topo=topo, controller=RemoteController, switch=OVSKernelSwitch, host=Host)
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    net.start()

    # Start iPerf on hosts: we will assume the last FANOUT hosts are servers
    servers = []
    clients = []
    for host in net.hosts[-FANOUT:]:
        servers.append(host)
        start_iperf_server(host)

    # Start iPerf clients on the first FANOUT hosts
    for i, host in enumerate(net.hosts[:FANOUT]):
        server_ip = servers[i].IP()
        start_iperf_client(host, server_ip)

    return net


def main():
    setLogLevel('info')
    net = setup_network()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()




