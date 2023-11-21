#!/usr/bin/env python
#modified; taken from Constructor University: https://cnds.jacobs-university.de/courses/cn-2019/p1-star.py
""" star.py:

    This Mininet script creates a simple star topology with a switch
    in the center and connects it to a Ryu controller:

      h1               h3
         \           /
        10 \       /10 mbps
             \   /
               s1
             /   \
        10 /       \10 mbps
         /           \
      h2              h4
"""

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.node import RemoteController

class Star(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        s1 = self.addSwitch('s1')
        self.addLink(h1, s1, bw=10)
        self.addLink(h2, s1, bw=10)
        self.addLink(h3, s1, bw=10)
        self.addLink(h4, s1, bw=10)

if __name__ == '__main__':
    setLogLevel('info')

    topo = Star()
    net = Mininet(topo=topo, link=TCLink, controller=None)

    # Start Ryu controller
    ryu_cmd = 'ryu-manager your_controller.py'  # Replace with your actual Ryu controller script
    net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6633, command=ryu_cmd)

    net.start()
    CLI(net)
    net.stop()



