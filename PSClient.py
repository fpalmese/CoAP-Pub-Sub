from coapthon.client.helperclient import HelperClient
from coapthon.defines import Codes
import time,sys


"""
    Class that extends the coapthon HelperClient 
    and allows to create a Publish-Subscribe CoAP client.
"""

class PSClient(HelperClient):

	def __init__(self,server,name="PsClient",qos=1,no_response = 0):
		super(PSClient,self).__init__(server,qos)
		self.name = name
		self.no_response = no_response
		print("[CLIENT "+self.name+"] Starting client...")
		
	#DISCOVERY with the DISCOVER method (a GET to ./well-known/core)
	#If uri is specified it will contains the path and the query ( example uri="/ps/topic?ct=0")
	def discovery(self,uri=None,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending DISCOVERY")
		if self.qos==0:
			callback = self.responseCallback
		else:
			callback = None
		if uri is None:
			response = self.discover(callback=callback,**kwargs)
		else:
			if self.qos==0:
				response = self.get_non(uri,callback = callback,**kwargs)
			else:
				response = self.get(uri,callback = callback,**kwargs)
		if callback is None:
			if response is not None:
				topicList=self.parseDiscovery(response)
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
		
		if self.qos == 0:
			callback = self.responseCallback
		else:
			callback = None
		response = self.post(path,payload,callback = callback,no_response = no_response,**kwargs)
		#print response.pretty_print()
		if response is not None and callback is None:
			self.printResponse(response)
		else:
			pass	
		print("------------------------")

	#PUBLISH method handled on put (may be done on post too, depends on broker)
	def publish(self,topic,payload,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending PUBLISH on "+topic+ ": "+payload)
		
		if self.qos == 0:
			callback = self.responseCallback
		else:
			#comment if you want that also a qos=1 request is sent without blocking the client
			#callback = None
			callback = self.responseCallback
		response = self.put(topic, payload,callback = callback,no_response = self.no_response,**kwargs)
		timeStamp=time.time()
		#print(response.pretty_print())
		if response is not None and callback is None:

			#lines to print in the file
			f = open("csv/"+self.name+".csv","a")
			f.write(payload+";"+str(timeStamp)+"\n")
			f.close()
			self.printResponse(response)
		print("------------------------")

	#function that handles the callback for subscription responses
	def subCallback(self,message):
		rcvtime = time.time()
		if message is not None:
			sys.stdout.flush()
			print("[CLIENT "+self.name+"]")
			print("Received message for subscription:\nCode: "+Codes.LIST[message.code].name+"\nPayload: "+str(message.payload)+"\nTime: "+str(rcvtime))
			"""
			if message.code == Codes.NOT_FOUND.number:
				topic = message.payload.split(" ")[0]
				try:
					self.subThreads[topic].stopit()
					del self.subThreads[topic]
				except KeyError:
					return
			"""
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

	def responseCallback(self,response):
		timeStamp = time.time()
		if response is not None:
			sys.stdout.flush()			
			try:
				f = open("csv/"+self.name+".csv","a")
				print("[CLIENT "+self.name+"]")
				print("Received message from server:\nTopic: /"+response.uri_path+"\nCode: "+Codes.LIST[response.code].name+"\nPayload: "+str(response.payload)+"\nTime:"+str(timeStamp))
				#lines to print in the file
				f.write(str(response.payload)+";"+str(timeStamp)+"\n")
				f.close()
				print("------------------------")
			except:
				pass
		return

	#SUBSCRIBE handled on OBSERVE (GET with observe = 0)
	def subscribe(self,topic,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending SUBSCRIBE to "+topic)
		f = open("csv/"+self.name+".csv","a")
		f.write("SUB;"+str(time.time())+"\n")
		f.close()
		response = self.observe(topic,self.responseCallback,**kwargs)
		return
	
	#UNSUBSCRIBE handled on REMOVE_OBSERVE (GET with observe = 1)
	def unsubscribe(self,topic):
		print("[CLIENT "+self.name+"]")
		print("Sending UNSUBSCRIBE to "+topic)
		"""
		if topic not in self.subThreads:
			print("Cannot send unsubscribe to a not subscribed resource")
			print("--------------------------")
			return
		#self.subThreads[topic].stopit()
		"""
		response = self.remove_observe(topic)
		if response is not None:
			self.printResponse(response)
	
	def read(self,topic,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending READ to "+topic)
		if topic is not None:
			if self.qos==0:
				response = self.get_non(topic,self.responseCallback,**kwargs)
			else:
				response = self.get(topic,self.responseCallback,**kwargs)
			self.printResponse(response)
		print("---------------------")

	def remove(self,topic,**kwargs):
		print("[CLIENT "+self.name+"]")
		print("Sending REMOVE to "+topic)
		if topic is not None:
			if self.qos == 0:
				callback = self.responseCallback
			else:
				callback = None
			response = self.delete(topic,callback,no_response=self.no_response,**kwargs)
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

