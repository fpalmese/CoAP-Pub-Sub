"""
/*******************************************************************************
 * Copyright (c) 2011, 2013 IBM Corp.
 *
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * and Eclipse Distribution License v1.0 which accompany this distribution. 
 *
 * The Eclipse Public License is available at 
 *    http://www.eclipse.org/legal/epl-v10.html
 * and the Eclipse Distribution License is available at 
 *   http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * Contributors:
 *    Ian Craggs - initial API and implementation and/or initial documentation
 *******************************************************************************/
"""
#add by me
import queue
import struct
import threading
import time
import signal
import sys,os
sys.path.append('c:/python34/steve/mqttsclient/')
print(sys.version_info)
##

from MQTTSNclient import Callback
from MQTTSNclient import Client
from MQTTSNclient import publish
import MQTTSN
gateways=[]
def keyboardInterruptHandler(signal, frame):
	print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	exit(0)

class MyCallback(Callback):
	def advertise(self,client,address, gwid, duration):
		m="advertise -address" + str(address)+"qwid= " +str(gwid)+"dur= " +str(duration)
		print ("found gateway at",m)
		ip_address,port=address
		temp=[ip_address,port,str(gwid),str(duration)]
		gateways.append(temp)
		client.GatewayFound=True


########
signal.signal(signal.SIGINT, keyboardInterruptHandler)
print ("threads ",threading.activeCount()) 
#if __name__ == "__main__":
host="192.168.1.159"
port=1883
s_port=1885
s_group="224.0.18.83"
r_port=1885 #port gateways advertises on
r_group="225.0.18.83" #IP gateways advertises on
#r_port=1883 #port gateways advertises on
#r_group="225.1.1.1" #IP gateways advertises on


#PARAMETERS FOR THE PUBLISHES
host="127.0.0.1"
port=1885
numVal = 50
interval = 0.25
clients = []
qos = 1
topic1="/ps/topic"
queues = []
topic1_id = 1
waitQ = queue.Queue()

def thread_body(client):
	#connect
	while(True):
		client.connect(host,port,100)
		client.lookfor(MQTTSN.CONNACK)
		if client.waitfor(MQTTSN.CONNACK)==None:
			print("connection failed")
		else:
			break
		time.sleep(0.01)
	time.sleep(0.02)
	#register
	while(True):
		topic1_id=client.register(topic1)
		if topic1_id is None:
			print("Register not acked")
			continue
		else:
			print("Register OK")
			print("topic id:", topic1_id)
			waitQ.put(0)
			break



def main(numPubs,loss):
	print ("MULTI PUBLISHER")
	for i in range(0,numPubs):
		client = Client("pub"+str(i+1))#change so only needs name
		clients.append(client)
		client.registerCallback(MyCallback())
		client.connected_flag=False
		#CONNECT CLIENT
		thread=threading.Thread(target = thread_body,args = ([client]))
		thread.start()
		time.sleep(0.01)
	"""
		while(True):
			client.connect(host,port)
			client.lookfor(MQTTSN.CONNACK)
			if client.waitfor(MQTTSN.CONNACK)==None:
				print("connection failed")
			else:
				break
		#REGISTER TOPIC
		while(True):
			topic1_id=client.register(topic1)
			if topic1_id is None:
				print("Register not acked")
				continue
			else:
				print("Register OK")
				break
	"""
	for i in range (0,numPubs):
		waitQ.get()
	
	os.system("sudo tc qdisc add dev lo root netem loss "+loss+"%")

	for i in range(0,numVal):
		print("publishing message "+str(time.time())+" topic: "+str(topic1_id))
		if qos==0 or qos ==2:
			id= clients[i%numPubs].publish(topic1_id,str(time.time()),qos=qos)
		else:
			thread=threading.Thread(target = clients[i%numPubs].publish,args = (topic1_id,str(time.time()),qos))	
			#thread=threading.Thread(target = clients[i%numPubs].publish,args = ("ps",str(time.time()),qos))	
			thread.start()
		time.sleep(interval)
		
	time.sleep(5)
	"""
	for c in clients:
		while(True):
			res = c.disconnect()
			print(res)
			if res is None:
				print("lost disconnect ack")
				pass
			else:
				print("received disconnect ack")
				break
		time.sleep(0.25)
		c.stop()
	"""
	#for c in clients:
	#	c.stop()

if __name__=='__main__':
	if len(sys.argv) < 2:
		numPubs = 1
		loss = "0"
	else:
		numPubs = int(sys.argv[1])
		loss = sys.argv[2]
	main(numPubs,loss)



