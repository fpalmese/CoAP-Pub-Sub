from coapthon.server.coap import CoAP
from PsResource import PsResource
import sys

"""
    Main server class for the Broker application
"""
class CoAPBroker(CoAP):
	def __init__(self, host, port,qos=0):
		CoAP.__init__(self, (host, port),qos)
		# Add the first base API ps/ resource
		root_res = PsResource("/ps",self)
		root_res.attributes["ct"] = 40
		root_res.allow_children=True
		self.add_resource('/ps', root_res)
		#line to have the "/ps/topic" always ready
		topic_res=PsResource("/ps/topic",self)
		topic_res.payload = "A"
		topic_res.parent = root_res
		self.add_resource('/ps/topic',topic_res)

def main():
	print("[BROKER] Starting Broker")
	sys.stdout.flush()    
	server = CoAPBroker("::", 5683)
	try:
		server.listen(10)
	except KeyboardInterrupt:
		print ("[BROKER] Broker Shutdown")
		server.close()
		print ("Exiting...")

if __name__ == '__main__':
	main()
	
