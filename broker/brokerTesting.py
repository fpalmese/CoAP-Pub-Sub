from coapthon.server.coap import CoAP
from TopicResource import TopicResource
import sys,os

"""
    Main server class for the Broker application
"""
class CoAPBroker(CoAP):
	def __init__(self, host, port,qos=0):
		CoAP.__init__(self, (host, port),qos)
		# Add the first base API ps/ resource
		root_res = TopicResource("/ps",self)
		root_res.allow_children=True
		self.add_resource('/ps', root_res)
		#lines to add /ps/topic
		topic_res=TopicResource("/ps/topic",self)
		topic_res.payload = "A"
		topic_res.parent = root_res
		root_res.children.append(topic_res)
		self.add_resource('/ps/topic',topic_res)

	def start(self):
		self.listen(timeout=10)

	def stop(self):
		self.stop()

def main():
	print("Starting Broker...")
	sys.stdout.flush()    
	broker = CoAPBroker("::", 5683)
	pid = os.getpid()
	f = open("/home/fabio/Scrivania/COAP PUB-SUB/csv/pid.txt","w")
	f.write(str(pid))
	f.close()
	try:
		broker.start()
	except KeyboardInterrupt:
		print ("Stopping Broker...")
		broker.stop()

if __name__ == '__main__':
	main()
	
