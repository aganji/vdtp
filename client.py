import vdtp

LOCAL_IP = '127.0.0.1'
LOCAL_PORT = 5050

# contruct packet (key-value pairs)
data = {'a':1,'b':2,'c':'String'}
data['d'] = 'abcdefghijklmnopqrstuvwxyz'
vdtp.send(data,(LOCAL_IP,LOCAL_PORT),1)

