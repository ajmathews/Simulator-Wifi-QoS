import network_param
import node
import random

class Network:

    rand = random.Random()
    networkParams = network_param.NetworkParameters

    def __init__(self, numberOfNodes: int, numberOfPacketsPerNode: int, contentionWindowMin: int, packetSize: int):

        Network.networkParams = network_param.NetworkParameters(3, 1, 1)

        self.totalNumberOfNodes = numberOfNodes
        self.totalNumberOfPackets = numberOfPacketsPerNode*numberOfNodes
        self.packetSize = packetSize
        self.nodes = [] # type: list[node.Node]
        self.burstSize = 0
        self.isBurstModeEnabled = False
        self.isBlockACKEnabled = False

        for i in range(numberOfNodes):
            temp = node.Node(numberOfPacketsPerNode, contentionWindowMin)
            self.nodes.append(temp)

    def generateRandomBackoff(self, contentionWindow: int, isQoS = False) -> int:
        if (isQoS):
            return Network.rand.randint(1, contentionWindow)
        return Network.rand.randint(0, contentionWindow-1)


    # def __str__(self, *args, **kwargs):
    #
    #     text = 'Network'
    #     text += "totalNumberOfNodes ->" + str(self.totalNumberOfNodes)
    #     text += "; totalNumberOfPackets ->" + str(self.totalNumberOfPackets)
    #     for i in len(self.nodes):
    #         text += str(self.nodes);
    #
    #     text += "\n"
    #     return text
