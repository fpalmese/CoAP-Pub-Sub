import time,os,threading,sys
from PSClient import PSClient

host="127.0.0.1"
port=5683
#for test use: qos=0 and no_response=26 (true)
#	or     qos=1 and no_response=0 (false)
#	note that with qos=1 and callback in the publish the request is non-blocking(will go on without waiting for response)
def main(numVal,interval):
	client = PSClient(server=(host, port),name="pub",qos=1,no_response = 0)
	for i in range (0,numVal):
		client.publish("/ps/topic",str(time.time()))
		time.sleep(interval)
	client.stop(1)

if __name__=='__main__':
	if(len(sys.argv)!=3):
		interval=0.1
		numVal=100
	else:
		numVal=int(sys.argv[1])
		interval=float(sys.argv[2])
	main(numVal,interval)
