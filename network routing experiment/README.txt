CODE SOURCES
______________________________________________________________________________________________________________________________________________________
  Topologies 
-------------
    Star Topology 
      -  Taken from Constructor University, adapted to fit specific needs of remote Ryu Controller: https://cnds.jacobs-university.de/courses/cn-2019 

    Tree Topology 
      -  Taken from https://webcms3.cse.unsw.edu.au/static/uploads/course/COMP3331/16s1/894894253a9d7bb9b3575af5092c2d80c9382bbbf860e4a9364cfae2bcf04cd6/Lab3a.pdf#:~:text=In%20a%20simple%20tree%20topology,to%20n%20hosts%20(servers). 
      -  Adapted for different number of nodes and to use iPerf

    Full Mesh Topology
      -  Used Star Topology template, increased node links 

Algorithms
-------------
    Round Robin
      -  Adaption from pre-built Simple Switch 13 controller and used template found at: https://github.com/PM-Abhishek/LoadBalancing-in-SDN 
    Least Connections
     -  Adapted from pre-built Simple Switch 13: https://github.com/Deepak281295/LoadBalancing-in-SDN 


Network Load Experiment Notes:
________________________________________________________________________________________________________________________________________________________
* In order to increase scale of tests by increasing network complexity, each topology file's number of nodes and switches, and data links must be updated
* Round Robin as well as Least Connections Algorithm acts as a starting template. To test on different topologies, changes must be made to fit specific number of nodes
