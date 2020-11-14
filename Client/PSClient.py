from coapthon.client.helperclient import HelperClient
from coapthon.defines import Codes
import time,sys


"""
    Class that extends the coapthon HelperClient 
    and allows to create a Publish-Subscribe CoAP client.
"""

class PSClient(HelperClient):

	def __init__(self,server,name="PSClient"):
		super(PSClient,self).__init__(server)
		self.name = name
		print("[CLIENT "+self.name+"] Starting client...")
		
	#DISCOVERY with the DISCOVER method (a GET to ./well-known/core)
	#If uri is specified it will contains the path and the query ( example uri="/ps/topic?ct=0")
	def discovery(self,uri=None, qos=1, **kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending DISCOVERY")
		if uri is None:
			response = self.discover(callback=self.responseCallback,**kwargs)
		else:
			if qos==0:
				response = self.get_non(uri,callback = self.responseCallback,**kwargs)
			else:
				response = self.get(uri,callback = self.responseCallback,**kwargs)
		if response is not None:
				topicList=self.parseDiscovery(response)
				print("[CLIENT "+self.name+"]")
				print ("Received response for DISCOVERY:\nTopic List: "+str(topicList)+"\n")
		print("------------------------")

	#CREATE method handled on POST			#args are for the topic(example ct), kwargs are for the request (example max-age)
	def create(self,path,topicName,ct=0,rt=None,sz=None,i_f=None,qos=1, no_response=0,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending CREATE for "+path+"/"+topicName)
		payload ="<"+topicName+">;ct="+str(ct)
		if rt is not None:
			payload = payload+";rt="+rt
		if sz is not None:
			payload = payload+";sz="+str(sz)
		if i_f is not None:
			payload = payload+";if="+i_f
		print("payload:"+payload)

		response = self.post(path,payload,callback = self.responseCallback, qos = qos, no_response = no_response,**kwargs)
		#print response.pretty_print()
		if response is not None:
			self.printResponse(response)
		print("------------------------")

	#PUBLISH method handled on put (may be done on post too, depends on broker)
	def publish(self,topic,payload, qos=1, no_response=0, **kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending PUBLISH on "+str(topic)+ ": "+str(payload))

		response = self.put(str(topic),str(payload),callback = self.responseCallback, qos = qos, no_response = no_response,**kwargs)
		if response is not None and callback is None:
			self.printResponse(response)
		print("------------------------")

	#function that handles the callback for server messages
	def responseCallback(self,response):
		timeStamp = time.time()
		if response is not None:
			sys.stdout.flush()			
			try:
				print("[CLIENT "+self.name+"]")
				print("Received message from server:\nTopic: /"+response.uri_path+"\nCode: "+Codes.LIST[response.code].name+"\nPayload: "+str(response.payload)+"\nTime:"+str(timeStamp))
				print("------------------------")
			except:
				pass
		return

	#SUBSCRIBE handled on OBSERVE (GET with observe = 0)
	def subscribe(self, topic, qos=1, **kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending SUBSCRIBE to "+topic)
		self.observe(topic,self.responseCallback, qos=qos, **kwargs)
	
	#UNSUBSCRIBE handled on REMOVE_OBSERVE (GET with observe = 1)
	def unsubscribe(self, topic, qos=1, no_response=0, **kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending UNSUBSCRIBE to "+topic)
		response = self.remove_observe(topic,callback=self.responseCallback,qos=qos,no_response=no_response,**kwargs)
		if response is not None:
			self.printResponse(response)
	
	def read(self,topic, qos=1,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending READ to "+topic)
		if qos==0:
			response = self.get_non(topic,callback = self.responseCallback,**kwargs)
		else:
			response = self.get(topic,callback = self.responseCallback,**kwargs)
		if response is not None:
			self.printResponse(response)
		print("---------------------")

	def remove(self,topic, qos=1, no_response = 0,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending REMOVE to "+topic)
		response = self.delete(topic,callback=self.responseCallback, qos = qos, no_response = no_response,**kwargs)
		if response is not None:
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
			if response is not None:
				sys.stdout.flush()
				print("[CLIENT "+self.name+"]")
				print("Received Response: \n Code: "+Codes.LIST[response.code].name+"\nPayload: "+str(response.payload))
		except:
			pass

	#function to stop the client
	#sleep: if i have to wait some time before stopping
	#killThreads if i have to wait for subthreads or just stop(kill them)
	def stop(self,sleep=None,killThread=False):
		if sleep is not None:
			time.sleep(sleep)
		if(killThread):
			self.runningThread.stopit()
			#self.queue.put(None)
			#self.runningThread.join()
			self.runningThread = None	
		while(self.runningThread is not None):
			pass
		
		print("[CLIENT "+self.name+"] Stopping client...")
		HelperClient.stop(self)

