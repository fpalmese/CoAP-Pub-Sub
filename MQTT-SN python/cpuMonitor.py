import os,time
#take the broker pid
#os.system("ps -C broker_mqtts -o pid --no-headers > csv/pid.txt")
os.system("ps -C MQTT-SNGateway -o pid --no-headers > csv/pid.txt")
f = open("csv/pid.txt","r")
pid = int(f.readline())
f.close()
while(True):
	os.system("ps -p "+str(pid)+" -o %cpu,%mem --no-headers >> csv/broker.csv")
	time.sleep(0.5)
