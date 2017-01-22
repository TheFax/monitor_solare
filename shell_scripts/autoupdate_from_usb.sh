#!/bin/bash
#Controllo se ci sono aggiornamenti in una chiavetta USB qualsiasi
#Script creato da FXO in Gennaio 2017
#versione 1

#Cerco la directory 'monitor_solare'
DIR_SEARCH="$(find /media/ -type d -name 'monitor_solare' -print -quit)"

if [ -d "$DIR_SEARCH" ] ; then
   #Se ne ho trovata una, ed è davvero una directory...
   echo $DIR_SEARCH found on USB device.
   #copio con rsync
   rsync -rt -c "$DIR_SEARCH"/ ./monitor_solare/
   #smonto tutti i device USB
   umount /media/pi/*
   #rendo avviabile lo script python
   chmod 755 ./monitor_solare/solar_monitor.py
else
   #Se non ho trovato la directory...
   echo There is not a USB device with a monitor_solare folder inside.
fi

