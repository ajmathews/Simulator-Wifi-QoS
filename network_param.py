class NetworkParameters:

    def __init__(self, DIFS: int, SIFS: int, ACK: int):
        self.timeDIFS = DIFS
        self.timeSIFS = SIFS
        self.timeACK = ACK

