
class Node:
    "This domain object is to handle the Node's properties"
    contentionWindowMin = 0

    def __init__(self, numberOfPacketsRemaining: int, contentionWindow: int):
        self.numberOfPacketsRemaining = numberOfPacketsRemaining
        self.contentionWindow = contentionWindow
        self.TC = 0
        self.AIFS = 0
        self.isBurstModeEnabled = False
        self.isBlockACKEnabled = False

        # Statistical purposes
        self.timeToCompleteTransmission = 0

        Node.contentionWindowMin = contentionWindow

    def resetContentionWindow(self):
        self.contentionWindow = Node.contentionWindowMin

    def doubleContentionWindow(self):
        self.contentionWindow *= 2

    # def __str__(self, *args, **kwargs):
    #     text = 'Node: '
    #     text += "numberOfPacketsRemaining ->" + str(self.numberOfPacketsRemaining)
    #     text += "; contentionWindow ->" + str(self.contentionWindow)
    #     text += "\n"
    #     return text

