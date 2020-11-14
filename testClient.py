import time,os,threading,psutil
from Client.PSClient import PSClient

host="127.0.0.1"
port=5683

client = PSClient(server=(host, port),name="Sub1")
#time.sleep(2)

client.create("ps","topic2",ct=40,i_f="temperature")
time.sleep(2)
print("\n\n")
client.publish("ps/topic2/topic4","value=1",qos=1,no_response=0)
time.sleep(2)
print("\n\n")
client.subscribe("ps/topic2",qos=1)
time.sleep(2)
print("\n\n")
client.unsubscribe("ps/topic2",qos=1)
time.sleep(2)
print("\n\n")
client.remove("ps/topic2",qos=1,no_response=0)
time.sleep(2)
print("\n\n")
client.read("ps/topic2",qos=1)

pid = os.getpid()


"""
attr= {}
attr["max_age"]=10
client.create("/ps","topic4",0,**attr)
"""

client.stop(1)
