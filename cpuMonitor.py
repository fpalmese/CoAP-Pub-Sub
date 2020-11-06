import os,time
f = open("csv/pid.txt")
pid = int(f.readline())
#os.system("ps -p "+pid+" -o %cpu,%mem --no-headers >> csv/broker.csv")
while(True):
	os.system("ps -p "+str(pid)+" -o %cpu,%mem --no-headers >> csv/broker.csv")
	time.sleep(0.5)
