from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel
import random
import time

# Configuration Variables
NUM_SWITCHES = 4
NUM_HOSTS = 10
TRAFFIC_INTENSITY ='10M'

def get_timestamp():
   return time.strftime("%Y%m%d-%H%M%S")

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

   num_servers = len(servers)

   # Set first half of servers as UDP servers and the other half as TCP servers
   udp_servers = servers[:num_servers//2]
   tcp_servers = servers[num_servers//2:]

   num_clients = len(clients)

   # Set first half of clients as UDP clients and the other half as TCP clients
   udp_clients = clients[:num_clients//2]
   tcp_clients = clients[num_clients//2:]

   # Start the network
   net.start()

   return net, switches, udp_servers, tcp_servers, udp_clients, tcp_clients

# Select random UDP server
def random_udp_server(udp_servers):
   return udp_servers[random.randint(0, len(udp_servers)-1)]

# Select random TCP server
def random_tcp_server(tcp_servers):
   return tcp_servers[random.randint(0, len(tcp_servers)-1)]


def start_servers(udp_servers, tcp_servers, udp_clients, tcp_clients, udp_filename, tcp_filename):
   first_udp_client = udp_clients[0]
   # Start UDP Servers
   for udp_server in udp_servers:
       udp_server.cmd(f'iperf -s -t 30 -u -b {TRAFFIC_INTENSITY} >> {udp_filename} 2>&1 &')
       latency = measure_latency(first_udp_client, udp_server)
       print("Latency for UDP (Server " + udp_server.name + "): " + latency)
     
   # Start TCP Servers
   first_tcp_client = tcp_clients[0]
   for tcp_server in tcp_servers:
       tcp_server.cmd(f'iperf -s -t 30 -b {TRAFFIC_INTENSITY} >> {tcp_filename} 2>&1 &')
       latency = measure_latency(first_tcp_client, tcp_server)
       print("Latency for TCP (Server " + tcp_server.name + "): " + latency)

def start_udp_clients(udp_clients, udp_servers, udp_filename):
   # Start UDP Clients
   for udp_client in udp_clients:
       selected_server = random_udp_server(udp_servers)
       udp_client.cmd('iperf -c ' + selected_server.IP() + ' -u -b ' + TRAFFIC_INTENSITY + ' >> f`{udp_filename}` 2>&1 &')
       latency = measure_latency(udp_client, selected_server)
       print("Latency for UDP (Client " + udp_client.name + " to Server " + selected_server.name + "): " + latency)


def start_tcp_clients(tcp_clients, tcp_servers, tcp_filename):
   # Start TCP Clients
   for tcp_client in tcp_clients:
       selected_server = random_tcp_server(tcp_servers)
       tcp_client.cmd('iperf -c ' + selected_server.IP() + ' -b ' + TRAFFIC_INTENSITY + ' >> f`{tcp_filename}` 2>&1 &')
       latency = measure_latency(tcp_client, selected_server)
       print("Latency for TCP (Client " + tcp_client.name + " to Server " + selected_server.name + "): " + latency)

def stop_hosts(hosts):
   for host in hosts:
       host.cmd('kill %iperf')

def measure_latency(client, server):
   return client.cmd('ping -c 1 ' + server.IP())

def main():
   timestamp = get_timestamp()

   udp_filename = f'iPerf_network_udp_stress_test_results_{timestamp}.txt'
   tcp_filename = f'iPerf_network_tcp_stress_test_results_{timestamp}.txt'
   setLogLevel('info')

   # Setup the network
   net, switches, udp_servers, tcp_servers, udp_clients, tcp_clients = setup_network()

   # Start the servers
   start_servers(udp_servers, tcp_servers, udp_clients, tcp_clients, udp_filename, tcp_filename)

   # Start the clients
   start_udp_clients(udp_clients, udp_servers, udp_filename)
   start_tcp_clients(tcp_clients, tcp_servers, tcp_filename)

   # Wait for the clients to finish
   CLI(net)

   # Stop the hosts
   stop_hosts(udp_servers)
   stop_hosts(tcp_servers)
   stop_hosts(udp_clients)
   stop_hosts(tcp_clients)

   # Stop the network
   net.stop()

if __name__ == '__main__':
   main()