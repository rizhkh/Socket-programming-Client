import binascii
import socket as syssock
import struct
import sys

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from

#   -> create a UDP sokets
# sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
# server_address = ( 'local' , 10000) # this part is basically something else dont know exactly what
# message = 'Msg passed.Received.Sent. Loop de loop.'

# UDPportTx -> port=10000


global UDP_send_port
global UDP_recv_port


def init(UDPportTx, UDPportRx):  # initialize your UDP socket here
    global UDP_send_port
    global UDP_recv_port

    UDP_send_port = UDPportTx
    UDP_recv_port = UDPportRx

    if UDP_send_port == 0:
        UDP_send_port = 27181

    if UDP_recv_port == 0:
        UDP_recv_port = 27182

        print('socket initialized')
    return


class socket:
    #  struct __attribute()


    UDP_IP_ADDRESS = "1.2.3.4"  # WE HAVE TO USE THIS
    UDP_PORT_NO = 1234
    Message = 'hello'

    # constants to add readability
    VERSION = 0x1
    SOCK352_SYN = 0x01
    SOCK352_FIN = 0x02
    SOCK352_ACK = 0x04
    SOCK352_RESET = 0x08
    SOCK352_HAS_OPT = 0xA0
    VER = 0
    FLAGS = 1
    OPT_PTR = 2
    PROTOCOL = 3
    HDR_LEN = 4
    CHECKSUM = 5
    SRC_PORT = 6
    DEST_PORT = 7
    SEQ_NO = 8
    ACK_NO = 9
    WINDOW = 10
    PAYLOAD_LEN = 11
    sock = 0

    def __init__(self):  # fill in your code here
        self.sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        # self.sock2 = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)

        global UDP_send_port  # IS SEND_PORT CLIENT OR RECV_PORT CLIENT FIGURE IT OUT AND PUT IT IN LISTEN
        global UDP_recv_port
        self.send_port = UDP_send_port
        self.recv_port = UDP_recv_port

        self.pkt_hdr_data = '!BBBBHHLLQQLL'
        self.pkt_hdr = struct.Struct(self.pkt_hdr_data)

        print('socket initialized')
        return

    def bind(self, address):

        print('<in bind>')
        print address
        return self.sock.bind(address)

        # return

    def accept(self):
        print('here')
        print self.sock
        print self.recv_port
        (sock, address2) = (self.sock,
                            self.recv_port)  # on the server side server1.py - it gets value of the socket and port so that should be returned through this and get connected to the client // PRINT states were to determine if they working but im still not sure if im suppose to use the send_port or recv_port
        return (sock, address2)

    # <IGNORING LISTEN FOR NOW>
    def listen(backlog):  # backlog is the number of queues so
        return self.sock.listen(backlog)

    def connect(self, address):  # fill in your code here
        print self.sock
        print 'in connect'
        print address
        print 'and > '
        print address[0]
        print self.send_port

        self.sock.connect(address)
        # self.sock.connect((address[0], self.send_port))

        syn_header = self.pkt_hdr.pack(1, 0x01, 0, 0, 320, 0, 0, 0, 1, 0, 0, 0)

        while True:
            self.sock.send(syn_header)
            # start_time = self.sock.settimeout(0.2)  # should probably use settimeout() instead
            syn_ack_data = self.sock.recv(320)
            # end_time = self.sock.settimeout()
            syn_ack = self.pkt_hdr.unpack(syn_ack_data)

            if syn_ack[FLAGS] == (SOCK352_ACK | SOCK352_SYN) and syn_ack[SEQ_NO] == 2 and end_time - start_time < 0.2:
                break

        ack = pkt_hdr.pack(VERSION, SOCK352_ACK, 0, 0, 320, 0, 0, 0, 2, syn_ack[SEQ_NO] + 1, 0, 0)
        self.sock.send(ack)
        return

    def close(self):  # fill in your code here
        sock.socket.shutdown(socket.SHUT_RDWR)
        sock.socket.close(self)
        # self.sock.socket.close()
        return a

        # buffer is the length

    def send(self, buffer):
        bytessent = 0  # fill in your code here
        print 'here in send'
        bytesAcp = bytessent
        while bytessent < buffer:
            sent = self.sock.send(buffer[bytesAcp])
            if sent == 0:
                raise RuntimeError("sock con. broke down")
            bytessent = bytessent + sent
            bytesAcp = bytessent
        return bytesAcp

    def recv(self, nbytes):
        nbytetwo = []
        print 'in recv'
        bytesreceived = 0  # fill in your code here
        while bytesreceived < MSGLEN:
            nbytetwo = self.sock.recv(min(MSGLEN - bytesreceived, 2048))
            if nbytetwo == '':
                raise RuntimeError("socket connection broke down");
            nbytetwo.append(nbytetwo)
            bytesreceived = bytesreceived + len(nbytetwo)
        return bytesreceived  ### sending back ack





