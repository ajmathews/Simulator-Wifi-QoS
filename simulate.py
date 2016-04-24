import network
import node

class Simulate:

    def __init__(self):
        self.isDIFS = False
        self.isSIFS = False
        self.isSIFSAndACK = False
        self.isPacket = False
        self.currentCellTimer = 0
        self.time = 0
        self.collisionCount = 0

    def run(self, network: network.Network, isQoS: bool):

        nodes = network.nodes # type: list[node.Node]
        numberOfNodes = network.totalNumberOfNodes

        if (not isQoS):
            print("\nInitiating 802.11 Standard Simulation")

            # Creating the backoff list with all -1
            backoffList = [-1 for _ in range(numberOfNodes)]

            # Assigning initial backoff if the node has packets to transmit
            for i in range(numberOfNodes):
                if (nodes[i].numberOfPacketsRemaining > 0):
                    backoffList[i] =  network.generateRandomBackoff(nodes[i].contentionWindow)

            self.startDIFS()

            while (network.totalNumberOfPackets > 0 or self.isSIFSAndACK):
                if (self.isDIFS or self.isSIFS or self.isSIFSAndACK):
                    if (self.currentCellTimer > 0):
                        self.time += self.currentCellTimer
                        self.currentCellTimer = 0
                        continue
                    # If the cell timer = 0
                    if (self.isSIFSAndACK):
                        self.startDIFS()
                    else:
                        self.stopAll()
                    continue


                if (not self.isDIFS and not self.isSIFSAndACK and not self.isSIFS and not self.isPacket):
                    # If any node is ready to transmit
                    if (0 in backoffList):
                        # collisionCount = backoffList.count(0)
                        nodeIndexes = [i for i, val in enumerate(backoffList) if val==0]

                        if (len(nodeIndexes) > 1):
                            # Collision will occur
                            self.collisionCount += 1
                            # Since we are using uniform packet size throughout
                            maxTime = network.packetSize
                            for i in nodeIndexes:
                                nodes[i].doubleContentionWindow()
                                backoffList[i] = network.generateRandomBackoff(nodes[i].contentionWindow)

                            self.time += maxTime
                            self.startDIFS()
                            continue

                        else:
                            # Single pack transmission
                            nodeIndex = nodeIndexes[0]
                            node = nodes[nodeIndex] # type: node.Node
                            # print("Node {0} is transmitting @ t {1}".format(nodeIndex+1, self.time))
                            node.numberOfPacketsRemaining -= 1
                            self.time += network.packetSize
                            network.totalNumberOfPackets -= 1

                            if (node.numberOfPacketsRemaining > 0):
                                node.resetContentionWindow()
                                backoffList[nodeIndex] = network.generateRandomBackoff(node.contentionWindow)
                            else:
                                backoffList[nodeIndex] = -1
                                node.timeToCompleteTransmission = self.time
                            self.startSIFSAndACK()
                            continue
                    else:
                        # Backoff Period
                        while (backoffList.count(0) == 0):
                            minTime = min([x for x in backoffList if x > 0])
                            self.time += minTime
                            for i in range(network.totalNumberOfNodes):
                                if (backoffList[i] != -1):
                                    backoffList[i] -= minTime



            print("Simulation took {0} unit time with {1} collisions".format(self.time, self.collisionCount))

        elif (isQoS):

            print("\nInitiating 802.11 QoS Simulation")

            numberOfTrafficCategories = 3

            # Intializes backoff list
            backoffList = [-1 for _ in range(numberOfNodes)]
            # Decides which nodes are assigned which TC values
            trafficCategoryList = [_%numberOfTrafficCategories + 1 for _ in range(numberOfNodes)]
            # List to remember which nodes use burst mode
            burstModeNodeIndexes = [] # type: list[int]

            # Initializing nodes with the TC parameters
            for i in range(numberOfNodes):
                if (nodes[i].numberOfPacketsRemaining > 0):
                    backoffList[i] = network.generateRandomBackoff(nodes[i].contentionWindow, isQoS)
                    nodes[i].TC = trafficCategoryList[i]
                    if (trafficCategoryList[i] == 1):
                        nodes[i].isBurstModeEnabled = network.isBurstModeEnabled
                        nodes[i].isBlockACKEnabled = network.isBlockACKEnabled

                    # --------This is for simulation purposes only---------
                    # Here, TC2 nodes are made TC1 nodes without burst and block ACK to compare
                    # if (nodes[i].TC == 2):
                    #     nodes[i].TC = 1
                    #     nodes[i].isBurstModeEnabled = False
                    #     nodes[i].isBlockACKEnabled = False

                    # AIFS[TC1] = DIFS + 1, AIFS[TC2] = DIFS + 2, AIFS[TC3] = DIFS + 3
                    nodes[i].AIFS = network.networkParams.timeDIFS + nodes[i].TC

            self.startDIFS()
            isBurstModeEnabled = False
            isBlockACKEnabled = False
            for i in range(numberOfNodes):
                if (nodes[i].isBurstModeEnabled == True):
                    isBurstModeEnabled = True
                    burstModeNodeIndexes.append(i)
                if (nodes[i].isBlockACKEnabled == True):
                    isBlockACKEnabled = True
                if (isBlockACKEnabled and isBurstModeEnabled):
                    break

            while (network.totalNumberOfPackets > 0 or self.isSIFSAndACK):
                if (self.isDIFS or self.isSIFS or self.isSIFSAndACK):
                    # if (self.currentCellTimer > 0):False
                    self.time += self.currentCellTimer
                    self.currentCellTimer = 0

                    if (self.isDIFS):
                        # If the AIFS is equal to DIFS, decrement the backoff as it starts counting down at (DIFS-1)
                        for i in range(numberOfNodes):
                            if (nodes[i].AIFS == network.networkParams.timeDIFS and backoffList[i] != -1):
                                backoffList[i] -= 1
                        self.stopAll()
                    elif (self.isSIFSAndACK):
                        self.startDIFS()
                        continue
                    # else:
                    #     self.stopAll() --> since i am not using startSIFS

                if (not self.isDIFS and not self.isSIFSAndACK and not self.isSIFS and not self.isPacket):
                    if (0 in backoffList):
                        # collisionCount = backoffList.count(0)
                        nodeIndexes = [i for i, val in enumerate(backoffList) if val == 0]

                        if (len(nodeIndexes) > 1):
                            # Collision
                            self.collisionCount += 1

                            if (not isBurstModeEnabled or (isBurstModeEnabled and not isBlockACKEnabled)):
                                # This is for normal transmission OR for Burst mode without Block ACK
                                # Since we are using uniform packet size throughout
                                maxTime = network.packetSize

                            elif (isBlockACKEnabled):
                                # Burst and Block is enabled on any node
                                # Now to check if one of the transmitting nodes has Burst Mode Enabled
                                isNodeBurstModeEnabled = False
                                for index in nodeIndexes:
                                    if (index in burstModeNodeIndexes):
                                        isNodeBurstModeEnabled = True
                                        break

                                if (isNodeBurstModeEnabled):
                                    # This is for Burst mode with Block ACK
                                    maxTime = network.burstSize*(network.packetSize + network.networkParams.timeSIFS) - network.networkParams.timeSIFS
                                else:
                                    # These are regular nodes
                                    maxTime = network.packetSize
                            else:
                                print("-----You shouldn't be here------ Block ACK and Burst Mode should be enabled at the same time")

                            for i in nodeIndexes:
                                nodes[i].doubleContentionWindow()
                                backoffList[i] = network.generateRandomBackoff(nodes[i].contentionWindow, isQoS)
                            self.time += maxTime
                            self.startDIFS()

                            continue

                        else:
                            # Single transmission
                            nodeIndex = nodeIndexes[0]
                            node = nodes[nodeIndex]  # type: node.Node
                            # print("Node {0} is transmitting @ t {1}".format(nodeIndex + 1, self.time))

                            if (not node.isBurstModeEnabled):
                                node.numberOfPacketsRemaining -= 1
                                maxTime = network.packetSize
                                network.totalNumberOfPackets -= 1
                                self.startSIFSAndACK()
                            else:
                                # Burst Mode is enabled
                                if (node.isBlockACKEnabled):
                                    maxTime = network.burstSize*(network.packetSize + network.networkParams.timeSIFS) - network.networkParams.timeSIFS
                                    self.startSIFSAndACK()
                                else:
                                    maxTime = network.burstSize*(network.packetSize + network.networkParams.timeACK + 2*network.networkParams.timeSIFS) - network.networkParams.timeSIFS
                                    self.startDIFS()

                                if (node.numberOfPacketsRemaining >= network.burstSize):
                                    node.numberOfPacketsRemaining -= network.burstSize
                                    network.totalNumberOfPackets -= network.burstSize
                                else:
                                    network.totalNumberOfPackets -= node.numberOfPacketsRemaining
                                    node.numberOfPacketsRemaining = 0

                            if (node.numberOfPacketsRemaining > 0):
                                node.resetContentionWindow()
                                backoffList[nodeIndex] = network.generateRandomBackoff(node.contentionWindow, isQoS)
                            else:
                                backoffList[nodeIndex] = -1
                                node.timeToCompleteTransmission = self.time
                            self.time += maxTime
                            continue
                    else:
                        # Backoff Period
                        step = 0
                        while (backoffList.count(0) == 0):

                            # Starts at DIFS + 1
                            self.time += 1
                            step += 1
                            for i in range(numberOfNodes):
                                if (network.networkParams.timeDIFS + step >= nodes[i].AIFS and backoffList[i] != -1):
                                    backoffList[i] -= 1

            print("Simulation took {0} unit time with {1} collisions".format(self.time, self.collisionCount))


    def startDIFS(self):
        self.stopAll()
        self.isDIFS = True
        self.currentCellTimer = network.Network.networkParams.timeDIFS

    def startSIFS(self):
        self.stopAll()
        self.isDIFS = True
        self.currentCellTimer = network.Network.networkParams.timeSIFS

    def startSIFSAndACK(self):
        self.stopAll()
        self.isSIFSAndACK = True
        self.currentCellTimer = network.Network.networkParams.timeSIFS + network.Network.networkParams.timeACK

    def stopAll(self):
        self.isDIFS = False
        self.isSIFS = False
        self.isSIFSAndACK = False
        self.isPacket = False
        self.currentCellTimer = 0


