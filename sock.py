
# CS 352 project part 2 
# this is the initial socket library for project 2 
# You wil need to fill in the various methods in this
# library 

# main libraries 
import binascii
import socket as syssock
import struct
import sys
import time
import random

# encryption libraries 
import nacl.utils
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, Box

# if you want to debug and print the current stack frame 
from inspect import currentframe, getframeinfo

# these are globals to the sock352 class and
# define the UDP ports all messages are sent
# and received from

global UDP_sock

# the ports to use for the sock352 messages 
global sock352portTx
global sock352portRx
# the public and private keychains in hex format 
global publicKeysHex
global privateKeysHex

# the public and private keychains in binary format 
global publicKeys
global privateKeys

# the encryption flag 
global ENCRYPT

publicKeysHex = {} 
privateKeysHex = {} 
publicKeys = {} 
privateKeys = {}

# this is 0xEC 
ENCRYPT = 236 

# this is the structure of the sock352 packet 
sock352HdrStructStr = '!BBBBHHLLQQLL'

#constants to add readability
RETRIES = 5
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

def init(UDPportTx,UDPportRx):
    global sock352portTx
    global sock352portRx
    global UDP_sock
    
    sock352portTx = int(UDPportTx)
    sock352portRx = int(UDPportRx)
    UDP_sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
    UDP_sock.settimeout(0.2)
    
    if sock352portTx == 0:
        sock352portTx = 27182
    
    if sock352portRx == 0:
        sock352portRx = 27182
    
    return
    
# read the keyfile. The result should be a private key and a keychain of
# public keys
def readKeyChain(filename):
    global publicKeysHex
    global privateKeysHex 
    global publicKeys
    global privateKeys 
    
    if (filename):
        try:
            keyfile_fd = open(filename,"r")
            for line in keyfile_fd:
                words = line.split()
                # check if a comment
                # more than 2 words, and the first word does not have a
                # hash, we may have a valid host/key pair in the keychain
                if ( (len(words) >= 4) and (words[0].find("#") == -1)):
                    host = words[1]
                    port = words[2]
                    keyInHex = words[3]
                    if (words[0] == "private"):
                        privateKeysHex[(host,port)] = keyInHex
                        privateKeys[(host,port)] = nacl.public.PrivateKey(keyInHex, nacl.encoding.HexEncoder)
                    elif (words[0] == "public"):
                        publicKeysHex[(host,port)] = keyInHex
                        publicKeys[(host,port)] = nacl.public.PublicKey(keyInHex, nacl.encoding.HexEncoder)
        except Exception,e:
            print ( "error: opening keychain file: %s %s" % (filename,repr(e)))
    else:
            print ("error: No filename presented")             

    return (publicKeys,privateKeys)

class socket:
    
    def __init__(self):
        global sock352portTx
        global sock352portRx
        global UDP_sock
        # to make future use of these variables easier
        # store as instance variables
        # this is likely only for part 1
        self.sock = UDP_sock
        self.send_port = sock352portTx
        self.recv_port = sock352portRx
        
        self.pkt_hdr_data = '!BBBBHHLLQQLL'
        self.pkt_hdr = struct.Struct(self.pkt_hdr_data)
        
        self.encryption = False
        
        self.sock.bind(('', self.recv_port))
        return
        
    def bind(self,address):
        # bind is not used in this assignment 
        return

    def connect(self,*args):

        global ENCRYPT
        if (len(args) >= 1): 
            (host,port) = args[0]
        if (len(args) >= 2):
            if (args[1] == ENCRYPT):
                self.encryption = True
                
        # create header with SYN flag
        seq_no = random.randint(0,100)
        syn_header = self.pkt_hdr.pack(VERSION, SOCK352_SYN, 0, 0, 40, 0, 0, 0, seq_no, 0, 0, 0)
        
        i = 0
        while i < RETRIES:
            # send SYN packet
            self.sock.sendto(syn_header, (host, self.send_port))
            
            # receive ACK from server
            # resend SYN if timeout occurs
            try:
                syn_ack_data, addr = self.sock.recvfrom(40)
                
                syn_ack = self.pkt_hdr.unpack(syn_ack_data)
            
                # check ACK for errors
                # if errors are found, resend SYN
                if syn_ack[FLAGS] == (SOCK352_ACK | SOCK352_SYN) and syn_ack[ACK_NO] == seq_no+1:
                    break
            except syssock.timeout:
                i += 1
                continue
            i += 1
        
        # send ACK to server
        ack = self.pkt_hdr.pack(VERSION, SOCK352_ACK, 0, 0, 40, 0, 0, 0, seq_no+1, syn_ack[SEQ_NO]+1, 0, 0)
        self.sock.sendto(ack, (host, self.send_port))
        
        # connection process complete
        # store address of server for use in future send/receives
        self.conn = (host, self.send_port)
        
        #create nonce and find keys to create box
        if self.encryption == True:
            global publicKeys
            global privateKeys
            
            self.nonce = nacl.utils.random(Box.NONCE_SIZE)
            
            addr = (host, str(self.send_port))
            if addr in publicKeys:
                publickey = publicKeys[addr]
            else:
                publickey = publicKeys[('*','*')]
            
            privatekey = privateKeys[('*','*')]
            
            self.box = Box(privatekey, publickey)
            
            print privatekey
            print publickey
            
        return

    def listen(self,backlog):
        # listen is not used in this assignments 
        return
    

    def accept(self,*args):
        # example code to parse an argument list 
        global ENCRYPT
        if (len(args) >= 1):
            if (args[0] == ENCRYPT):
                self.encryption = True
        
        while True:
            # receive SYN packet from a client
            try:
                syn_header_data, addr = self.sock.recvfrom(40)
            except syssock.timeout:
                continue
            syn_header = self.pkt_hdr.unpack(syn_header_data)
            
            # if there is an error
            # ignore and wait for another packet
            if syn_header[FLAGS] == SOCK352_SYN:
                break
        
        
        # send ACK for SYN packet
        syn_ack_flags = SOCK352_SYN | SOCK352_ACK
        seq_no = random.randint(0,100)
        syn_ack = self.pkt_hdr.pack(VERSION, syn_ack_flags, 0, 0, 40, 0, 0, 0, seq_no, syn_header[SEQ_NO]+1, 0, 0)
        self.sock.sendto(syn_ack, addr)
        
        # receive ACK from client
        try:
            ack, addr = self.sock.recvfrom(40)
        except syssock.timeout:
            pass
        
        
        # connection complete, store client address
        self.conn = (addr[0], self.send_port)
        
        #create nonce and find keys to create box
        if self.encryption == True:
            global publicKeys
            global privateKeys
            
            self.nonce = nacl.utils.random(Box.NONCE_SIZE)
            
            if (addr[0], str(addr[1])) in publicKeys:
                publickey = publicKeys[(addr[0], str(addr[1]))]
            elif ('localhost', str(self.send_port)) in publicKeys:
                publickey = publicKeys[('localhost',str(self.send_port))]
            else:
                publickey = publicKeys[('*','*')]
            
            privatekey = privateKeys[('*','*')]
            
            self.box = Box(privatekey, publickey)
            
            print privatekey
            print publickey
        
        (clientsocket, address) = (self, addr)
        return (clientsocket,address)

    def close(self):
        fin_header = self.pkt_hdr.pack(VERSION, SOCK352_FIN, 0, 0, 40, 0, 0, 0, 0, 0, 0, 0)
        self.sock.sendto(fin_header, self.conn)
        
        try:
            fin_ack_data, addr = self.sock.recvfrom(40)
        except syssock.timeout:
            pass
        
        self.conn = None
        return

    def send(self,buffer):
        buf = []
        
        # split buffer into chunks if necessary
        if len(buffer) > 65427:
            buf, num_pkts = _split(buffer)
        else:
            buf.append(buffer)
            num_pkts = 1
        
        i = 0
        j = 0
        seq_no = 0
        while i < num_pkts and j < RETRIES:
            # build and send packet with appropriate sequence no. and payload length
            payload_size = len(buf[i])
            opt = 0
            
            if self.encryption == True:
                opt = 1
                payload_size += 40 #for nonce+authenticator
                buf[i] = self.box.encrypt(buf[i], self.nonce)
            
            header = self.pkt_hdr.pack(VERSION, 0, opt, 0, 40, 0, 0, 0, seq_no, 0, 0, payload_size)
            packet = header + buf[i]
            self.sock.sendto(packet, self.conn)
            
            # receive ACK for this packet
            # resend packet if timeout occurs
            try:
                ack_data, addr = self.sock.recvfrom(40)
                
                ack = self.pkt_hdr.unpack(ack_data)
            
                # if there is an error in the ACK
                # resend the same chunk of data
                # otherwise, send the next chunk
                if ack[ACK_NO] != seq_no + payload_size:
                    j += 1
                    continue
                else:
                    seq_no = seq_no + payload_size
                    i+=1
                    j = 0
            except syssock.timeout:
                j += 1
                continue
            
        bytessent = seq_no - num_pkts*40
        return bytessent

    def recv(self,nbytes):
        bytesreceived = ''
        
        j = 0
        # receive up to the number of bytes requested by the user
        while len(bytesreceived) < nbytes and j < RETRIES:
            try:
                payload, addr = self.sock.recvfrom(65535)
                header = self.pkt_hdr.unpack(payload[:40])
            
                # if the seq no of the received packet does not match
                # the number of bytes already received, do nothing
                # otherwise send the appropriate ACK
                if header[SEQ_NO] != len(bytesreceived):
                    j += 1
                    continue
                else:
                    ack = self.pkt_hdr.pack(VERSION, SOCK352_ACK, 0, 0, 40, 0, 0, 0, 0, header[PAYLOAD_LEN]+header[SEQ_NO], 0, 0)
                    self.sock.sendto(ack, self.conn)
                    
                    # add the new data to the buffer that will be sent back to the user
                    if header[OPT_PTR] == 1:
                        bytesreceived = bytesreceived + self.box.decrypt(payload[40:])
                    else:
                        bytesreceived = bytesreceived + payload[40:]
            except syssock.timeout:
                j += 1
                continue
        
        return bytesreceived



# Utility Functions
        
# splits data into chunks small enough to send in a UDP packet (64K)
# returns a 2-tuple containing the list of chunks and the total number of chunks
def _split(buffer):
    # 65467 is the max number of bytes we can send with our header
    num_packets = len(buffer) / 65467 + 1
    buf = []
    
    for i in range(num_packets):
        buf.append(buffer[i*65467:i*65467+65467])
    
    return (buf, num_packets)
