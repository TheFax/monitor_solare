#!/bin/bash
#Controllo aggiornamenti su GitHub
#Script creato da FXO in Gennaio 2017
#versione 1

cd ./monitor_solare
git pull
chmod 755 solar_monitor.py
cd ..

