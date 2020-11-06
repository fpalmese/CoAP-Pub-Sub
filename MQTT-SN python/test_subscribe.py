import queue
import struct
import threading
import time
import sys
sys.path.append('c:/python34/steve/mqttsclient/')
print(sys.version_info)

from MQTTSNclient import Callback
from MQTTSNclient import Client
from MQTTSNclient import publish
import MQTTSN
message_q=queue.Queue()

class MyCallback(Callback):
  def messageArrived(self,client,TopicId, payload, qos, retained, msgid):
    m= "d-p-Arrived" +" topic  " +str(TopicId)+ "message " +\
       str(payload) +"  qos= " +str(qos) +" ret= " +str(retained)\
       +"  msgid= " + str(msgid)
    #print("got the message ",payload)
    message_q.put(payload)
    return True

######
def empty_queue(delay=0):
    while not message_q.empty():
      m=message_q.get()
      print("Received message "+m+" at time "+str(time.time()))
    if delay!=0:
      time.sleep(delay)
########

#if __name__ == "__main__":
host="127.0.0.1"
port=1885
#m_port=1885 #port gateways advertises on
#m_group="225.0.18.83" #IP gateways advertises on
clients = []

topic1="topic1"
client = Client("sub")#change so only needs name
client.message_arrived_flag=False
client.registerCallback(MyCallback())
clients.append(client)
client.connected_flag=False
client.connect(host,port)
client.lookfor(MQTTSN.CONNACK)
try:
	if client.waitfor(MQTTSN.CONNACK)==None:
		print("connection failed")
		raise SystemExit("no Connection quitting")
except:
	print("connection failed")
	raise SystemExit("no Connection quitting")
client.loop_start() #start loop
client.subscribed_flag=False
while True:
	rc, topic1_id = client.subscribe(topic1,0)
	if rc==None:
		print("subscribe failed")
		raise SystemExit("Subscription failed quitting")
	if rc==0:
		print("subscribed ok to ",topic1)
		break
print("TOPICID: "+str(topic1_id))
while(True):	
	#client.publish(topic1_id,"1",qos=0)
	empty_queue(0)
	time.sleep(1)

