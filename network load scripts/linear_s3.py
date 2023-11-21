#!/usr/bin/python
# taken from: https://gist.github.com/John-Lin/961156c1c6dcac545b41

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.node import RemoteController

REMOTE_CONTROLLER_IP = "127.0.0.1"

class SimpleTopo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        switch1 = self.addSwitch('s1', protocols='OpenFlow13')
        switch2 = self.addSwitch('s2', protocols='OpenFlow13')
        switch3 = self.addSwitch('s3', protocols='OpenFlow13')  # Added switch s3
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')  # Added host h4

        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch2)
        self.addLink(host4, switch3)  # Added link for h4 and s3

def simpleTest():
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=None, autoStaticArp=True)
    net.addController("c0", controller=RemoteController, ip=REMOTE_CONTROLLER_IP, port=6633)
    net.start()

    # Redirecting output to a text file named simple_linear_data.txt
    with open("linear_s3_data.txt", "w") as f:
        # Dumping host connections
        f.write("Dumping host connections:\n")
        f.write(str(net.pingAll()) + "\n")

        # Testing latency between h1 and h2
        f.write("\nTesting latency between h1 and h2:\n")
        result = net.ping([net.get('h1'), net.get('h2')], timeout=1)
        if isinstance(result, float):
            # Handle the case when there's only one host
            result = [result]
        f.write("Latency Results:\n")
        f.write("Average Latency: {}\n".format(sum(result) / len(result)))
        f.write("Maximum Latency: {}\n".format(max(result)))
        f.write("Minimum Latency: {}\n".format(min(result)))

        # Testing throughput between h1 and h2
        f.write("\nTesting throughput between h1 and h2:\n")
        h1, h2 = net.get('h1', 'h2')
        f.write(str(net.iperf((h1, h2))) + "\n")

        # Testing packet loss between h1 and h2
        f.write("\nTesting packet loss between h1 and h2:\n")
        f.write(str(net.ping([net.get('h1'), net.get('h2')], timeout=1)) + "\n")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simpleTest()


