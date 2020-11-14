import csv,sys,pyshark

if len(sys.argv)>=2:
	numPubs=1
	numSubs=int(sys.argv[1])
if len(sys.argv)>=3:	
	numSubs = int(sys.argv[1])
	numPubs=int(sys.argv[2])

else:
	numPubs = 1
	numSubs = 1

numVal = 50
pubTimes = []
pubackTimes =[]
notifyTimes = []
subTimes = []
subAckTimes = []

for i in range(0,numSubs):
	subTimes.append(0.0)
	subAckTimes.append(0.0)
for i in range(0,numVal):
	notifyTimes.append([])
	for j in range(0,numSubs):
		notifyTimes[i].append(0.0)
		
for i in range(1,numPubs+1):
	with open("csv/pub"+str(i)+".csv") as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=';')
		line_count = 0
		for row in csv_reader:
			line_count += 1
			if line_count <2:
				pass
			else:
				pubTimes.append(float(row[0]))
				pubackTimes.append(float(row[1]))
		csv_file.close()

def getIndexOfPub(pubTime):
	for i in range(0,len(pubTimes)):
		if pubTimes[i]==pubTime:
			return i
	print(pubTime)
	return -1

if(len(pubackTimes)>0):
	no_response = False
else:
	no_response = True

extraNotify = 0
for i in range(1,numSubs+1):
	with open("csv/sub"+str(i)+".csv") as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=';')
		line_count = 0
		for row in csv_reader:
			line_count +=1
			if line_count <2:
				continue
			if row[0]=="SUB":
				subTimes[i-1]=float(row[1])
			elif row[0]=="A":

				subAckTimes[i-1]=float(row[1])
			else:
				pubTime = float(row[0])
				index = getIndexOfPub(pubTime)
				if(index<0):
					pubTimes.append(pubTime)
					pubackTimes.append(0.0)
					index = len(pubTimes)-1
				if notifyTimes[index][i-1]==0.0:
					notifyTimes[index][i-1]=float(row[1])
				else:
					print("extra notify: sub"+str(i)+" pcktime: "+str(pubTimes[index]))
					extraNotify +=1
		csv_file.close()


avgTotTime =0
avgSingleTime=0
avgPubAckTime=0
pubackLost = 0
totSkipped =0
for i in range(0,len(pubTimes)):
	lastNotify = max(notifyTimes[i])
	if lastNotify>0:
		avgTotTime += lastNotify-pubTimes[i]
	else:
		totSkipped +=1

	for time in notifyTimes[i]:
		if time >0:
			avgSingleTime += (time-pubTimes[i])

	if not no_response:
		if pubackTimes[i] ==0.0:
			pubackLost +=1
		else:
			avgPubAckTime+=(pubackTimes[i]-pubTimes[i])

avgTotTime = avgTotTime/(len(pubTimes)-totSkipped)
avgPubAckTime = avgPubAckTime/len(pubTimes)
print("avgTotTime: ",avgTotTime)
print("avgPubAckTime",avgPubAckTime)
totalNotify = 0
for i in range(0,len(pubTimes)):
	for j in range(0,numSubs):
		if notifyTimes[i][j]!=0.0:
			totalNotify += 1
avgSingleTime = avgSingleTime/totalNotify
print("avgSingleTime: ",avgSingleTime)



lastTime = 0
for i in range(0,len(pubTimes)):
	lastTime = max(lastTime,max(notifyTimes[i]))
totTime = lastTime - min(pubTimes)
print("totTime: ",totTime)



avgSubAckTime = 0
skipped = 0
for i in range(0,numSubs):
	if subAckTimes[i]!= 0.0 and subTimes[i]!=0.0:
		avgSubAckTime += subAckTimes[i]-subTimes[i]
	else:
		skipped +=1
		continue
avgSubAckTime = avgSubAckTime/(numSubs-skipped)
print("avgSubAckTime",avgSubAckTime)



totalSubTime = max(subAckTimes)-min(subTimes)
print("totalSubTime: ",totalSubTime)


print("totalNotify: ",totalNotify)
print("extraNotify: ",extraNotify)

print("total puback lost: ",pubackLost)
print("total suback lost: ",(numSubs-len(subAckTimes)))


cpu = 0
mem = 0
with open("csv/broker.csv") as csv_file:
	cnt = 0
	for line in csv_file:
		cnt +=1
		if cnt == 1:
			continue
		words = line.split("  ")
		cpu += float(words[0])
		mem += float(words[1])

	csv_file.close()
cpu = cpu/cnt
mem = mem/cnt
print("avg cpu:",cpu)
print("avg memory: ",mem)


totalBytes = 0
capFile = pyshark.FileCapture("./captures/capture.cap")
for pck in capFile:
	if "coap" in pck:
		if int(pck.coap.code) in [1,3,68,69]:
			totalBytes +=int(pck.length)
print("totalBytes: ",totalBytes)


f=open("out"+sys.argv[3]+".csv","a")
out = str(numSubs)+";"+str(totalNotify)+";"+str(totTime)+";"+str(avgSingleTime)+";"+str(avgPubAckTime)+";"+str(avgSubAckTime)+";"+str(numVal*numSubs - totalNotify)+";"+str(extraNotify)+";"+str(cpu)+";"+str(mem)+";"+str(totalBytes)
f.write(out.replace(".",",")+"\n")
