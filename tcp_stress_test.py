from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
import random
import time

def get_timestamp():
    return time.strftime("%Y%m%d-%H%M%S")

# Configuration Variables
NUM_SWITCHES = 4
NUM_HOSTS = 10
TRAFFIC_INTENSITY ='10M'

def setup_network():
    net = Mininet(controller=None, switch=OVSKernelSwitch, host=Host)

    # Add Ryu Controller
    # Note: Ryu must be already running in a terminal
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Add Switches
    switches = []
    for i in range(NUM_SWITCHES):
        switches.append(net.addSwitch('s' + str(i+1)))

    # Link Switches
    for i in range(NUM_SWITCHES-1):
        net.addLink(switches[i], switches[i+1])

    # Add Hosts
    hosts = []
    for i in range(NUM_HOSTS):
        hosts.append(net.addHost('h' + str(i+1)))

# Link Hosts to Switches
    for i in range(NUM_HOSTS):
        net.addLink(hosts[i], switches[i%NUM_SWITCHES])

    # Set first half of hosts as servers and the other half as clients
    servers = hosts[:NUM_HOSTS//2]
    clients = hosts[NUM_HOSTS//2:]

    # Start the network
    net.start()

    return net, switches, servers, clients

# Select random server
def random_server(servers):
    return servers[random.randint(0, len(servers)-1)]

def start_servers(clients, servers, tcp_filename):
    first_client = clients[0]
    for server in servers:
        server.cmd(f'iperf -s -t 30 -b {TRAFFIC_INTENSITY} >> {tcp_filename} 2>&1 &')
        latency = measure_latency(first_client, server)
        print("Latency for TCP (Server " + server.name + "): " + latency)

def start_clients(clients, servers, tcp_filename):
    for client in clients:
        selected_server = random_server(servers)
        client.cmd('iperf -c ' + selected_server.IP() + ' -b ' + TRAFFIC_INTENSITY + ' >> {tcp_filename} 2>&1 &')
        latency = measure_latency(client, selected_server)
        print("Latency for TCP (Client " + client.name + " to Server " + selected_server.name + "): " + latency)

def stop_hosts(hosts):
    for host in hosts:
        host.cmd('kill %iperf')

def measure_latency(client, server):
    return client.cmd('ping -c 1 ' + server.IP())

def main():
    timestamp = get_timestamp()

    tcp_filename = f'iPerf_tcp_stress_test_results_{timestamp}.txt'

    setLogLevel('info')

    # Setup the network
    net, switches, clients, servers = setup_network()

    base_latency = measure_latency(clients[0], servers[0])
    print("Baseline Latency for TCP: " + base_latency)

    # Start the servers
    start_servers(clients, servers, tcp_filename)

    # Start the clients
    start_clients(clients, servers, tcp_filename)

    # Wait for the clients to finish
    CLI(net)

    # Stop the hosts
    stop_hosts(clients)
    stop_hosts(servers)

    # Stop the network
    net.stop()   

if __name__ == '__main__':
    main()