import csv,sys


pubTimes = []
pubackTimes =[]
if len(sys.argv)!=2:
	numNotexisting=0
else:
	numNotexisting = int(sys.argv[1])
with open('csv/pub.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=';')
	line_count = 0
	for row in csv_reader:
		pubTimes.append(float(row[0]))
		pubackTimes.append(float(row[1]))
	csv_file.close()

avgPubAckTime=0
for i in range(0,len(pubTimes)):
	avgPubAckTime+=(pubackTimes[i]-pubTimes[i])

avgPubAckTime = avgPubAckTime/len(pubTimes)

print("avgPubAckTime",avgPubAckTime)
f=open("out.csv","a")
out = str(numNotexisting)+";"+str(avgPubAckTime)
f.write(out.replace(".",",")+"\n")
