from coapthon.client.helperclient import HelperClient
from coapthon.defines import Codes
import time,sys


"""
    Class that extends the coapthon HelperClient 
    and allows to create a Publish-Subscribe CoAP client.
"""

class PSClient(HelperClient):

	def __init__(self,server,name="PsClient",qos=0):
		super(PSClient,self).__init__(server)
		self.name = name
		self.no_response = True if qos==0 else False
		print("[CLIENT "+self.name+"] Starting client...")
		
	#DISCOVERY with the DISCOVER method (a GET to ./well-known/core)
	#If uri is specified it will contains the path and the query ( example uri="/ps/topic?ct=0")
	def discovery(self,uri=None,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending DISCOVERY")
		#response=self.get("/.well-known/core")	
		if uri is None:
			response = self.discover(**kwargs)
		else:
			response = self.get(uri,**kwargs)	
		topicList=self.parseDiscovery(response)
		if response is not None:
			print("[CLIENT "+self.name+"]")
			print ("Received response for DISCOVERY:\nTopic List: "+str(topicList)+"\n")
		else:
			pass
		print("------------------------")

	#CREATE method handled on POST			#args are for the topic, kwargs are for the request (example max-age)
	def create(self,path,topicName,*args,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending CREATE for "+path+"/"+topicName)
		#payload ="<"+topicName+">;ct="+str(topicCT)
		payload ="<"+topicName+">"
		for arg in args:
			payload = payload+";"+str(arg)
		print("payload:"+payload)
		
		response = self.post(path,payload,no_response=self.no_response,**kwargs)
		#print response.pretty_print()
		if response is not None and not self.no_response:
			self.printResponse(response)
		else:
			pass	
		print("------------------------")

	#PUBLISH method handled on put (may be done on post too, depends on broker)
	def publish(self,topic,payload,**kwargs):
		print("[CLIENT "+self.name+"]")
		sndtime = time.time()
		print("Sending PUBLISH on "+topic+ ": "+payload+ " at time: "+str(sndtime))

		response = self.put(topic, payload,no_response=self.no_response,**kwargs)
		#print(response.pretty_print())
		if not self.no_response:
			self.printResponse(response)
		print("------------------------")
	#function that handles the callback for subscription responses
	def subCallback(self,message):
		rcvtime = time.time()
		if message is not None:
			sys.stdout.flush()
			print("[CLIENT "+self.name+"]")
			print("Received message for subscription:\nCode: "+Codes.LIST[message.code].name+"\nPayload: "+str(message.payload)+" Time: "+str(rcvtime))
			if message.code == Codes.NOT_FOUND.number:
				topic = message.payload.split(" ")[0]
				try:
					self.subThreads[topic].stopit()
					del self.subThreads[topic]
				except KeyError:
					return

		else:
			return
		print("------------------------")
		return

	def readCallback(self,message):
		if message is not None:
			sys.stdout.flush()
			print("[CLIENT "+self.name+"]")
			print("Received message from past READ:\nCode: "+Codes.LIST[message.code].name+"\nPayload: "+str(message.payload))
		print("------------------------")
		return

	#SUBSCRIBE handled on OBSERVE (GET with observe = 0)
	def subscribe(self,topic,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending SUBSCRIBE to "+topic)
		response = self.observe(topic,self.subCallback,**kwargs)
	
	#UNSUBSCRIBE handled on REMOVE_OBSERVE (GET with observe = 1)
	def unsubscribe(self,topic):
		print("[CLIENT "+self.name+"]")
		print("Sending UNSUBSCRIBE to "+topic)
		if topic not in self.subThreads:
			print("Cannot send unsubscribe to a not subscribed resource")
			print("--------------------------")
			return
		#self.subThreads[topic].stopit()
		response = self.remove_observe(topic)
	
	def read(self,topic,blocking=True,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending READ to "+topic)
		if topic is not None:
			if blocking:
				response = self.get(topic,self.readCallback,**kwargs)
			else:
				response = self.get(topic,**kwargs)
				self.printResponse(response)
		print("---------------------")

	def remove(self,topic,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending REMOVE to "+topic)
		if topic is not None:
			response = self.delete(topic,**kwargs)
			self.printResponse(response)
		print("--------------------")

	#function to parse the response to discovery (take topic list)
	def parseDiscovery(self,response):
		topicList=str(response.payload).split(",")
		topicList.pop()
		return topicList

	#function for simple print of response code and payload
	def printResponse(self,response):
		try:
			sys.stdout.flush()
			print("[CLIENT "+self.name+"]")
			print("Received Response: \n Code: "+Codes.LIST[response.code].name+"\nPayload: "+str(response.payload))
		except:
			pass

	#function to stop the client
	#sleep: if i have to wait some time before stopping
	#killThread if i have to wait for subthreads or just stop
	def stop(self,sleep=None,killThreads=False):
		if sleep is not None:
			time.sleep(sleep)
		if(killThreads):
			for t in list(self.subThreads):
				self.subThreads[t].stopit()
				del self.subThreads[t]
			for t in list(self.readThreads):
				self.readThreads[t].stopit()
				del self.readThreads[t]

		while(len(self.subThreads)>0 or len(self.readThreads)>0):
			pass
		
		print("[CLIENT "+self.name+"] Stopping client...")
		HelperClient.stop(self)

