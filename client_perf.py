import paho.mqtt.publish as publish
import sys
from coapthon.client.helperclient import HelperClient
import vdtp

ptl = sys.argv[2]
ip_address = sys.argv[1] #broker
payload = 'Happy'

def sendCoap(client,path,payload):
	response = client.post(path,payload,timeout=30)
	client.stop()
	print 'COAP sent'
	return

if ptl == 'mqtt':
	try:		
		publish.single('perf_test',payload,hostname=ip_address)
		print 'Sent'
	except:
		print 'Fail'

if ptl == 'coap':
	client = HelperClient(server=(ip_address, 5683))
	path = 'Basic'
	sendCoap(client,path,payload)

if ptl == 'vdtp':
	port=5050
	vdtp.send(payload,(ip_address,port),1)