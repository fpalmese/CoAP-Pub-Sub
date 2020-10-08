#Run broker
(python3 broker/app.py)&

#Start capture for subscribe
(sudo tshark -i any -w /home/fabio/Scrivania/COAP\ PUB-SUB/captures/sub.cap)&
sleep 4

#Start subscribe  (input argument is the number of subscribe)
(python3 subscribers.py $1)&

sleep 5

#Stop capture for subscribe
sudo killall tshark

sleep 1

#Start capture for publish
(sudo tshark -i any -w /home/fabio/Scrivania/COAP\ PUB-SUB/captures/pub.cap)&
sleep 4

#Start publish
(python3 publisher.py 100 0.1)&
sleep 18

#Stop capture for publish
sudo killall tshark

#Stop server and subscribers
sudo killall python3

#Analize capture files and print result to csv files
python3 analizeCap.py
