import queue
import struct
import threading
import time
import sys,os
import socket
sys.path.append('c:/python34/steve/mqttsclient/')
from MQTTSNclient import Callback
from MQTTSNclient import Client
from MQTTSNclient import publish
import MQTTSN

numVal = 50
interval = 0.25
#client = Client("linh_pub")#change so only needs name
def main(loss):
    os.system("sudo tc qdisc add dev lo root netem loss "+loss+"%")
    for i in range(0,numVal):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('',12345))
        publish(1,str(time.time()),port=1885,host="127.0.0.1",sock = sock)
        time.sleep(interval)
        sock.close()

if __name__=="__main__":
    if len(sys.argv)!= 2:
        loss = 0
    else: 
        loss = sys.argv[1]
    main(loss)
