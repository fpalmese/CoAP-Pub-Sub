import time,sys,threading,os,psutil
from PSClient import PSClient

host="127.0.0.1"
port=5683
clients = []

def main(numSubs=10):
	try:
		for i in range(0,numSubs):
			client = PSClient(server=(host, port), name="sub"+str(i+1))
			client.subscribe("/ps/topic")
			clients.append(client)
			time.sleep(0.03)

	except KeyboardInterrupt:
		print("SHUTTING DOWN")
		print(len(clients))
		for c in clients:
			sys.stdout.flush()
			c.stop(2,True)
		sys.stdout.flush()
		sys.exit()

if __name__=="__main__":
	if(len(sys.argv)!=2):
		print("Error! Usage: python3 subscribers.py numSubscribers")
		sys.exit(0)
	main(int(sys.argv[1]))
