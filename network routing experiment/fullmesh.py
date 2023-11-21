from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel
import os

# Configuration Variables
NUM_HOSTS = 10
LOG_DIR = "/home/dlnash/mininet/mininet/logs"
SERVER_LOG = os.path.join(LOG_DIR, 'servers.log')
CLIENT_LOG = os.path.join(LOG_DIR, 'clients.log')

def start_iperf_server(host):
    # Include the '-u' flag to start the server in UDP mode
    host.cmd('iperf -s -u &>> {} &'.format(SERVER_LOG))

def start_iperf_client(client, server_ip, duration=15, bandwidth='10M'):
    # Include the '-u' flag to start the client in UDP mode
    # The '-b' option is used to set the bandwidth for UDP client
    client.cmd('iperf -c {} -u -t {} -b {} &>> {} &'.format(server_ip, duration, bandwidth, CLIENT_LOG))

def setup_network():
    # Create log directory
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    net = Mininet(controller=None, switch=OVSKernelSwitch, host=Host)
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Adding two switches for full mesh topology
    switches = [net.addSwitch('s{}'.format(i+1), protocols='OpenFlow13') for i in range(2)]

    # Creating hosts and adding links to create a full mesh topology
    hosts = [net.addHost('h{}'.format(i+1)) for i in range(NUM_HOSTS)]
    for i in range(NUM_HOSTS):
        for switch in switches:
            net.addLink(hosts[i], switch)

    net.start()

    # Start iPerf on the last 5 hosts as servers and the first 5 hosts as clients
    for i in range(5, NUM_HOSTS):
        start_iperf_server(hosts[i])
    for i in range(5):
        server_ip = '10.0.0.{}'.format(i+6)  # IP Addresses may need to be assigned if not automatically done
        start_iperf_client(hosts[i], server_ip)

    return net

def main():
    setLogLevel('info')
    net = setup_network()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
