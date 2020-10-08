import sys
numSubs = int(sys.argv[1])

#reset sub file
for i in range(1,numSubs+1):
	f=open("csv/sub"+str(i)+".csv","w")
	f.write("SENDTIME;RCVTIME\n")
	f.close()

#reset pub file
f = open("csv/pub.csv","w")
f.write("PAYLOAD;TIME\n")
f.close()
