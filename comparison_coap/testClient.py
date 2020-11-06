import time,os,threading,sys

from PSClient import PSClient

host="127.0.0.1"
port=5683
client = PSClient(server=(host, port),name="pub",qos=1,no_response=0)
if(len(sys.argv)!=2):
	notexisting = 0
else:
	notexisting = int(sys.argv[1])

topics =[]
for i in range(1,101-notexisting):
	topics.append("/ps/topic"+str(i))
	



for t in topics:
	client.publish(t,str(time.time()))
	time.sleep(0.05)

for i in range(0,notexisting):
	timeStamp = time.time()
	client.create("/ps","topic"+str(101+i),"ct=0")
	client.publish("/ps/topic"+str(101+i),str(timeStamp))
	time.sleep(0.05)


client.stop(1)
