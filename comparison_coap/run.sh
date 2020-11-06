#!/bin/bash
#reset csv
rm csv/pub.csv

#Run broker
(python3 ../broker/app.py)&

sleep 1

#create topics
(python3 createTopics.py)&

sleep 1

#Start publishing (input is number of nonexisting topics)
(python3 testClient.py $1)&
sleep 11

#Stop server and publisher
sudo killall python3

#Analize capture files and print result to csv files
python3 analizeCsv.py $1
