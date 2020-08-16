from coapthon.client.helperclient import HelperClient
from coapthon.defines import Codes
from coapthon.utils import generate_random_token
from utils import generate_subscribe_token
host = "127.0.0.1"
port = 5683



class PSClient(HelperClient):
	psPath="/ps"
	observed_list = {}
	#DISCOVERY with the DISCOVER method (a GET to ./well-known/core)
	def discovery(self):
		print("sending DISCOVERY")
		#response=self.get("/.well-known/core")	
		response = self.discover()		
		topicList=self.parseDiscover(response)
		if response is not None:
			print ("received response for DISCOVERY:\nTopic List: "+str(topicList)+"\nPS: "+self.psPath)
		else:
			print("received empty response")
		print("------------------------")

	#CREATE method handled on POST
	def create(self,path,topicName,topicCT):
		print("sending CREATE for "+self.psPath+path+"/"+topicName)
		payload ="<"+topicName+">;ct="+str(topicCT)+";"
		response = self.post("/ps"+path,payload)
		#print response.pretty_print()
		if response is not None:
			self.printResponse(response)
		else:
			print("received empty response")	
		print("------------------------")

	#PUBLISH method handled on put (may be done on post too, depends on broker)
	def publish(self,topic,payload,method="PUT"):
		print("PUBLISH on "+topic+ ": "+payload)
		
		if(method.lower()=="post"):
			response = self.post(self.psPath+topic, payload)
			
		else:
			response = self.put(self.psPath+topic, payload)
		#print(response.pretty_print())
		self.printResponse(response)
		print("------------------------")
	#function that handles the callback for subscription responses
	def subCallback(self,message):
		if message is not None:
			print("Received message for subscription:\nCode: "+Codes.LIST[message.code].name+"\nPayload: "+str(message.payload))
		else:
			print("Received empty message")
		print("------------------------")

	#SUBSCRIBE handled on OBSERVE (GET with observe = 0)
	def subscribe(self,topic):
		print("SUBSCRIBE to "+ topic)
		tkn_size = 4	#token size in bytes
		token = generate_subscribe_token(topic,tkn_size)
		response = self.observe(self.psPath+"/"+topic,self.subCallback,token)
		print("------------------------")
	
	#UNSUBSCRIBE handled on GET with observe = 1
	def unsubscribe(self,topic):
		print("UNSUBSCRIBE to "+ topic)
		tkn_size = 4 #token size in bytes
		token = generate_subscribe_token(topic,tkn_size)
		response = self.remove_observe(self.psPath+"/"+topic,token)
		self.printResponse(response)
		print("------------------------")

	#function to parse the response to discovery
	def parseDiscover(self,response):	#take topic list and update the ps
						#PROBLEM IN THIS FUNCTION HERE WHEN WE SET THE PSPATH
		topicList=str(response.payload).split(",")
		topicList.pop()
		for t in topicList:
			if("core.ps" in t):
				self.psPath=[s.split('>')[0] for s in t.split('<') if '>' in s][0]
		return topicList

	#function for simple print of response code and payload
	def printResponse(self,response):
		try:
			print("Received Response: \n Code: "+Codes.LIST[response.code].name+"\nPayload: "+response.payload)
		except:
			print("Received malformed response")

