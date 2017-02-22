#!/bin/bash
#Controllo se ci sono aggiornamenti in una chiavetta USB qualsiasi
#Script creato da FXO in Gennaio 2017

echo ">Autoupdate script (begin)"
echo "Looking for magic folders into mounted devices..."

#Cerco la directory 'monitor_solare'
DIR_SEARCH="$(find /media/ -type d -name 'update_monitor_solare' -print -quit)"
DIR_BACKUP="$(find /media/ -type d -name 'backup_monitor_solare' -print -quit)"
DIR_DESTINATION="/home/pi/Socomec/monitor_solare"

if [ -d "$DIR_BACKUP" ] ; then
    echo "$DIR_BACKUP found on USB device."
    echo "Generating backup..."
    rm -Rf "$DIR_BACKUP"/*
    cp -Rf "$DIR_DESTINATION"/../* "$DIR_BACKUP"/
    echo "Backup done."
fi

if [ -d "$DIR_SEARCH" ] ; then
   #Se ne ho trovata una, ed è davvero una directory...
   echo "$DIR_SEARCH" found on USB device.

   #Copio con copy (Rf = Recursive force)
   echo "Copy files from USB to Raspberry..."
   cp -Rf "$DIR_SEARCH"/* "$DIR_DESTINATION"/

   #Copio con rsync (rtc = ...)
   #echo "rsync..."
   #rsync -rt -c "$DIR_SEARCH"/ "$DIR_DESTINATION"/

   #smonto tutti i device USB
   echo "Umount USB media..."
   umount /media/pi/*
   echo "Changing execution bit..."
   #rendo avviabile lo script python
   chmod 755 "$DIR_DESTINATION"/solar_monitor.py
   echo "Update from USB terminated."
else
   #Se non ho trovato la directory...
   echo "There is not an USB device with a magic folder inside."
fi
echo "<Autoupdate script (end)"
