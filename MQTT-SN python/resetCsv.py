import sys
if len(sys.argv)==2:
	numSubs = int(sys.argv[1])
	numPubs = 1
elif len(sys.argv) ==3:
	numSubs = int(sys.argv[1])
	numPubs = int(sys.argv[2])
else:
	numSubs = 1
	numPubs = 1
#reset sub file
for i in range(1,numSubs+1):
	f=open("csv/sub"+str(i)+".csv","w")
	f.write("SENDTIME;RCVTIME\n")
	f.close()

#reset pub file
f = open("csv/pub.csv","w")
f.write("PAYLOAD;TIME\n")
f.close()

#reset multi pub files
for i in range(1,numPubs+1):
	f=open("csv/pub"+str(i)+".csv","w")
	f.write("PAYLOAD;TIME\n")
	f.close()

