#!/bin/bash
for i in {20,30}
do
   for j in {1..10}
   do
   	sudo bash run_multi.sh 1 1 $i
        sleep 3
        sudo bash run_multi.sh 10 10 $i
        sleep 3
        sudo bash run_multi.sh 100 50 $i
   done


done
