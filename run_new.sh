#!/bin/bash
#Reset csv files
(python3 resetCsv.py $1)

#Run broker
(python3 broker/app.py)&

sleep 2

#Start subscribe  (input argument is the number of subscribe)
(python3 subscribers.py $1)&

sleep 10

#Start publish
(python3 publisher.py 100 0.1)&
sleep 30

#Stop broker and clients
sudo killall python3

#Analyze capture files and print result to csv files
#python3 analizeCap.py

#Analyze csv files for pub/sub times
#python3 analizeCsv.py $1


