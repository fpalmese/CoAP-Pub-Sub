import os,sys
from coapthon.server.coap import CoAP
from TopicResource import TopicResource



class CoAPBroker(CoAP):
	"""
	Class for the broker extending the CoAPthon server class.
	"""
	def __init__(self, host, port,qos=0):
		CoAP.__init__(self, (host, port),qos)
		root_res = TopicResource("/ps",self)
		root_res.content_type=40
		root_res.allow_children=True
		self.add_resource('/ps', root_res)

def main():
	print("Starting Broker...")
	broker = CoAPBroker("::", 5683)
	try:
		broker.listen(10)
	except KeyboardInterrupt:
		print ("Stopping Broker...")
		broker.close()

if __name__ == '__main__':
	main()
	
