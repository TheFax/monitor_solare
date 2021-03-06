#!/usr/bin/python
# -*- coding: utf-8 -*-

# Monitor solare
# FXO 12/12/2016 ... Dicembre 2016 / Gennaio 2017

# Questo software è progettato per funzionare su Banana PI oppure su Raspberry PI
# Se avviato su BananaPI, è necessario usare Python 2.7 perchè GPIO non è supportato da Python 3

######################################################################################################
######################################################################################################
#Libraries
######################################################################################################
######################################################################################################

#tkinter per la parte grafica
try:
    #Python 2
    import Tkinter as tk
except ImportError:
    #python 3
    import tkinter as tk
    print ("Loaded library tkinter (probably running on Python 3.x)")
else:
    print ("Loaded library Tkinter (probably running on Python 2.x)")

#time è usata per alcune funzioni legate al rilevamento del tempo e per creare ritardi
import time

#sys e os sono usate per determinare la directory corrente
import sys, os

#GPIO serve appunto per i GPIO
import RPi.GPIO as GPIO

######################################################################################################
######################################################################################################
#Configuration
######################################################################################################
######################################################################################################

#Fonts
fontButton =       "-family {Cantarell}     -size 24 -weight bold -slant roman -underline 0 -overstrike 0"
fontDescrLabel  =  "-family {Nimbus Sans L} -size 34              -slant roman -underline 0 -overstrike 0"
fontLabel  =       "-family {Nimbus Sans L} -size 54 -weight bold -slant roman -underline 0 -overstrike 0"
fontBottomLabel  = "-family {Nimbus Sans L} -size 28              -slant roman -underline 0 -overstrike 0"

#GPIO configuration
GPIO_CICALINA = 25
GPIO_CURRENT_1 = 21     #Sensori di corrente 1 e 2
GPIO_CURRENT_2 = 20
GPIO_SIM_1_STATUS = 26  #Stato dei simulatori 1 e 2 
GPIO_SIM_2_STATUS = 16

#Fullscreen? true or false
fullscren_mode = "true"

######################################################################################################
######################################################################################################
#Constants
######################################################################################################
######################################################################################################

#Versione software: ricordarsi di aggiornarla
VERSION = "4.9"

#Tempi
AUTOARM_TIME = 400  #secondi
RUNIN_TIME =  5460 #secondi
AUTOARM_AFTER_NOT_FLOWING = 60 #secondi
SHUTDOWN_TIME = "17:05"
SHUTDOWN_PROCEDURE = "sudo shutdown -t 0"

#Color constants
RED =   "#ff0000"
GREEN = "#00ff00"
BLUE =  "#0000ff"
WHITE = "#ffffff"
BLACK = "#000000"
GRAY =  "#8D8D8D"
ORANGE= "#ff8000"
YELLOW= "#ffff00"
CIAN =  "#25D0FF"

#LOOP state constants
LOOP_STANDBY_INIT =             "Standby..."
LOOP_STANDBY =                  "Standby"
LOOP_ARMING_INIT =              "Arming..."
LOOP_ARMING =                   "Arming"
LOOP_ARMED_INIT =               "Armed..."
LOOP_ARMED =                    "Armed"
LOOP_HOLE_INIT =                "Fail..."
LOOP_HOLE =                     "Fail!"
LOOP_END_RUN_IN_INIT =          "Run-in ENDING"
LOOP_END_RUN_IN =               "Run-in PASS"
LOOP_CURRENT_NOT_FLOWING_INIT = "Current not flowing..."
LOOP_CURRENT_NOT_FLOWING =      "Current not flowing"
LOOP_MANUAL_OFF_INIT =          "Manual OFF..."
LOOP_MANUAL_OFF =               "Manual OFF"
LOOP_MANUAL_TIMER_INIT =        "Manual Timer..."
LOOP_MANUAL_TIMER =             "Manual Timer"


#SIMULATOR state constants
SIMULATOR_ON = "ON"
SIMULATOR_OFF = "OFF"

#CURRENT state constants
CURRENT_PRESENT = "Flowing"
CURRENT_ABSENT = "Not flowing"

######################################################################################################
######################################################################################################
#Functional Variables
######################################################################################################
######################################################################################################

#Timers speed
FAST_TIMER_SPEED = 100
SLOW_TIMER_SPEED = 500

#Fast timer counter (only for debug & info)
fast_counter = 0

#Loop state
LOOP_1_status = LOOP_STANDBY_INIT
LOOP_2_status = LOOP_STANDBY_INIT

#Simulator state
SIMULATOR_1_status = SIMULATOR_OFF
SIMULATOR_2_status = SIMULATOR_OFF

#Current state
CURRENT_1_status = CURRENT_ABSENT
CURRENT_2_status = CURRENT_ABSENT

#Countdown
countdown = [ 0 , 0 , 0]

#Rilevatore del cambio di secondo
seconds_edge_finder = 0

######################################################################################################
######################################################################################################
#Functions
######################################################################################################
######################################################################################################

def timer_fast():
    '''Richiamata ogni 100ms, si occupa di verificare lo stato dei simulatori, della corrente
    passante per i TA e di calcolare lo stato dei Loop per verificare i buchi di erogazione.
    Lo stato dei simulatori, lo stato dei loop e lo stato di passaggio della corrente vengono 
    salvati in variabili globali.'''
    global fast_counter
    global SIMULATOR_1_status
    global SIMULATOR_2_status
    global CURRENT_1_status
    global CURRENT_2_status
    global LOOP_1_status
    global LOOP_2_status
    fast_counter += 1
    SIMULATOR_1_status = test_simulator (GPIO_SIM_1_STATUS)
    SIMULATOR_2_status = test_simulator (GPIO_SIM_2_STATUS)
    CURRENT_1_status = test_ta (GPIO_CURRENT_1)
    CURRENT_2_status = test_ta (GPIO_CURRENT_2)
    LOOP_1_status = main_logic(1, LOOP_1_status, CURRENT_1_status, SIMULATOR_1_status)
    LOOP_2_status = main_logic(2, LOOP_2_status, CURRENT_2_status, SIMULATOR_2_status)
    #global countdown; print countdown, SIMULATOR_1_status, SIMULATOR_2_status, CURRENT_1_status, CURRENT_2_status, GPIO_SIM_1_STATUS, GPIO_CURRENT_1
    #Ri-armo il timer fast
    root.after(FAST_TIMER_SPEED,timer_fast)

def timer_slow():
    '''Richiamata circa 2 volte al secondo, aggiorna la grafica e rileva il passaggio dei secondi
    per poter eseguire i countdown dovuti'''
    global Countdown           #questo in realtà è un array
    global seconds_edge_finder #ultimo secondo effetivo
    #Aggiornamento parte grafica
    update_debug_labels()      
    update_labels()
    #Rilevo il passaggio dei secondi
    time_time=time.time()    #Leggo l'orario attuale   
    if seconds_edge_finder != int(time_time):   #Confronto l'orario letto con quello memorizzato nella variabile "seconds_edge_finder"
        #Se l'orario attuale differisce da quello salvato, vuol dire che stiamo analizzando un "nuovo" secondo.
        #Questo significa che:
        #passo per questo punto del programma 1 volta al secondo
        seconds_edge_finder = int(time_time)
        #Decremento i countdown, se è il caso di farlo
        if countdown[1] != 0 : countdown[1] -= 1
        if countdown[2] != 0 : countdown[2] -= 1
        #Verifico se è ora di spegnere il Raspberry
        if time.strftime('%H:%M') == SHUTDOWN_TIME :
            if SIMULATOR_1_status == SIMULATOR_OFF and SIMULATOR_2_status == SIMULATOR_OFF:
                os.System(SHUTDOWN_PROCEDURE)

    root.after(SLOW_TIMER_SPEED,timer_slow)

#cicalacounter=0
def timer_beep():
    dontuseme()
    #global cicalacounter
    #cicalacounter=cicalacounter+1
    root.after(100,timer_beep)

def melodia_autoarm():
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,0)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,0)
    time.sleep(1)
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,0)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,0)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,0)

def melodia_pausa():
   #'se'
   GPIO.output(GPIO_CICALINA,1)
   time.sleep(0.091)
   GPIO.output(GPIO_CICALINA,0)
   time.sleep(0.192)
   #'c'è'
   GPIO.output(GPIO_CICALINA,1)
   time.sleep(0.061)
   GPIO.output(GPIO_CICALINA,0)
   time.sleep(0.069)
   #'la'
   GPIO.output(GPIO_CICALINA,1)
   time.sleep(0.065)
   GPIO.output(GPIO_CICALINA,0)
   time.sleep(0.073)
   #'go'
   GPIO.output(GPIO_CICALINA,1)
   time.sleep(0.094)
   GPIO.output(GPIO_CICALINA,0)
   time.sleep(0.197)
   #'ccia'
   GPIO.output(GPIO_CICALINA,1)
   time.sleep(0.175)
   GPIO.output(GPIO_CICALINA,0)
   time.sleep(0.413)
   #'è'
   GPIO.output(GPIO_CICALINA,1)
   time.sleep(0.118)
   GPIO.output(GPIO_CICALINA,0)
   time.sleep(0.197)
   #'giiiiiiiim'
   GPIO.output(GPIO_CICALINA,1)
   time.sleep(2)
   GPIO.output(GPIO_CICALINA,0)

def melodia_finerunin():
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(1)
    GPIO.output(GPIO_CICALINA,0)
    time.sleep(1)
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(1)
    GPIO.output(GPIO_CICALINA,0)
    time.sleep(1)
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(3)
    GPIO.output(GPIO_CICALINA,0)

def melodia_hole():
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,0)

def test_simulator(the_gpio):
    '''Questa funzione rileva lo stato del simulatore collegato al pin passato come argomento'''
    if (GPIO.input(the_gpio) == True) :
    #if 1==1 :    #Usato in modalità demo
        return SIMULATOR_ON
    else:
        return SIMULATOR_OFF

def test_ta(the_gpio):
    '''Questa funzione ricerca il passaggio di corrente sul TA collegato al pin passato come
    argomento, per massimo 40 ms'''
    for x in range(0,40):
        if (GPIO.input(the_gpio) == True) :
        #if (1==1) :   #Usato in modalità demo
            #Arrivo qui se trovo corrente passante per il TA
            return CURRENT_PRESENT
        #Attendo 1 ms
        time.sleep(0.001)
    #Arrivo qui se non ho trovato corrente per 20ms consecutivi
    return CURRENT_ABSENT

def main_logic(loop,actual_status,ta,simulator):
    '''Questa funzione calcola lo stato del loop, partendo dai tre argomenti passati:
    -Il numero di loop
    -Lo stato precedente del loop
    -Lo stato del passaggio di corrente
    -Lo stato di erogazione del simulatore
    ---
    Tutto funziona grazie ad una macchina a stati finiti.
    '''
    if   (actual_status == LOOP_STANDBY_INIT) :
        countdown[loop] = 0
        actual_status = LOOP_STANDBY
    elif (actual_status == LOOP_STANDBY) :
        #Stato STANDBY. Questo significa simulatore spento.
        #if ta == CURRENT_PRESENT:
        #    actual_status = LOOP_ARMING_INIT
        if simulator == SIMULATOR_ON:
            actual_status = LOOP_ARMING_INIT
    elif (actual_status == LOOP_ARMING_INIT) :
        countdown[loop] = AUTOARM_TIME    #Tempo autoarm / Carico il contatore
        actual_status = LOOP_ARMING
    elif (actual_status == LOOP_ARMING) :
        #Stato ARMING. Questo significa simulatore acceso, ma devo ancora attendere che il solare inizi ad erogare in rete
        if countdown[loop] == 0:
            if ta == CURRENT_ABSENT :
                actual_status = LOOP_CURRENT_NOT_FLOWING_INIT
            else :
                actual_status = LOOP_ARMED_INIT
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
    elif (actual_status == LOOP_ARMED_INIT) :
        countdown[loop] = RUNIN_TIME    #Tempo run-in
        melodia_autoarm()
        actual_status = LOOP_ARMED
    elif (actual_status == LOOP_ARMED) :
        #Stato ARMED: Questo significa simulatore acceso e solare in erogazione. Questo stato perdura per tutto il run-in
        if countdown[loop] == 0:
            actual_status = LOOP_END_RUN_IN_INIT
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
        if ta == CURRENT_ABSENT:
            actual_status = LOOP_HOLE_INIT
    elif (actual_status == LOOP_HOLE_INIT) :
        countdown[loop] = 0
        event_logger("Logic","Hole in loop " + str(loop))
        actual_status = LOOP_HOLE
    elif (actual_status == LOOP_HOLE) :
        #Stato HOLE: Questo significa che ho rilevato un "buco" di erogazione e devo segnalarlo tramite beep
        melodia_hole()
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
    elif (actual_status == LOOP_END_RUN_IN_INIT) :
        countdown[loop] = -1
        melodia_finerunin()
        actual_status = LOOP_END_RUN_IN
    elif (actual_status == LOOP_END_RUN_IN) :
        #Stato END_RUN_IN: Questo significa che il tempo di run-in è passato. Continuiamo comunque a ricercare buchi di erogazione
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
        if ta == CURRENT_ABSENT:
            actual_status = LOOP_HOLE_INIT
        if countdown[loop] == -600:
            melodia_finerunin()  
    elif (actual_status == LOOP_CURRENT_NOT_FLOWING_INIT) :
        event_logger("Logic","Current not flowing in loop " + str(loop))
        actual_status =  LOOP_CURRENT_NOT_FLOWING
    elif (actual_status == LOOP_CURRENT_NOT_FLOWING) :
        #Stato CURRENT_NOT_FLOWING: Questo significa che il simulatore è acceso da un po' e il solare non ha ancora iniziato l'erogazione. C'è un problema.
        melodia_hole()
        if ta == CURRENT_PRESENT :
            countdown[loop] = AUTOARM_AFTER_NOT_FLOWING    #Tempo autoarm / Carico il contatore
            actual_status = LOOP_ARMING
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
    elif (actual_status == LOOP_MANUAL_OFF_INIT) :
        #Stato MANUAL_OFF: Tutte le logiche automatiche sono disattivate.
    	actual_status = LOOP_MANUAL_OFF
    	countdown[loop] = 0
    elif (actual_status == LOOP_MANUAL_OFF) :
    	pass
    elif (actual_status == LOOP_MANUAL_TIMER_INIT) :
    	actual_status = LOOP_MANUAL_TIMER
    	countdown[loop] = RUNIN_TIME    #Tempo run-in
    elif (actual_status == LOOP_MANUAL_TIMER) :
        #Stato MANUAL_TIMER: Eseguo solo un conteggio alla rovescia, per cronometrare il tempo di run-in. Le logiche automatiche sono disattivate
        if countdown[loop] == 0:
            countdown[loop] = -1
            melodia_finerunin()
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
    else:
        #Per nessuna ragione dovrei passare di qui...
        pass
    return actual_status


def click_lblWallpaper(event=None):
    '''Se clicco nello sfondo dell'applicazione, questa si chiude'''
    GPIO.output(GPIO_CICALINA,0)
    event_logger("Event","exit via click_lblWallpaper")
    root.destroy()


def click_btnOff1():
    event_logger("Event","Manual off loop 1")
    global LOOP_1_status
    LOOP_1_status = LOOP_MANUAL_OFF_INIT

def click_btnDisarm1():
    event_logger("Event","Manual disarm loop 1")
    global LOOP_1_status
    LOOP_1_status = LOOP_STANDBY_INIT

def click_btnTimer1():
    event_logger("Event","Manual timer loop 1")
    global LOOP_1_status
    LOOP_1_status = LOOP_MANUAL_TIMER_INIT

def click_btnOff2():
    event_logger("Event","Manual off loop 2")
    global LOOP_2_status
    LOOP_2_status = LOOP_MANUAL_OFF_INIT

def click_btnDisarm2():
    event_logger("Event","Manual disarm loop 2")
    global LOOP_2_status
    LOOP_2_status = LOOP_STANDBY_INIT

def click_btnTimer2():
    event_logger("Event","Manual timer loop 2")
    global LOOP_2_status
    LOOP_2_status = LOOP_MANUAL_TIMER_INIT

def event_logger(group, description):
    '''Tengo traccia degli eventi importanti
    -group = una parola che identifichi il macrogruppo
    -description = una fresetta che identifichi l'evento'''
    print "[",time.strftime('%H:%M:%S'),"] ", group, ":", description
    text = "[" + time.strftime('%H:%M:%S') + "] " + group + " - " + description
    lblBottom.configure(text=text)

def update_debug_labels():
    '''Solo per debug'''
    global fast_counter
    time_now = time.strftime('%H:%M:%S')  #20:33:59
    time_time = time.time()               #1483472098.44
    time.sleep(0.002)                     #delay 2ms
    time_time2 = time.time()
    time_clock = time.clock() * 1000      #per quanti millisecondi ho occupato il uP?
    delta = time_time2 - time_time
    #stringone = "Now:" + str(time_now) + " | Time:" + str(time_time) + "s | Processor: " + str(time_clock) + "ms | Counter: " + str(fast_counter) + " ticks | Delta: " + str(delta*1000) + " ms"
    stringone="CT1: " + CURRENT_1_status + " | CT2: " + CURRENT_2_status
    lblDebug.config(text=stringone)

def update_labels():
    '''Aggiorno lo stato di tutte le label della finestra'''
    mytext=text_composer(LOOP_1_status,countdown[1])
    lblSim1.config(text=mytext)
    mycolor=color_composer(LOOP_1_status)
    lblSim1.configure(background=mycolor)

    mytext=text_composer(LOOP_2_status,countdown[2])
    lblSim2.config(text=mytext)
    mycolor=color_composer(LOOP_2_status)
    lblSim2.configure(background=mycolor)

def text_composer(status,my_countdown):
    '''Il compositore dei testi che finiranno nelle label dello stato dei Loop'''
    if my_countdown < 0:
        mytext=status
        mytext += ": "
        mytext += time.strftime("%H:%M:%S", time.gmtime(abs(my_countdown)))
    elif my_countdown == 0:
        mytext=status
    elif my_countdown < 3600:
        mytext=status
        mytext += ": "
        mytext += time.strftime('%M:%S"', time.gmtime(my_countdown))
    elif my_countdown >= 3600:
        mytext=status
        mytext += ": "
        mytext += time.strftime("%H:%M", time.gmtime(my_countdown))
    else:
        mytext = "Error"
    return mytext

def color_composer(status):
    '''Il selettore del colore che dovranno avere le label dei Loop'''
    if status==LOOP_ARMING:
        return YELLOW
    if status==LOOP_STANDBY:
        return GRAY
    if status==LOOP_ARMED:
        return GREEN
    if status==LOOP_HOLE:
        return ORANGE
    if status==LOOP_END_RUN_IN:
        return GREEN
    if status==LOOP_MANUAL_OFF:
    	return CIAN
    if status==LOOP_MANUAL_TIMER:
    	return CIAN


def setup_GPIO():
    '''Inizializzazione GPIO'''
    GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_CURRENT_1,GPIO.IN)
    GPIO.setup(GPIO_CURRENT_2,GPIO.IN)
    GPIO.setup(GPIO_SIM_1_STATUS,GPIO.IN)
    GPIO.setup(GPIO_SIM_2_STATUS,GPIO.IN)
    GPIO.setup(GPIO_CICALINA,GPIO.OUT)
    GPIO.output(GPIO_CICALINA,1)
    time.sleep(0.1)
    GPIO.output(GPIO_CICALINA,0)
    pass

######################################################################################################
######################################################################################################
#Main
######################################################################################################
######################################################################################################

print 'Command line, with arguments: ', sys.argv[0]
pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname)
print 'Full path: ', fullpath

#Creazione finestra principale Tkinter
root = tk.Tk()
root.title("Solar Monitor")             #titolo
root.minsize(300,300)                   #minima dimensione
root.geometry("1280x768")               #dimensione richiesta
root.configure(background='#ffffff')    #background

#A pieno schermo?
if fullscren_mode == "true":
    root.attributes("-fullscreen", True)   #http://effbot.org/tkinterbook/wm.htm

#Rilevo (e scrivo per debug) la dimensione dello schermo in pixel
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
print "Screen width = ", str(screen_width)
print "Screen height = ", str(screen_height)

#Canvas principale
canvas = tk.Canvas(root)
canvas.config(background=WHITE)
canvas.place(x=0, y=0, height=screen_height, width=screen_width)

#La seguente riga di codice traccia una diagonale sullo schermo. Utile per vedere l'overscan.
#canvas.create_line(0,0,screen_width,screen_height)

#Wallpaper di tutta la finestra
lblWallpaper = tk.Label(root)
#lblWallpaper.place(x=0, y=0, height=screen_height, width=screen_width)
lblWallpaper.place(x=0, y=0)
root._img1 = tk.PhotoImage(file=fullpath+"/monitor_solare_wallpaper3.png")
lblWallpaper.configure(image=root._img1)
lblWallpaper.configure(text="")
lblWallpaper.bind("<Button-1>",click_lblWallpaper)

#Bottone exit, fin'ora usato solo per debug
##btnExit = tk.Button(root)
##btnExit.place(x=30, y=260, height=46, width=207)
##btnExit.configure(activebackground="#d9d9d9")
##btnExit.configure(command=root.destroy)
##btnExit.configure(font=fontButton)
##btnExit.configure(text='''Exit''')

#Loop1
lblDescr1 = tk.Label(root)
lblDescr1.place(x=300, y=40, height=60, width=310)
lblDescr1.configure(background=WHITE, anchor='w')
lblDescr1.configure(font=fontDescrLabel)
lblDescr1.configure(text=''' Simulator 1''')
#Le prossime tre righe costruiscono la linea grafica su Loop1
canvas.create_line(300,101,1091,101)
canvas.create_line(300,102,1091,102)
canvas.create_line(300,103,1091,103)

lblSim1 = tk.Label(root)
lblSim1.place(x=300, y=105, height=140, width=1011)
lblSim1.configure(background=GREEN)
lblSim1.configure(font=fontLabel)
lblSim1.configure(text='''loading''')

btnOff1 = tk.Button(root)
btnOff1.place(x=800, y=40, height=60, width=100)
btnOff1.configure(activebackground="#d9d9d9")
btnOff1.configure(takefocus="0")
btnOff1.configure(command=click_btnOff1)
btnOff1.configure(font=fontButton)
btnOff1.configure(text='''OFF''')

btnDisarm1 = tk.Button(root)
btnDisarm1.place(x=925, y=40, height=60, width=175)
btnDisarm1.configure(activebackground="#d9d9d9")
btnDisarm1.configure(takefocus="0")
btnDisarm1.configure(command=click_btnDisarm1)
btnDisarm1.configure(font=fontButton)
btnDisarm1.configure(text='''Reset''')

btnTimer1 = tk.Button(root)
btnTimer1.place(x=1125, y=40, height=60, width=175)
btnTimer1.configure(activebackground="#d9d9d9")
btnTimer1.configure(takefocus="0")
btnTimer1.configure(command=click_btnTimer1)
btnTimer1.configure(font=fontButton)
btnTimer1.configure(text='''Timer''')

#Predisposizione progressbar
#TProgressbar1 = tk.Progressbar(root)
#TProgressbar1.place(relx=0.37, rely=0.26, relwidth=0.62, relheight=0.0, height=19)
#TProgressbar1.configure(length="790")

#Loop2
lblDescr2 = tk.Label(root)
lblDescr2.place(x=300, y=300, height=60, width=310)
lblDescr2.configure(background=WHITE, anchor='w')
lblDescr2.configure(font=fontDescrLabel)
lblDescr2.configure(text=''' Simulator 2''')
#Le prossime tre righe costruiscono la linea grafica su Loop2
canvas.create_line(300,361,1091,361)
canvas.create_line(300,362,1091,362)
canvas.create_line(300,363,1091,363)
lblSim2 = tk.Label(root)
lblSim2.place(x=300, y=365, height=140, width=1011)
lblSim2.configure(background=GREEN)
lblSim2.configure(font=fontLabel)
lblSim2.configure(text='''loading...''')

btnOff1 = tk.Button(root)
btnOff1.place(x=800, y=300, height=60, width=100)
btnOff1.configure(activebackground="#d9d9d9")
btnOff1.configure(takefocus="0")
btnOff1.configure(command=click_btnOff2)
btnOff1.configure(font=fontButton)
btnOff1.configure(text='''OFF''')

btnDisarm1 = tk.Button(root)
btnDisarm1.place(x=925, y=300, height=60, width=175)
btnDisarm1.configure(activebackground="#d9d9d9")
btnDisarm1.configure(takefocus="0")
btnDisarm1.configure(command=click_btnDisarm2)
btnDisarm1.configure(font=fontButton)
btnDisarm1.configure(text='''Reset''')

btnTimer1 = tk.Button(root)
btnTimer1.place(x=1125, y=300, height=60, width=175)
btnTimer1.configure(activebackground="#d9d9d9")
btnTimer1.configure(takefocus="0")
btnTimer1.configure(command=click_btnTimer2)
btnTimer1.configure(font=fontButton)
btnTimer1.configure(text='''Timer''')

#Predisposizione progressbar
#TProgressbar2 = tk.Progressbar(root)
#TProgressbar2.place(relx=0.37, rely=0.70, relwidth=0.62, relheight=0.0, height=19)
#TProgressbar2.configure(length="790")

#Label in basso, contenente l'ultimo evento loggato
lblBottom = tk.Label(root)
lblBottom.place(x=30, y=560, height=60, width=screen_width-30-30)
lblBottom.configure(background="#808080")
lblBottom.configure(font=fontBottomLabel)
lblBottom.configure(text='''Solar Monitor''')



#Label centrale per debug
lblDebug = tk.Label(root, font=("Helvetica", 36))
lblDebug = tk.Label(text='Waiting function call...')
lblDebug.place(x=300, y=260, height=20, width=791)

#Button Emergency, fin'ora usato solo per debug. Funziona da solo, senza bisogno di altre funzioni
#btnEmergency = tk.Button(root, text='EMERGENCY', width=25, command=root.destroy)
#btnEmergency.place(x = 10, y = 10 , width=100, height=55)

#Setup GPIO
setup_GPIO()

#Prima riga di LOG
event_logger("System","Boot. Software v " + VERSION)

#Avvio i due timer
timer_fast()
timer_slow()

#Passo il controllo al sistema ad eventi
root.mainloop()
