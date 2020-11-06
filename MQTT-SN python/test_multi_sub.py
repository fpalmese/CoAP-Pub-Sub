import queue
import struct
import threading
import time
import sys
import os
import psutil

sys.path.append('c:/python34/steve/mqttsclient/')
print(sys.version_info)

from MQTTSNclient import Callback
from MQTTSNclient import Client
from MQTTSNclient import publish
import MQTTSN
message_q=queue.Queue()

class MyCallback(Callback):
  def __init__(self,msg_queue):
    super(MyCallback,self).__init__()
    self.message_q=msg_queue
  def messageArrived(self,client,TopicId, payload, qos, retained, msgid):
    m= "d-p-Arrived" +" topic  " +str(TopicId)+ "message " +\
       str(payload) +"  qos= " +str(qos) +" ret= " +str(retained)\
       +"  msgid= " + str(msgid)
    #print("got the message ",payload)
    timeStamp = time.time()
    self.message_q.put(payload)
    f=open("csv/"+client.clientid+".csv","a")
    f.write(payload+";"+str(timeStamp)+"\n")
    f.close()
    return True

######
def empty_queue(clientid,msg_queue,delay=0):
    while not msg_queue.empty():
      m=msg_queue.get()
      print("Client "+str(clientid)+" received message "+m+" ")#at time "+str(time.time()))
    if delay!=0:
      time.sleep(delay)
########

clients = []
host="127.0.0.1"
port=1885
topic1="/ps/topic"

def sub(client,msg_queue):
	client.message_arrived_flag=False
	client.registerCallback(MyCallback(msg_queue))
	clients.append(client)
	client.connected_flag=False
	while(True):
		client.connect(host,port,100)
		client.lookfor(MQTTSN.CONNACK)
		try:
			connack = client.waitfor(MQTTSN.CONNACK)
			if connack==None:
				print("[Client "+client.clientid+"] connection failed")
			else:
				break
			time.sleep(0.01)
		except:
			print("connection failed")
			raise SystemExit("no Connection quitting")
	
	client.loop_start() #start loop
	client.subscribed_flag=False
	while True:
		f = open("csv/"+client.clientid+".csv","a")
		f.write("SUB;"+str(time.time())+"\n")
		f.close()
		rc, topic1_id = client.subscribe(topic1,qos=0) #topic normal name ("/ps/topic")
		#rc, topic1_id = client.subscribe(1,qos=0)	#predefined topic with id 1
		#rc, topic1_id = client.subscribe("ps",qos=0)	#topic short-name with name "ps"
		subackTime = time.time()
		if rc==None:
			print("[Client "+client.clientid+"] subscribe failed")
			time.sleep(0.01)
		if rc==0:
			f = open("csv/"+client.clientid+".csv","a")
			f.write("SUBACK;"+str(subackTime)+"\n")
			f.close()
			print("[Client "+client.clientid+"] subscribed ok to ",topic1,"time : "+str(time.time()))
			break
		else:
			print("Error: return code-> ",rc)
			time.sleep(2)
	#client.unsubscribe(topic1_id)
	print("TOPICID: "+str(topic1_id))
	while(True):	
		#client.publish(topic1_id,"1",qos=0)
		empty_queue(client.clientid,msg_queue,0)
		time.sleep(0.000000001)
pid = os.getpid()

def trackOS(pid):
	while(True):
		py = psutil.Process(pid)
		cpu = py.cpu_percent()
		mem = py.memory_percent()
		for child in py.children():
			cpu = cpu+child.cpu_percent()
			mem = mem+child.memory_percent()
		print('cpu use:', cpu*1000)
		print('memory use:',mem)
		time.sleep(1)

def main(numSubs):
	for i in range(0,numSubs):
		client = Client("sub"+str(i+1))#change so only needs name
		msg_queue =queue.Queue()
		clients.append(client)
		thread = threading.Thread(target=sub, args=(client, msg_queue))
		thread.start()
		time.sleep(0.05)
#trackOS(pid)

if __name__=='__main__':
	try:
		numSubs = int(sys.argv[1])
	except: 
		numSubs = 1
	main(numSubs)








