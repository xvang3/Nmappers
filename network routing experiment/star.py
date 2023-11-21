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
        os.makedirs(LOG_DIR)  # Corrected indentation: spaces are used here

    net = Mininet(controller=None, switch=OVSKernelSwitch, host=Host)
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    switch = net.addSwitch('s1', protocols='OpenFlow13')  # This line should be indented to match the block

    hosts = []
    for i in range(NUM_HOSTS):
        host = net.addHost('h' + str(i+1))  # Corrected indentation: spaces are used here
        net.addLink(host, switch)  # Corrected indentation: spaces are used here
        hosts.append(host)  # Corrected indentation: spaces are used here

    net.start()

    # Start iPerf on hosts
    for i in range(5, 10):
        start_iperf_server(hosts[i])  # Corrected indentation: spaces are used here
    for i in range(5):
        server_ip = '10.0.0.' + str(6 + (i % 5))
        start_iperf_client(hosts[i], server_ip)  # Corrected indentation: spaces are used here

    return net

def main():
    setLogLevel('info')
    net = setup_network()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()









