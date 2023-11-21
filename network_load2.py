#Xue’s code modified again:
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel
import random
import time

# Configuration Variables
TRAFFIC_INTENSITY = '10M'
EXPERIMENT_DURATION = 30

def get_timestamp():
    return time.strftime("%Y%m%d-%H%M%S")

def setup_network(num_hosts, num_switches):
    net = Mininet(controller=None, switch=OVSKernelSwitch, host=Host)

    # Add Ryu Controller
    # Note: Ryu must be already running in a terminal
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Add Switches
    switches = [net.addSwitch(f's{i+1}') for i in range(num_switches)]

    # Link Switches
    for i in range(num_switches - 1):
        net.addLink(switches[i], switches[i + 1])

    # Add Hosts
    hosts = [net.addHost(f'h{i+1}') for i in range(num_hosts)]

    # Link Hosts to Switches
    for i in range(num_hosts):
        net.addLink(hosts[i], switches[i % num_switches])

    # Start the network
    net.start()

    return net, hosts, switches

def start_iperf_servers(hosts, traffic_type, filename):
    for host in hosts:
        host.cmd(f'iperf -s -t {EXPERIMENT_DURATION} -{traffic_type} >> {filename} 2>&1 &')

def start_iperf_clients(clients, servers, traffic_type, filename):
    for client in clients:
        selected_server = random.choice(servers)
        client.cmd(f'iperf -c {selected_server.IP()} -{traffic_type} -t {EXPERIMENT_DURATION} >> {filename} 2>&1 &')

def stop_iperf_processes(hosts):
    for host in hosts:
        host.cmd('kill %iperf')

def measure_latency(client, server):
    return client.cmd(f'ping -c 1 {server.IP()}')

def main():
    timestamp = get_timestamp()
    udp_filename = f'iPerf_network_udp_stress_test_results_{timestamp}.txt'
    tcp_filename = f'iPerf_network_tcp_stress_test_results_{timestamp}.txt'
    setLogLevel('info')

    # Experiment Configurations
    topologies = [(3, 1), (5, 2), (7, 3)]  # Example: [(num_hosts, num_switches), ...]

    for num_hosts, num_switches in topologies:
        # Setup the network
        net, hosts, switches = setup_network(num_hosts, num_switches)

        # Start iPerf servers
        start_iperf_servers(hosts, 'u', udp_filename)
        start_iperf_servers(hosts, 't', tcp_filename)

        # Start iPerf clients
        start_iperf_clients(hosts, hosts, 'u', udp_filename)
        start_iperf_clients(hosts, hosts, 't', tcp_filename)

        # Wait for the experiment to finish
        time.sleep(EXPERIMENT_DURATION + 5)

        # Stop iPerf processes
        stop_iperf_processes(hosts)

        # Stop the network
        net.stop()

if __name__ == '__main__':
    main()


