import time,os,threading,psutil
from PSClient import PSClient

host="127.0.0.1"
port=5683
client = PSClient(server=(host, port),name="Sub1",qos=1)
client.subscribe("/ps/topic")
time.sleep(1)
client.unsubscribe("/ps/topic")
time.sleep(1)
client.publish("/ps/topic","val:3")
#time.sleep(2)
#client.read("/ps/topic2")


pid = os.getpid()


"""
attr= {}
attr["max_age"]=10
client.create("/ps","topic4",0,**attr)
"""

#client.create("/ps/topic5","topic6",40)
#time.sleep(1)
#client.create("/ps","topic2",0)
#time.sleep(1)


#time.sleep(2)
#client.unsubscribe("/ps/topic")
#time.sleep(2)

"""
for i in range (1,101):
	client.publish("/ps/topic",'{"val":'+str(i)+'}')
	time.sleep(0.3)
"""


#time.sleep(2)
#client.read("/ps/topic")
#time.sleep(2)
#client.subscribe("/ps/topic/topic2/topic3/topic4")
#time.sleep(2)
#client.remove("/ps/topic/topic2")
#client.create("/ps/topic3","topic4",0)

#response = client.get("/ps/topic") #implement here
#print(response.pretty_print())
client.stop(1)
