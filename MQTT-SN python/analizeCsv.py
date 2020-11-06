import csv,sys
if(len(sys.argv)!=2):
	numSubs = 1
else:
	numSubs = int(sys.argv[1])


pubTimes =[]
pubackTimes =[]
notifyTimes = []
subTimes = []
subAckTimes = []
with open('csv/sub1.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0
	for row in csv_reader:
		line_count += 1
		if line_count == 1:
			pass
		elif line_count == 2:
			subTimes.append(float(row[1]))
		elif line_count ==3:
			subAckTimes.append(float(row[1]))
		else:	
			pubTimes.append(float(row[0]))
			notifyTimes.append([])
			notifyTimes[line_count-4].append(float(row[1]))
	csv_file.close()

for i in range(2,numSubs+1):
	with open("csv/sub"+str(i)+".csv") as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=';')
		line_count = 0
		for row in csv_reader:
			line_count += 1
			if line_count == 1:
				pass
			elif line_count == 2:
				subTimes.append(float(row[1]))
			elif line_count ==3:
				subAckTimes.append(float(row[1]))
			else:
				notifyTimes[line_count-4].append(float(row[1]))
		csv_file.close()

with open('csv/pub.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0
	for row in csv_reader:
		line_count += 1
		if line_count <2:
			pass
		else:
			pubackTimes.append(float(row[1]))
	csv_file.close()
if(len(pubackTimes)>0):
	no_response = False
else:
	no_response = True

avgTotTime =0
avgSingleTime=0
avgPubAckTime=0
for i in range(0,len(pubTimes)):
	avgTotTime += (notifyTimes[i][len(notifyTimes[i])-1]-pubTimes[i])
	avgRcvSubTime = 0
	for time in notifyTimes[i]:
		avgRcvSubTime += (time-pubTimes[i])
	avgRcvSubTime = avgRcvSubTime / len(notifyTimes[i])
	avgSingleTime+=avgRcvSubTime
	if not no_response:
		avgPubAckTime+=(pubackTimes[i]-pubTimes[i])

avgTotTime = avgTotTime/len(pubTimes)
avgSingleTime = avgSingleTime/len(pubTimes)
avgPubAckTime = avgPubAckTime/len(pubTimes)

print("avgTotTime: ",avgTotTime)
print("avgSingleTime: ",avgSingleTime)
print("avgPubAckTime",avgPubAckTime)

lastNotifyTime=0
for i in range(0,len(notifyTimes)):
	if max(notifyTimes[i]) >lastNotifyTime:
		lastNotifyTime = max(notifyTimes[i])
totTime = lastNotifyTime - pubTimes[0]
print("totTime: ",totTime)


avgSubAckTime = 0
for i in range(0,numSubs):
	avgSubAckTime += subAckTimes[i]-subTimes[i]
avgSubAckTime = avgSubAckTime/numSubs
print("avgSubAckTime "+str(avgSubAckTime))

totalSubTime = max(subAckTimes)-min(subTimes)
print("totalSubTime: ",totalSubTime)

totalNotify = 0
for i in range(0,len(pubTimes)):
		totalNotify+=len(notifyTimes[i])
print("totalNotify: ",totalNotify)


f=open("out.csv","a")
out = str(numSubs)+";"+str(totalNotify)+";"+str(totTime)+";"+str(avgSingleTime)+";"+str(avgTotTime)+";"+str(avgPubAckTime)+";"+str(avgSubAckTime)+";"+str(totalSubTime)
f.write(out.replace(".",",")+"\n")

