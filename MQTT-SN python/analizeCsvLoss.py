import csv,sys
if(len(sys.argv)!=2):
	numSubs = 1
else:
	numSubs = int(sys.argv[1])
numPubs = 100

pubTimes = []
pubackTimes =[]
notifyTimes = []
subTimes = []
subAckTimes = []

for i in range(0,numSubs):
	subTimes.append(0.0)
	subAckTimes.append(0.0)

for i in range(0,numPubs):
	notifyTimes.append([])
	for j in range(0,numSubs):
		notifyTimes[i].append(0.0)
		

with open('csv/pub.csv') as csv_file:
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
				if subTimes[i-1]!= 0.0:
					continue
				subTimes[i-1]=float(row[1])
			elif row[0]=="SUBACK":
				if subAckTimes[i-1]!= 0.0:
					continue
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


	avgRcvSubTime = 0
	singleSkipped = 0
	for time in notifyTimes[i]:
		if time >0:
			avgRcvSubTime += (time-pubTimes[i])
		else:
			singleSkipped +=1
	try:
		avgRcvSubTime = avgRcvSubTime / (len(notifyTimes[i])-singleSkipped)
		avgSingleTime+=avgRcvSubTime
	except ZeroDivisionError:
		pass
	if not no_response:
		if pubackTimes[i] ==0.0:
			pubackLost +=1
		else:
			avgPubAckTime+=(pubackTimes[i]-pubTimes[i])

avgTotTime = avgTotTime/(len(pubTimes)-totSkipped)
avgSingleTime = avgSingleTime/(len(pubTimes)-totSkipped)
avgPubAckTime = avgPubAckTime/len(pubTimes)
print("avgTotTime: ",avgTotTime)
print("avgSingleTime: ",avgSingleTime)
print("avgPubAckTime",avgPubAckTime)


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

totalNotify = 0
for i in range(0,len(pubTimes)):
	for j in range(0,numSubs):
		if notifyTimes[i][j]!=0.0:
			totalNotify += 1

print("totalNotify: ",totalNotify)
print("extraNotify: ",extraNotify)

print("total puback lost: ",pubackLost)
print("total suback lost: ",(numSubs-len(subAckTimes)))

f=open("out.csv","a")
out = str(numSubs)+";"+str(totalNotify)+";"+str(totTime)+";"+str(avgSingleTime)+";"+str(avgTotTime)+";"+str(avgPubAckTime)+";"+str(avgSubAckTime)+";"+str(totalSubTime)
f.write(out.replace(".",",")+"\n")


