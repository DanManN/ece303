# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import channelsimulator
import utils
import sys
from myhash import checksum_md5
import struct

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
    PACK_SIZE = 1024*128-32
    BUF_SIZE = 3

    def __init__(self, timeout=.1):
        super(SupReceiver, self).__init__(timeout=timeout)

    def getFromChannel(self):
        packet = bytearray()
        while len(packet)<SupReceiver.PACK_SIZE:
            p = self.simulator.u_receive()
            packet += p
            if len(p) < 1024:
                break
        return packet

    def receive(self):
        #self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        ll = -1
        buf = [None]*SupReceiver.BUF_SIZE
        cc = 0
        while True:
            try:
                while cc < SupReceiver.BUF_SIZE:
                    cc += 1
                    data = self.getFromChannel()
                    #self.logger.info("Got data from socket: {}".format(len(data)))
                    checksum = checksum_md5(str(data[:-16]))
                    if checksum == str(data[-16:]):
                        cp = struct.unpack(">Q",str(data[:8]))[0]
                        self.logger.info("current packet {} and ll {}".format(cp,ll))
                        if cp <= SupReceiver.BUF_SIZE + ll:
                            try:
                                buf[cp-ll-1] = data[:-16]
                            except IndexError:
                                pass
                                #self.logger.info("buf: {} , cp: {}, ll: {}\ndata: {}".format(len(buf),cp,ll,data))
                            toresp = bytearray(data[:8])
                            toresp += bytearray(checksum_md5(str(toresp)))
                            self.simulator.u_send(toresp)

                cc = 0
                self.logger.info("llB: {}".format(ll))
                for i in xrange(SupReceiver.BUF_SIZE):
                    if buf[i]:
                        sys.stdout.write(buf[i][16:])
                        ll += 1
                        if buf[i][0:8] == buf[i][8:16]:
                            return
                        if i == SupReceiver.BUF_SIZE-1:
                            buf = [None]*SupReceiver.BUF_SIZE
                    else:
                        buf = buf[i:]
                        buf += [None]*(SupReceiver.BUF_SIZE-len(buf))
                        self.logger.info("BUF LEN: {}".format(len(buf)))
                        break
                self.logger.info("llA: {}".format(ll))

            except socket.timeout:
                pass


if __name__ == "__main__":
    rcvr = SupReceiver()
    rcvr.receive()
