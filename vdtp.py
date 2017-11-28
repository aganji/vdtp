# Client module
import socket
import pickle
from random import *
import struct
import threading
import time

# Required functions
# Send_packet
# Receive_packet
# Construct_packet

# Packet Type   - 2 bits
# flowId        - 6 bits
# seq           - 6 bits
# reliable      - 1 bits
# lastFrag      - 1 bit
# data          - 1450 bytes (max)

# Fragment Data into chunks of 1000 bytes
def fragmentData(serialData,reliable):
    FRAG_SIZE = 1450
    flowId = randint(1,63)
    print 'Flow Id:',flowId
    retBuf = []
    if len(serialData) > FRAG_SIZE:
        #print "Fragmenting Data"
        current = 0
        seq = 0
        lastFrag = 0
        while current < len(serialData):
            if current + FRAG_SIZE > len(serialData):
                lastFrag = 1
            if seq > 63:
                seq = 0
            #print seq,lastFrag
            seqHdr = (seq<<2) + (reliable << 1) + lastFrag
            #print seqHdr
            header = struct.pack('BB',flowId,seqHdr)
            retBuf.append(header + serialData[current:current+FRAG_SIZE])
            current += FRAG_SIZE
            seq += 1
    else:
        header = struct.pack('BB',flowId,(reliable << 1) + 1)
        #print len(header)
        retBuf.append(header + serialData)

    return retBuf

def ackThread(fragDataList,sk,addr):
    #print 'Ack thread created'
    totalPackets = len(fragDataList)
    lastCompleteAck = -1
    count = 0
    sk.settimeout(2)
    timeoutVal = 0
    while True:
        try:
            ackPacket, retAddr = sk.recvfrom(2)

            if retAddr == addr:
                flowId = struct.unpack('B',ackPacket[0])
                flowId = flowId[0]

                seqHdr = struct.unpack('B',ackPacket[1])
                seqHdr = seqHdr[0]

                seq = (seqHdr >> 2)
                if seq > lastCompleteAck:
                    lastCompleteAck = seq
                print 'Received ACK: {}'.format(lastCompleteAck)
                if seq == totalPackets-1:
                    break
                count += 1
        except socket.timeout:
            if timeoutVal > 2:
                break
            print 'Timeout Occured'
            timeoutVal += 1
            for x in range(lastCompleteAck+1,totalPackets):
                sk.sendto(fragDataList[x],addr)


def send(data,addr,reliable=0):
    serialData = pickle.dumps(data)
    #print 'Original Data Length:',len(serialData)

    # Fragment application layer packet to 1000 byte chunks
    fragDataList = fragmentData(serialData,reliable)

    # Attach header to individual messages
    # Send individual messages
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    # Create ackThread for reliability
    if reliable == 1:
        t = threading.Thread(target=ackThread,args=(fragDataList,sk,addr))
        t.start()
        #t.setDaemon(True)

    for item in fragDataList:
        #print 'Item Length:',len(item)
        sk.sendto(item,addr)

def extractHeader(hdr):

    flowId = struct.unpack('B',hdr[0])
    flowId = flowId[0]

    seqHdr = struct.unpack('B',hdr[1])
    seqHdr = seqHdr[0]
    lastFrag = seqHdr & 1
    reliable = (seqHdr >> 1) & 1
    seq = (seqHdr >> 2) & 63

    return flowId,int(seq),reliable,lastFrag

def sendAck(flowId,seq,addr,sk):
    ackPacket = struct.pack('BB',(2 << 6)+flowId,(seq << 2))
    #print 'Sending Ack to', flowId,seq,addr
    sk.sendto(ackPacket,addr)

class Server:
    def __init__(self):
        self.on_recv = None

    def start_serving(self,localAddr):
        sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        ackSk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sk.bind(localAddr)
        output = ''
        flowIdList = {}
        ackCount = {}
        completedFlows = []
        while True:
            data,addr = sk.recvfrom(1500)
            flowId,seq,reliable,lastFrag = extractHeader(data[0:2])
            if ackCount.has_key((addr,flowId)):
                ackCount[(addr,flowId)] += 1
            else:
                ackCount[(addr,flowId)] = 1
            length = len(data)

            # Send back ack
            if ackCount[(addr,flowId)]%2 == 0 or lastFrag == 1:
                sendAck(flowId,seq,addr,sk)

            if (addr,flowId) in completedFlows:
                print 'in completed flow'
                continue

            # In order delivery
            if flowIdList.has_key((addr,flowId)):
                flowIdList[(addr,flowId)][seq] = data[2:length]
            else:
                flowIdList[(addr,flowId)] = {}
                flowIdList[(addr,flowId)][seq] = data[2:length]

            if lastFrag == 1:
                for x in range(0,64):
                    if flowIdList[(addr,flowId)].has_key(x):
                        output += flowIdList[(addr,flowId)][x]
                    else:
                        del flowIdList[(addr,flowId)]
                        del ackCount[(addr,flowId)]
                        completedFlows.append((addr,flowId))
                        break
                returnBuf = pickle.loads(output)
                output = ''
                if self.on_recv:
                    self.on_recv(returnBuf,(addr,flowId))
