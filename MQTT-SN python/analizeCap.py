import pyshark,sys
from pprint import pprint
mqttsnSubs = []
mqttsnPubs = []

subCap = pyshark.FileCapture("./captures/sub.cap")
print("Analizing sub.cap")
subSize = 0
subOverhead = 0
for pck in subCap:
	if "mqttsn" in pck:
		#print(vars(pck.mqttsn))
		#consider only Connect-Connack and Sub-Suback
		if int(getattr(pck.mqttsn,"msg.type")) in [4,5,18,19]:
			mqttsnSubs.append(pck)			
			subSize +=len(pck)
			#for sub consider the name of the topic as paylaod
			if int(getattr(pck.mqttsn,"msg.type"))==18:
				subOverhead+= (len(pck)-len(getattr(pck.mqttsn,"topic.name.or.id")))
			else:
				subOverhead+=len(pck)

if(len(mqttsnSubs)>0):
	subTime = float(mqttsnSubs[len(mqttsnSubs)-1].sniff_timestamp) - float(mqttsnSubs[0].sniff_timestamp)
subCap.close()

pubCap = pyshark.FileCapture("./captures/pub.cap")
pubTimes = []
notifyTimes = []
pubackTimes = []
pubrelTimes = []
pubSize = 0
pubOverhead = 0
print("Analizing pub.cap")

for pck in pubCap:
	if "mqttsn" in pck:
		#take only Pub-PubAck-Pubrec-Pubrel
		if int(getattr(pck.mqttsn,"msg.type")) in [12,13,14,15]:
			mqttsnPubs.append(pck)
			pubSize+=len(pck)
			#for pub consider msg value as payload
			if int(getattr(pck.mqttsn,"msg.type"))==12:
				pubOverhead+=(len(pck)-len(getattr(pck.mqttsn,"pub.msg")))
				try:
					notifyTimes[int(getattr(pck.mqttsn,"pub.msg"))-1].append(float(pck.sniff_timestamp))
				except:
					notifyTimes.append([])
					pubTimes.append(float(pck.sniff_timestamp))
			else:
				pubOverhead+=len(pck)
				if int(getattr(pck.mqttsn,"msg.type"))==13 and int(pck.udp.port)==1885:
					pubackTimes.append(float(pck.sniff_timestamp))
				elif int(getattr(pck.mqttsn,"msg.type"))==15 and int(pck.udp.port)==1885:
					pubrelTimes.append(float(pck.sniff_timestamp))
pubCap.close()
avgTotTime = 0
avgSingleTime = 0
avgPuback = 0
avgPubrel = 0
qos = 0
if len(pubackTimes)>0:
	if len(pubrelTimes)>0:
		qos=2
	else:
		qos=1	

for i in range(0,len(pubTimes)):
	avgTotTime += (notifyTimes[i][len(notifyTimes[i])-1]-pubTimes[i])
	avgRcvSubTime=0
	for time in notifyTimes[i]:
		avgRcvSubTime += (time-pubTimes[i])
	avgRcvSubTime = avgRcvSubTime / len(notifyTimes[i])
	avgSingleTime +=avgRcvSubTime
	if qos==1:
		avgPuback+=(pubackTimes[i]-pubTimes[i])
	elif qos==2:
		avgPubrel+=(pubrelTimes[i]-pubTimes[i])

avgTotTime = avgTotTime/len(pubTimes)
avgSingleTime = avgSingleTime/len(pubTimes)
avgPuback = avgPuback/len(pubTimes)
avgPubrel = avgPubrel/len(pubTimes)

if qos==0:
	avgAckTime = "---"
elif qos==1:
	avgAckTime = str(avgPuback)
else:
	avgAckTime = str(avgPubrel)

if(len(mqttsnPubs)>0):
	pubTime = float(mqttsnPubs[len(mqttsnPubs)-1].sniff_timestamp) - float(mqttsnPubs[0].sniff_timestamp)


fsub = open("outSub.csv","a")
fpub = open("outPub.csv","a")


#EACH LINE HAS:
#    			 NSUB;			NUM;		SIZE;		OVERHEAD;		TIME;	AVG TOT TIME; 	AVG SINGLE TIME; AVG PUBACK TIME
outSub = str(int(len(mqttsnSubs)/4))+";"+str(len(mqttsnSubs))+";"+str(subSize)+";"+str(subOverhead)+";"+str(subTime)
fsub.write(outSub.replace(".",",")+"\n")
fsub.close()
outPub = str(int(len(mqttsnSubs)/4))+";"+str(len(mqttsnPubs))+";"+str(pubSize)+";"+str(pubOverhead)+";"+str(pubTime)+";"+str(avgSingleTime)+";"+str(avgTotTime)+";"+str(avgAckTime)
fpub.write(outPub.replace(".",",")+"\n")
fpub.close()




