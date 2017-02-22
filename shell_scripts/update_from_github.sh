#!/bin/bash
#Controllo aggiornamenti su GitHub
#Script creato da FXO in Gennaio 2017

cd /home/pi/Socomec/monitor_solare
echo "GitHub clone origin..."
LOG=$(git fetch origin 2>&1)
echo "$LOG"
LOG=$(git reset --hard origin/master)
echo "$LOG"
#chmod 755 solar_monitor.py

