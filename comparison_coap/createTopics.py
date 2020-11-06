import time,os,threading,psutil

from PSClient import PSClient

host="127.0.0.1"
port=5683
client = PSClient(server=(host, port),name="pub",qos=0,no_response=26)

for i in range(1,101):
	client.create("/ps","topic"+str(i),"ct=0")




client.stop(1)
