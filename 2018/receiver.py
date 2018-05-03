# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import channelsimulator
import utils
import sys
import hashlib

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class SupReceiver(Receiver):
    PACK_SIZE = 4
    WIN_SIZE = 5

    def __init__(self, timeout=1):
        super(SupReceiver, self).__init__(timeout=timeout)

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        recd = set()
        while True:
            try:
                data = self.simulator.get_from_socket()
                self.logger.info("Got data from socket: {}".format(data[1:-16].decode('ascii')))
                checksum = hashlib.md5(str(data[1:-16])).digest()
                if checksum == str(data[-16:]) and checksum not in recd:
                    sys.stdout.write(data[1:-16])
                    toresp = bytearray([data[0],1])
                    toresp += bytearray(hashlib.md5(str(toresp)).digest())
                    recd.add(checksum)
                    self.simulator.put_to_socket(toresp)
            except socket.timeout:
                return


if __name__ == "__main__":
    rcvr = SupReceiver()
    rcvr.receive()
