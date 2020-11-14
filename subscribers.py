import time,sys,threading,os,psutil
from Client.PSClient import PSClient

host="127.0.0.1"
port=5683
clients = []

def main(numSubs=10):
	for i in range(0,numSubs):
		client = PSClient(server=(host, port), name="sub"+str(i+1))
		client.subscribe("/ps/topic")
		clients.append(client)
		time.sleep(0.03)

if __name__=="__main__":
	if(len(sys.argv)!=2):
		print("Error! Usage: python3 subscribers.py numSubscribers")
		sys.exit(0)
	main(int(sys.argv[1]))
