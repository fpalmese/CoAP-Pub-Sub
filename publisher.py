import time,os,threading,sys
from PSClient import PSClient

host="127.0.0.1"
port=5683

def main(numVal,interval):
	client = PSClient(server=(host, port),name="Publisher")
	for i in range (0,numVal):
		client.publish("/ps/topic",'val:'+str(i+1))
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
