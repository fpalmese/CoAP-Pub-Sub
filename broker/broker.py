import os,sys
from coapthon.server.coap import CoAP
from TopicResource import TopicResource



class CoAPBroker(CoAP):
	"""
	Class for the broker extending the CoAPthon server class.
	To run the broker, instantiate and call the start method.

	"""
	def __init__(self, host, port,qos=0):
		CoAP.__init__(self, (host, port),qos)
		root_res = TopicResource("/ps",self)
		root_res.content_type=40
		root_res.allow_children=True
		self.add_resource('/ps', root_res)

	def start(self):
		self.listen(timeout=10)

	def stop(self):
		self.close()

def main():
	broker = CoAPBroker("::", 5683,qos=0)
	try:
		print("Starting Broker...")
		broker.start()
	except KeyboardInterrupt:
		print ("Stopping Broker...")
		broker.stop()

if __name__ == '__main__':
	main()
	
