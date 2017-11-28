import socket
import pickle
import struct
import vdtp

LOCAL_IP = '127.0.0.1'
LOCAL_PORT = 5050

def on_recv(retBuf,addrTuple):
    print retBuf['d'],addrTuple

serverApp = vdtp.Server()
serverApp.on_recv = on_recv
serverApp.start_serving((LOCAL_IP,LOCAL_PORT))

