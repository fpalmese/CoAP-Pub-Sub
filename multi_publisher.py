import time,os,threading,sys
from PSClient import PSClient

host="127.0.0.1"
port=5683

numVal = 50
interval=0.25
#for test use: qos=0 and no_response=26 (true)
#	or     qos=1 and no_response=0 (false)
#	note that with qos=1 and callback in the publish the request is non-blocking(will go on without waiting for response)
def main(numClients):
	clients = []
	#start clients
	for i in range(0,numClients):
		#client = PSClient(server=(host,port),name="pub"+str(i+1),qos=0,no_response=26)
		client = PSClient(server=(host,port),name="pub"+str(i+1),qos=1,no_response=0)
		clients.append(client)

	#publish numVal values on same topic
	for i in range (0,numVal):
		clients[i%numClients].publish("/ps/topic",str(time.time()))
		time.sleep(interval)

	time.sleep(30)
	
	#stop clients
	for c in clients:
		c.stop(0)

if __name__=='__main__':
	if(len(sys.argv)!=2):
		numClients = 1
	else:
		numClients = int(sys.argv[1])
	main(numClients)
