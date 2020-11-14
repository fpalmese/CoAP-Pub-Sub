from coapthon.server.coap import CoAP
from PsResource import PsResource
import sys,os

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
		root_res.children.append(topic_res)
		self.add_resource('/ps/topic',topic_res)

def main():
	print("Starting Broker...")
	sys.stdout.flush()    
	broker = CoAPBroker("::", 5683)
	pid = os.getpid()
	f = open("/home/fabio/Scrivania/COAP PUB-SUB/csv/pid.txt","w")
	f.write(str(pid))
	f.close()
	try:
		broker.listen(10)
	except KeyboardInterrupt:
		print ("Stopping Broker...")
		broker.close()

if __name__ == '__main__':
	main()
	
