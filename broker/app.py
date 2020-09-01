from coapthon.server.coap import CoAP
from PsResource import PsResource
import sys

"""
    Main server class for the Broker application
"""
class CoAPBroker(CoAP):
	def __init__(self, host, port):	
		CoAP.__init__(self, (host, port))
		# Add the first base API ps/ resource
		root_res = PsResource("/ps",self)
		root_res.attributes["ct"] = ["40"]
		self.add_resource('/ps', root_res)

def main():
	print("[BROKER] Starting Broker")
	sys.stdout.flush()    
	server = CoAPBroker("::", 5683)
	try:
		server.listen(10)
	except KeyboardInterrupt:
		print ("Server Shutdown")
		server.close()
		print ("Exiting...")

if __name__ == '__main__':
	main()
