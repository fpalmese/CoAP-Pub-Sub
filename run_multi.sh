#!/bin/bash

#Reset csv files
#(first input argument is the number of subscribe)
#(second input argument is the number of publish)
(python3 resetCsv.py $1 $2)

#Run broker
(python3 broker/broker.py)&

sleep 1

#start cpu/mem tracking
(python3 cpuMonitor.py)&

#start wireshark capture on loopback interface
(sudo tshark -i lo -w /home/fabio/Scrivania/COAP\ PUB-SUB/captures/capture.cap)&

sleep 6

#Start subscribe  (input argument is the number of subscribe)
(python3 subscribers.py $1)&

sleep 9

#add loss rate , $3 is packet loss!!
sudo tc qdisc add dev lo root netem loss $3%


sleep 1
#Start publish
(python3 multi_publisher.py $2)&


#sleep `expr 15 + $3 \* 2`
sleep 18

#Stop broker, clients and cpu/mem tracking
sudo killall python3

#stop wireshark capture
sudo killall tshark

#remove loss rate
sudo tc qdisc del dev lo root

python3 analizeMulti.py $1 $2 $3




