import time
from PSClient import PSClient

host="127.0.0.1"
port=5683
client = PSClient(server=(host, port))
#client.discovery()


#time.sleep(1)
#client.create("","topic",0)
#time.sleep(1)
client.create("","topic2",0)
#time.sleep(1)
client.subscribe("topic")
#time.sleep(1)
client.subscribe("topic2")

#client.publish("/topic","{'val':5}")

#time.sleep(1)
client.unsubscribe("topic")

#client.create("/topic3","topic4",0)

#response = client.get("/ps/topic") #implement here
#print(response.pretty_print())


#client.stop()
