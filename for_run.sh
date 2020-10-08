#!/bin/bash
for i in {1..10}
do
   sudo bash run_new.sh 1
   sleep 3
   sudo bash run_new.sh 10
   sleep 3 
   sudo bash run_new.sh 100
   sleep 3
done
