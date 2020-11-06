#!/bin/bash

#Reset csv files
#(first input argument is the number of subscribe)
#(second input argument is the number of publish)
python3 resetCsv.py $1 $2

#Start server
#(./BROKER/mosquitto.rsmb-master/rsmb/src/broker_mqtts BROKER/mosquitto.rsmb-master/rsmb/src/config.txt)&
(/home/fabio/Scrivania/MQTTSN-GATEWAY/MQTT-SNGateway -f /home/fabio/Scrivania/MQTTSN-GATEWAY/gateway.conf)&

sleep 1

#start cpu/mem tracking
(python3 cpuMonitor.py)&

#start wireshark capture on loopback interface
(sudo tshark -i any -w /home/fabio/Scrivania/MQTT-SN\ python/captures/capture.cap)&

sleep 5

#Start subscribe  
(python3 test_multi_sub.py $1)&

sleep 10

#Start publish (for qos=-1 use quick_publish)
#(python3 multi_publisher.py $2 $3)&
(python3 quick_publish_sn.py $3)&


#sleep `expr 18 + $3 \* 2`
sleep 18


#Stop publisher,subscribers and cpu/mem tracking
sudo killall python3

#Stop broker
#sudo killall broker_mqtts
sudo killall -s SIGKILL MQTT-SNGateway

#Stop wireshark capture
sudo killall tshark

sudo tc qdisc del dev lo root

#Analize capture files and print result to csv files
python3 analizeMulti.py $1 $2 $3
