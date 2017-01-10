#!/usr/bin/python
# -*- coding: utf-8 -*-

# Monitor solare versione 2
# FXO 12/12/2016 ... Dicembre 2016 / Gennaio 2017

# Questo software è progettato per funzionare su Banana PI oppure su Raspberry PI
# Se avviato su BananaPI, è necessario usare Python 2.7 perchè GPIO non è supportato da Python 3

######################################################################################################
######################################################################################################
#Libraries
######################################################################################################
######################################################################################################

try:
    #Python 2
    import Tkinter as tk
except ImportError:
    #python 3
    import tkinter as tk
    print ("Loaded library tkinter (probably running on Python 3.x)")
else:
    print ("Loaded library Tkinter (probably running on Python 2.x)")

import time

#import RPi.GPIO as GPIO

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
GPIO_CICALINA = 1
GPIO_SIM_1_STATUS = 2
GPIO_SIM_2_STATUS = 3
GPIO_CURRENT_1 = 4
GPIO_CURRENT_2 = 5

fullscren_mode = "false"

######################################################################################################
######################################################################################################
#Constants
######################################################################################################
######################################################################################################

#Color constants
RED =   "#ff0000"
GREEN = "#00ff00"
BLUE =  "#0000ff"
WHITE = "#ffffff"
BLACK = "#000000"
GRAY =  "#8D8D8D"
ORANGE= "#ff8000"
YELLOW= "#ffff00"

#LOOP state constants
LOOP_STANDBY_INIT = "Standby..."
LOOP_STANDBY = "Standby"
LOOP_ARMING_INIT = "Arming..."
LOOP_ARMING = "Arming"
LOOP_ARMED_INIT = "Armed..."
LOOP_ARMED = "Armed"
LOOP_HOLE_INIT = "Hole..."
LOOP_HOLE = "Hole!"
LOOP_END_RUN_IN_INIT = "Run-in ENDING"
LOOP_END_RUN_IN = "Run-in PASS"

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
    passante per i TA e di calcolare lo stato dei Loop per verificare i buchi di erogazione'''
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
    root.after(100,timer_fast)

def timer_slow():
    '''Richiamata circa 2 volte al secondo, aggiorna la grafica e rileva il passaggio dei secondi
    per poter eseguire i countdown dovuti'''
    global countdown
    global seconds_edge_finder
    update_debug_labels()
    update_labels()
    time_time=time.time()
    if seconds_edge_finder != int(time_time):
        seconds_edge_finder = int(time_time)
        if countdown[1] != 0 : countdown[1] -= 1
        if countdown[2] != 0 : countdown[2] -= 1
    root.after(500,timer_slow)

def test_simulator(the_gpio):
    '''Questa funzione rileva lo stato del simulatore collegato al pin passato come argomento'''
    #if (GPIO.input(the_gpio) == False) :
    if 1==1 :
        return SIMULATOR_ON
    else:
        return SIMULATOR_OFF

def test_ta(the_gpio):
    '''Questa funzione ricerca il passaggio di corrente sul TA collegato al pin passato come
    argomento, per massimo 20 ms'''
    for x in range(0,20):
        #if (GPIO.input(the_gpio) == False) :
        if 1==1 :
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
    -Lo stato di erogazione del simulatore'''
    if actual_status == LOOP_STANDBY_INIT:
        countdown[loop] = 0
        actual_status = LOOP_STANDBY
    elif actual_status == LOOP_STANDBY:
        if ta == CURRENT_PRESENT:
            actual_status = LOOP_ARMING_INIT
        if simulator == SIMULATOR_ON:
            actual_status = LOOP_ARMING_INIT
    elif actual_status == LOOP_ARMING_INIT:
        countdown[loop] = 300    #Tempo autoarm
        actual_status = LOOP_ARMING
    elif actual_status == LOOP_ARMING:
        if countdown[loop] == 0:
            actual_status = LOOP_ARMED_INIT
        if simulator == SIMULATOR_OFF or ta == CURRENT_ABSENT:
            actual_status = LOOP_STANDBY_INIT
    elif actual_status == LOOP_ARMED_INIT:
        countdown[loop] = 5460    #Tempo run-in
        actual_status = LOOP_ARMED
    elif actual_status == LOOP_ARMED:
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
        if ta == CURRENT_ABSENT:
            actual_status = LOOP_HOLE_INIT
        if countdown[loop] == 0:
            actual_status = LOOP_END_RUN_IN_INIT
    elif actual_status == LOOP_HOLE_INIT:
        countdown[loop] = 0
        event_logger("Logic","Hole in loop " + str(loop))
        actual_status = LOOP_HOLE
    elif actual_status == LOOP_HOLE:
        if simulator == SIMULATOR_OFF:
            actual_status = LOOP_STANDBY_INIT
    elif actual_status == LOOP_END_RUN_IN_INIT:
        countdown[loop] = -1
        actual_status = LOOP_END_RUN_IN
    elif actual_status == LOOP_END_RUN_IN:
        pass
    else:
        pass
    return actual_status

def click_lblWallpaper(event=None):
    '''Se clicco nello sfondo dell'applicazione, questa si chiude'''
    event_logger("Event","exit via click_lblWallpaper")
    root.destroy()
    
def click_btnDisarm1():
    event_logger("Event","Manual disarm loop 1")
    global LOOP_1_status
    LOOP_1_status = LOOP_STANDBY_INIT

def click_btnDisarm2():
    event_logger("Event","Manual disarm loop 2")
    global LOOP_2_status
    LOOP_2_status = LOOP_STANDBY_INIT

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
    stringone = "Now:" + str(time_now) + " | Time:" + str(time_time) + "s | Processor: " + str(time_clock) + "ms | Counter: " + str(fast_counter) + " ticks | Delta: " + str(delta*1000) + " ms"
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

def text_composer(status,countdown):
    '''Il compositore dei testi che finiranno nelle label dello stato dei Loop'''
    if countdown < 0:
        mytext=status
        mytext += ": "
        mytext += time.strftime("%H:%M:%S", time.gmtime(abs(countdown)))
    elif countdown == 0:
        mytext=status
    elif countdown < 3600:
        mytext=status
        mytext += ": "
        mytext += time.strftime('%M:%S"', time.gmtime(countdown))
    elif countdown >= 3600:
        mytext=status
        mytext += ": "
        mytext += time.strftime("%H:%M", time.gmtime(countdown))
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
    
def setup_GPIO():
    '''Inizializzazione GPIO'''
    # #GPIO_CICALINA = 1
    # #GPIO_SIM_1_STATUS = 2
    # #GPIO_SIM_2_STATUS = 3
    # #GPIO_CURRENT_1 = 4
    # #GPIO_CURRENT_2 = 5
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.OUT)
    pass

######################################################################################################
######################################################################################################
#Main
######################################################################################################
######################################################################################################

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

#Le prossime tre righe costruiscono la linea grafica su Loop1
canvas.create_line(300,101,1091,101)
canvas.create_line(300,102,1091,102)
canvas.create_line(300,103,1091,103) 

#Wallpaper di tutta la finestra
lblWallpaper = tk.Label(root)
lblWallpaper.place(x=0, y=0, height=screen_height, width=screen_width)
root._img1 = tk.PhotoImage(file="./monitor_solare_wallpaper3.png")
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
lblDescr1.place(x=300, y=40, height=60, width=260)
lblDescr1.configure(background=WHITE, anchor='w')
lblDescr1.configure(font=fontDescrLabel)
lblDescr1.configure(text=''' Simulator 1''')
lblSim1 = tk.Label(root)
lblSim1.place(x=300, y=105, height=140, width=791)
lblSim1.configure(background=GREEN)
lblSim1.configure(font=fontLabel)
lblSim1.configure(text='''loading''')
btnDisarm1 = tk.Button(root)
btnDisarm1.place(x=800, y=40, height=60, width=291)
btnDisarm1.configure(activebackground="#d9d9d9")
btnDisarm1.configure(takefocus="0")
btnDisarm1.configure(command=click_btnDisarm1)
btnDisarm1.configure(font=fontButton)
btnDisarm1.configure(text='''Disarm''')
#Predisposizione progressbar 
#TProgressbar1 = tk.Progressbar(root)
#TProgressbar1.place(relx=0.37, rely=0.26, relwidth=0.62, relheight=0.0, height=19)
#TProgressbar1.configure(length="790")

#Loop2
lblDescr2 = tk.Label(root)
lblDescr2.place(x=300, y=300, height=60, width=260)
lblDescr2.configure(background=WHITE, anchor='w')
lblDescr2.configure(font=fontDescrLabel)
lblDescr2.configure(text=''' Simulator 2''')
canvas.create_line(300,361,1091,361)
canvas.create_line(300,362,1091,362)
canvas.create_line(300,363,1091,363) 
lblSim2 = tk.Label(root)
lblSim2.place(x=300, y=365, height=140, width=791)
lblSim2.configure(background=GREEN)
lblSim2.configure(font=fontLabel)
lblSim2.configure(text='''loading...''')
btnDisarm2 = tk.Button(root)
btnDisarm2.place(x=800, y=300, height=60, width=291)
btnDisarm2.configure(activebackground="#d9d9d9")
btnDisarm2.configure(font=fontButton)
btnDisarm2.configure(command=click_btnDisarm2)
btnDisarm2.configure(takefocus="0")
btnDisarm2.configure(text='''Disarm''')
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
event_logger("System","Boot")

#Avvio i due timer
timer_fast()
timer_slow()

#Passo il controllo al sistema ad eventi
root.mainloop()
