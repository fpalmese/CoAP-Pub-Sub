#Start server
#WARNING: RUN SERVER SEPARATELY
#./BROKER/mosuitto.rsmb-master/rsmb/src/broker_mqqts BROKER/mosuitto.rsmb-master/rsmb/src/config.txt

#Start capture for subscribe
(sudo tshark -i any -w /home/fabio/Scrivania/MQTT-SN\ python/captures/sub.cap)&
sleep 4

#Start subscribe  (input argument is the number of subscribe)
(python3 test_multi_sub.py $1)&

sleep 10

#Stop capture for subscribe
sudo killall tshark

sleep 1

#Start capture for publish
(sudo tshark -i any -w /home/fabio/Scrivania/MQTT-SN\ python/captures/pub.cap)&
sleep 4

#Start publish
(python3 test_publish.py)&
sleep 20

#Stop capture for publish
sudo killall tshark

#Stop server and subscribers
sudo killall python3

#Analize capture files and print result to csv files
python3 analizeCap.py
