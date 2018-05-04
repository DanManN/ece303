# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import channelsimulator
import utils
import sys
import hashlib
import struct

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")

def chunk(l, n):
    n = max(1, n)
    return [bytearray(struct.pack(">Q",i/n)) + bytearray(l[i:i+n]) + bytearray(hashlib.md5(str(l[i:i+n])).digest()) for i in xrange(0, len(l), n)]

class SupSender(Sender):
    PACK_SIZE = 1000 # it is actually 1024 because of header (8) + checksum (16)
    WIN_SIZE = 5

    def __init__(self, timeout=10):
        super(SupSender, self).__init__(timeout=timeout)

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        chunks = chunk(data,SupSender.PACK_SIZE)
        cc = 0
        acked = 0
        nacked = set()
        while True:
            try:
                # send stuff
                temp = nacked.copy()
                for i in xrange(SupSender.WIN_SIZE):
                    if temp:
                        self.simulator.put_to_socket(chunks[temp.pop()])
                    else:
                        if cc >= len(chunks):
                            break
                        self.simulator.put_to_socket(chunks[cc])
                        nacked.add(cc)
                        cc = cc+1

                # wait for acks/naks
                for i in xrange(SupSender.WIN_SIZE):
                    if acked == len(chunks):
                        self.logger.info("DONE")
                        return
                    resp = self.simulator.get_from_socket()
                    respnum = struct.unpack(">Q",str(resp[:-16]))[0]
                    self.logger.info("Got RESPONSE from socket: {}".format(respnum))
                    checksum = hashlib.md5(str(resp[:-16])).digest()
                    if checksum == str(resp[-16:]):
                        if respnum in nacked:
                            nacked.remove(respnum)
                            acked += 1

            except socket.timeout:
                pass


if __name__ == "__main__":
    TEST_DATA = bytearray(sys.stdin.read())
    sndr = SupSender()
    sndr.send(TEST_DATA)
