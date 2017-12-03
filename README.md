# vdtp
Vehicular data transport protocol for communication information over road side units (RSUs)

# Install paho and CoAP library (install pip first)
sudo pip install paho-mqtt
sudo pip install CoAPthon

# Server and client commands
server: sudo python server_perf <mqtt or coap or vdtp> <localIP-192.168.1.75>
client: sudo python client_perf <server_ip-192.168.1.75> <mqtt or coap or vdtp>
