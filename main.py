# The code will initiate the simulation from here
import random
import simulate
import network as ntwk
import time

def main():

    numberOfNodes = 100
    numberOfPacketsPerNode = 300
    contentionWindowMin = 8
    numberOfSims = 1000
    packetSize = 10
    isQoS = True  # type: bool
    # isQoS = False  # type: bool
    isBurstModeEnabled = True
    isBlockACKEnabled = True

    # Initializing random function for the whole simulation
    rand = random.Random()
    rand.seed(time.gmtime())

    timings = [] # type: list[int]
    collisions = [] # type: list[int]
    burstSize = 3
    nodalTransmissionTimes = [ [0 for _ in range(numberOfSims)] for _ in range(numberOfNodes) ] # type: list[int][int]

    if (not isQoS and (isBlockACKEnabled or isBurstModeEnabled)):
        print("The Block/Burst mode cannot be used in a non-QoS environment")
    elif (isQoS  and not isBurstModeEnabled and isBlockACKEnabled):
         print("The Block ACK mode requires Burst mode to be active for implementation")
    else:

        for simNum in range(numberOfSims):
            print("{0}".format(simNum), end="")
            sim = simulate.Simulate() # type: simulate.Simulate
            # Create a new Network object for each simulation run
            network = ntwk.Network(numberOfNodes, numberOfPacketsPerNode, contentionWindowMin, packetSize) # type: ntwk.Network
            network.rand = rand
            network.burstSize = burstSize

            network.isBurstModeEnabled = isBurstModeEnabled
            network.isBlockACKEnabled = isBlockACKEnabled
            # Initiating simulation
            sim.run(network, isQoS)

            # Collects nodal time statistics
            for nodeNum in range(numberOfNodes):
                nodalTransmissionTimes[nodeNum][simNum] = network.nodes[nodeNum].timeToCompleteTransmission
            # Collects simulation's average time and collision count
            timings.append(sim.time)
            collisions.append(sim.collisionCount)

        avgTime = sum(timings)/numberOfSims
        print("\nAverage Time: {0}".format(avgTime))
        nodalTimeAverages = []
        for i in range(numberOfNodes):
            nodalTimeAverages.append(sum(nodalTransmissionTimes[i])/numberOfSims)
        print("Nodal Average Times: ", nodalTimeAverages)
        print("Average Throughput {0}".format((numberOfPacketsPerNode*numberOfNodes)/avgTime))
        print("Average collisions: {0}".format(sum(collisions) / numberOfSims))

main()

