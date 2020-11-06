#!/bin/bash

#Reset csv files
python3 resetCsv.py $1

#Start server
#WARNING: RUN SERVER SEPARATELY
(./BROKER/mosquitto.rsmb-master/rsmb/src/broker_mqtts BROKER/mosquitto.rsmb-master/rsmb/src/config.txt)&


sleep 2

#Start subscribe  (input argument is the number of subscribe)
(python3 test_multi_sub.py $1)&

sleep 20

#Start publish
(python3 test_publish.py 100 0.1)&
sleep 35

#Stop publisher and subscribers
sudo killall python3

#Stop broker
sudo killall broker_mqtts

#Analize capture files and print result to csv files
#python3 analizeCsv.py $1
