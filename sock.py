
import binascii
import random
import socket as syssock
import struct
import sys
import time

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from

#   -> create a UDP sokets
#sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
#server_address = ( 'local' , 10000) # this part is basically something else dont know exactly what
#message = 'Msg passed.Received.Sent. Loop de loop.'

# UDPportTx -> port=10000

#constants to add readability
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



# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from
global UDP_send_port
global UDP_recv_port
global UDP_sock

def init(UDPportTx,UDPportRx):   # initialize your UDP socket here 
    global UDP_send_port
    global UDP_recv_port
    global UDP_sock
	
    UDP_send_port = int(UDPportTx)
    UDP_recv_port = int(UDPportRx)
    UDP_sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
    UDP_sock.settimeout(0.2)
    
    if UDP_send_port == 0:
        UDP_send_port = 27181
    
    if UDP_recv_port == 0:
        UDP_recv_port = 27182
    
    print('socket initialized')
    return



class socket:

  #  struct __attribute()
  
    def __init__(self):
        global UDP_send_port
        global UDP_recv_port
        global UDP_sock
        # to make future use of these variables easier
        # store as instance variables
        # this is likely only for part 1
        self.sock = UDP_sock
        self.send_port = UDP_send_port
        self.recv_port = UDP_recv_port
        
        self.pkt_hdr_data = '!BBBBHHLLQQLL'
        self.pkt_hdr = struct.Struct(self.pkt_hdr_data)
        print "SOCKET CLASS SOCKET INITIALIZED"
        
        return


    def bind(self,address):
        print'<in bind>'
        self.sock.bind((address[0], self.recv_port))
        return
      

    def accept(self):
        print('in Accept()')
        ## THIS PART IS FOR SENDING AND RECV PCK ACKNOWLEDGMENTS
        while True:
            try:
                syn_header_data, addr = self.sock.recvfrom(40)
            except:
                continue
            syn_header = self.pkt_hdr.unpack(syn_header_data)
            if syn_header[FLAGS] == SOCK352_SYN:
                break
        ##
        
        ##THIS PART SENDS  ACK FOR SYN PACKET
        syn_ack = self.pkt_hdr.pack(VERSION,SOCK352_SYN | SOCK352_ACK,0,0,40,0,0,0, random.randint(0,100), syn_header[SEQ_NO]+1,0,0)
        self.sock.sendto(syn_ack, addr)
        
        ##THIS PART RECEIVES ACK FROM CLIENT
        try:
            ack, addr = self.sock.recvfrom(40) #my guess is addr in this ack address
        except syssock.timeout:
            pass
            
        ##ABOVE PART COMPLETES THE CONNECTION	
        self.conn = (addr[0], self.send_port) #HONESTLY DONT KNOW WHAT THIS PART DOES
        (clientsocket, address) = (self.sock, addr)	
        #print self.sock
        #print self.recv_port
        #(sock,address2) = (self.sock,self.recv_port)
        #return (sock,address2)
        return (clientsocket,address)

            
    #<IGNORING LISTEN FOR NOW>		
    def listen(self,backlog): #backlog is the number of queues so
        return 

         
    def connect(self,address):
        # bind socket in order to receive packets on the given port
        # this will only be called by client
        self.sock.bind(('', self.recv_port))
        
        # create header with SYN flag
        seq_no = random.randint(0,100)
        syn_header = self.pkt_hdr.pack(VERSION, SOCK352_SYN, 0, 0, 40, 0, 0, 0, seq_no, 0, 0, 0)
        
        while True:
            # send SYN packet
            self.sock.sendto(syn_header, (address[0], self.send_port))
            
            # receive ACK from server
            # resend SYN if timeout occurs
            try:
                syn_ack_data, addr = self.sock.recvfrom(40)
            except syssock.timeout:
                continue
            
            syn_ack = self.pkt_hdr.unpack(syn_ack_data)
            
            # check ACK for errors
            # if errors are found, resend SYN
            if syn_ack[FLAGS] == (SOCK352_ACK | SOCK352_SYN) and syn_ack[ACK_NO] == seq_no+1:
                break
        
        # send ACK to server
        ack = self.pkt_hdr.pack(VERSION, SOCK352_ACK, 0, 0, 40, 0, 0, 0, seq_no+1, syn_ack[SEQ_NO]+1, 0, 0)
        self.sock.sendto(ack, (address[0], self.send_port))
        
        # connection process complete
        # store address of server for use in future send/receives
        self.conn = (address[0], self.send_port)
        
        return


          
    def close(self):   # fill in your code here
        sock.socket.shutdown(socket.SHUT_RDWR)
        sock.socket.close(self)
        #self.sock.socket.close()
        return a

        # buffer is the length
    def send(self,buffer):
            bytessent = 0     # fill in your code here
            print 'here in send'
            bytesAcp=bytessent
            while bytessent < buffer:
                sent = self.sock.send( buffer[bytesAcp] )
                if sent==0:
                    raise RuntimeError("sock con. broke down")
                bytessent=bytessent+sent
                bytesAcp=bytessent
            return bytesAcp

    def recv(self,nbytes):
            nbytetwo = []
            print 'in recv'        
            bytesreceived = 0     # fill in your code here
            while bytesreceived < MSGLEN:
                nbytetwo = self.sock.recv( min(MSGLEN - bytesreceived, 2048) )
                if nbytetwo =='':
                    raise RuntimeError("socket connection broke down");
                nbytetwo.append(nbytetwo)
                bytesreceived = bytesreceived + len(nbytetwo)
            return bytesreceived ### sending back ack


        


