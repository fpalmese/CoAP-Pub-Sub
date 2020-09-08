from coapthon.client.helperclient import HelperClient
from coapthon.defines import Codes
from coapthon.utils import generate_random_token
from utils import generate_subscribe_token
import time


"""
    Class that extends the coapthon HelperClient 
    and allows to create a Publish-Subscribe CoAP client.
"""

class PSClient(HelperClient):

	def __init__(self,server,name="PsClient"):
		super(PSClient,self).__init__(server)
		self.name = name
		print("[CLIENT "+self.name+"] Starting client...")

	#DISCOVERY with the DISCOVER method (a GET to ./well-known/core)
	def discovery(self):
		print("[CLIENT "+self.name+"]")
		print("Sending DISCOVERY")
		#response=self.get("/.well-known/core")	
		response = self.discover()		
		topicList=self.parseDiscovery(response)
		if response is not None:
			print("[CLIENT "+self.name+"]")
			print ("Received response for DISCOVERY:\nTopic List: "+str(topicList)+"\n")
		else:
			print("Received empty response")
		print("------------------------")

	#CREATE method handled on POST			#MODIFY THE ARGS TO VARYING 
	def create(self,path,topicName,topicCT=None,topicRT=None):
		print("[CLIENT "+self.name+"]")
		print("Sending CREATE for "+path+"/"+topicName)
		payload ="<"+topicName+">;"
		if topicCT is not None:
			payload = payload + "ct="+str(topicCT)+";"
		if topicRT is not None:
			payload = payload + "rt="+str(topicRT)+";"
		response = self.post(path,payload)
		#print response.pretty_print()
		if response is not None:
			self.printResponse(response)
		else:
			print("received empty response")	
		print("------------------------")

	#PUBLISH method handled on put (may be done on post too, depends on broker)
	def publish(self,topic,payload,method="PUT"):
		print("[CLIENT "+self.name+"]")
		print("Sending PUBLISH on "+topic+ ": "+payload)
		
		if(method.lower()=="post"):
			response = self.post(topic, payload)
			
		elif(method.lower()=="put"):
			response = self.put(topic, payload)
		#print(response.pretty_print())
		self.printResponse(response)
		print("------------------------")
	#function that handles the callback for subscription responses
	def subCallback(self,message):
		if message is not None:
			print("[CLIENT "+self.name+"]")
			print("Received message for subscription:\nCode: "+Codes.LIST[message.code].name+"\nPayload: "+str(message.payload))
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

	#SUBSCRIBE handled on OBSERVE (GET with observe = 0)
	def subscribe(self,topic):
		print("[CLIENT "+self.name+"]")
		print("Sending SUBSCRIBE to "+topic)
		tkn_size = 4	#token size in bytes
		token = generate_subscribe_token(self.name+topic,tkn_size)
		response = self.observe(topic,self.subCallback,token)
	
	#UNSUBSCRIBE handled on REMOVE_OBSERVE (GET with observe = 1)
	def unsubscribe(self,topic):
		print("[CLIENT "+self.name+"]")
		print("Sending UNSUBSCRIBE to "+topic)
		if topic not in self.subThreads:
			print("Cannot send unsubscribe to a not subscribed resource")
			print("--------------------------")
			return
		#self.subThreads[topic].stopit()	
		tkn_size = 4 #token size in bytes
		token = generate_subscribe_token(self.name+topic,tkn_size)
		response = self.remove_observe(topic,token)
	
	def read(self,topic):
		print("[CLIENT "+self.name+"]")
		print("Sending READ to "+topic)
		if topic is not None:
			response = self.get(topic)
			self.printResponse(response)
		print("---------------------")

	def remove(self,topic):
		print("[CLIENT "+self.name+"]")
		print("Sending REMOVE to "+topic)
		if topic is not None:
			response = self.delete(topic)
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
			print("[CLIENT "+self.name+"]")
			print("Received Response: \n Code: "+Codes.LIST[response.code].name+"\nPayload: "+str(response.payload))
		except:
			print("Received malformed response")

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
		while(len(self.subThreads)>0):
			pass
		
		print("[CLIENT "+self.name+"] Stopping client...")
		HelperClient.stop(self)

