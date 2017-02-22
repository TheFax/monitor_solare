#!/bin/bash

LOGFILE="/home/pi/Socomec/log.txt"
sleep 15
echo Autostart > $LOGFILE
#/home/pi/Socomec/update_from_github.sh >> $LOGFILE
/home/pi/Socomec/update_from_usb.sh >> $LOGFILE
/home/pi/Socomec/monitor_solare/solar_monitor.py >> $LOGFILE &
