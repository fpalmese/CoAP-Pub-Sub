import pyshark,sys
from pprint import pprint

coapSubs = []
coapPubs = []

subCap = pyshark.FileCapture("./captures/sub.cap")
print("Analizing sub.cap")
subSize = 0
subOverhead = 0
for pck in subCap:
	if "coap" in pck:
		#print(vars(pck.coap))
		coapSubs.append(pck)
		subSize+=len(pck)
		try:
			payload = int(pck.coap.payload_length)
		except:
			payload = 0
		subOverhead += (len(pck)-payload) 
		
subCap.close()
if(len(coapSubs)>0):
	subTime = float(coapSubs[len(coapSubs)-1].sniff_timestamp) - float(coapSubs[0].sniff_timestamp)

pubCap = pyshark.FileCapture("./captures/pub.cap")
print("Analizing pub.cap")
pubSize = 0
pubOverhead = 0
for pck in pubCap:
	if "coap" in pck:
		coapPubs.append(pck)
		pubSize+=len(pck)
		payload = int(pck.coap.payload_length)
		pubOverhead += (len(pck)-payload) 
		
subCap.close()
if(len(coapPubs)>0):
	pubTime = float(coapPubs[len(coapPubs)-1].sniff_timestamp) - float(coapPubs[0].sniff_timestamp)

f = open("out.csv","a")
#EACH LINE HAS:
#     NSUB;	TYPE;		NUM;		SIZE;		OVERHEAD;		TIME
out = str(int(len(coapSubs)/2))+";SUB;"+str(len(coapSubs))+";"+str(subSize)+";"+str(subOverhead)+";"+str(subTime)

f.write(out.replace(".",",")+"\n")
out2 = str(int(len(coapSubs)/2))+";PUB;"+str(len(coapPubs))+";"+str(pubSize)+";"+str(pubOverhead)+";"+str(pubTime)
f.write(out2.replace(".",",")+"\n")
f.close()
print("Done")


