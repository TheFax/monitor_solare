#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python 2.7 (perchè GPIO su BananaPI non è supportato da Python 3
#FAX 12/12/2016

'''
Installing GPIO library on Banana Pi:

LINK: http://wiki.lemaker.org/BananaPro/Pi:GPIO_library

step 1: git clone https://github.com/LeMaker/RPi.GPIO_BP -b bananapi
step 2: sudo apt-get update
step 3: sudo apt-get install python-dev
step 4: cd RPi.GPIO_BP
step 5: python setup.py install                 
step 6; sudo python setup.py install
'''

'''
Installing PIL
step 1: sudo apt-get install python-pip
step 2: sudo pip install Pillow
'''

#Librerie da importare
try:
    #Python 2
    import Tkinter as tk
except ImportError:
    #python 3
    import tkinter as tk
    print ("Loaded library tkinter (running on Python 3.x)")
else:
    print ("Loaded library Tkinter (running on Python 2.x)")

import time

#import RPi.GPIO as GPIO   #https://github.com/LeMaker/RPi.GPIO_BP

#Fonts
fontButton =       "-family {Cantarell}     -size 24 -weight bold -slant roman -underline 0 -overstrike 0"
fontDescrLabel  =  "-family {Nimbus Sans L} -size 34              -slant roman -underline 0 -overstrike 0"
fontLabel  =       "-family {Nimbus Sans L} -size 54 -weight bold -slant roman -underline 0 -overstrike 0"
fontBottomLabel  = "-family {Nimbus Sans L} -size 28              -slant roman -underline 0 -overstrike 0"

GPIO_CICALINA = 1
GPIO_SIM_1_STATUS = 2
GPIO_SIM_2_STATUS = 3
GPIO_TA_1 = 4
GPIO_TA_2 = 5

fast_counter = 0 

RED =   "#ff0000"
GREEN = "#00ff00"
BLUE =  "#0000ff"
WHITE = "#ffffff"
BLACK = "#000000"
ORANGE= "#ff8000"
YELLOW= "#ffff00"

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

LOOP_1_status = LOOP_STANDBY_INIT
LOOP_2_status = LOOP_STANDBY_INIT

SIMULATOR_ON = "ON"
SIMULATOR_OFF = "OFF"

SIMULATOR_1_status = SIMULATOR_OFF
SIMULATOR_2_status = SIMULATOR_OFF

CURRENT_PRESENT = "Flowing"
CURRENT_ABSENT = "Not flowing"

TA_1_status = CURRENT_ABSENT
TA_2_status = CURRENT_ABSENT

countdown = [ 0 , 0 , 0]

second_edge_finder = 0

def timer_fast():
    global fast_counter
    global SIMULATOR_1_status
    global SIMULATOR_2_status
    global TA_1_status
    global TA_2_status
    global LOOP_1_status
    global LOOP_2_status
    fast_counter += 1
    SIMULATOR_1_status = test_simulator (GPIO_SIM_1_STATUS)
    SIMULATOR_2_status = test_simulator (GPIO_SIM_2_STATUS)
    TA_1_status = test_ta (GPIO_TA_1)
    TA_2_status = test_ta (GPIO_TA_2)
    LOOP_1_status = main_logic(1, LOOP_1_status, TA_1_status, SIMULATOR_1_status)
    LOOP_2_status = main_logic(2, LOOP_2_status, TA_2_status, SIMULATOR_2_status)
    root.after(100,timer_fast)

def timer_slow():
    global countdown
    global second_edge_finder
    update_debug_labels()
    update_labels()
    time_time=time.time()
    if second_edge_finder != int(time_time):
        second_edge_finder = int(time_time)
        if countdown[1] != 0 : countdown[1] -= 1
        if countdown[2] != 0 : countdown[2] -= 1
    root.after(500,timer_slow)

def test_simulator(the_gpio):
    #if (GPIO.input(the_gpio) == False) :
    if 1==1 :
        return SIMULATOR_ON
    else:
        return SIMULATOR_OFF

def test_ta(the_gpio):
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
##    LOOP_STANDBY_INIT = "Standby..."
##    LOOP_STANDBY = "Standby"
##    LOOP_ARMING_INIT = "Arming..."
##    LOOP_ARMING = "Arming"
##    LOOP_ARMED_INIT = "Armed..."
##    LOOP_ARMED = "Armed"
##    LOOP_HOLE_INIT = "Hole..."
##    LOOP_HOLE = "Hole!"
##    LOOP_END_RUN_IN_INIT = "Run-in: ENDING"
##    LOOP_END_RUN_IN = "Run-in: END"
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

def click_lblLogo(event=None):
    event_logger("Event","exit via click_lblLogo")
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
    print "[",time.strftime('%H:%M:%S'),"] ", group, ":", description
    text = "[" + time.strftime('%H:%M:%S') + "] " + group + " - " + description
    lblBottom.configure(text=text)
 
def update_debug_labels():
    global fast_counter
    time_now = time.strftime('%H:%M:%S')  #20:33:59
    time_time = time.time()               #1483472098.44
    time.sleep(0.002)                     #delay 2ms
    time_time2 = time.time()
    time_clock = time.clock() * 1000      #per quanti millisecondi ho occupato il uP?
    delta = time_time2 - time_time
    stringone = "Now:" + str(time_now) + " | Time:" + str(time_time) + "s | Processor: " + str(time_clock) + "ms | Counter: " + str(fast_counter) + " ticks | Delta: " + str(delta*1000) + " ms"
    lblClock.config(text=stringone)
    
def update_labels():
    mytext=text_composer(LOOP_1_status,countdown[1])
    lblSim1.config(text=mytext)
    mycolor=color_composer(LOOP_1_status)
    lblSim1.configure(background=mycolor)

    mytext=text_composer(LOOP_2_status,countdown[2])
    lblSim2.config(text=mytext)
    mycolor=color_composer(LOOP_2_status)
    lblSim2.configure(background=mycolor)

def text_composer(status,countdown):
    mytext=status
    if countdown < 0:
        mytext += ": "
        mytext += time.strftime("%H:%M:%S", time.gmtime(abs(countdown)))        
    elif countdown > 3600:
        mytext += ": "
        mytext += time.strftime("%H:%M", time.gmtime(countdown))
    else:
        mytext += ": "
        mytext += time.strftime('%M:%S"', time.gmtime(countdown))
    return mytext

def color_composer(status):
    if status==LOOP_ARMING:
        return YELLOW
    if status==LOOP_STANDBY:
        return WHITE
    if status==LOOP_ARMED:
        return GREEN
    if status==LOOP_HOLE:
        return ORANGE
    if status==LOOP_END_RUN_IN:
        return GREEN
    
def setup_GPIO():
##GPIO_CICALINA = 1
##GPIO_SIM_1_STATUS = 2
##GPIO_SIM_2_STATUS = 3
##GPIO_TA_1 = 4
##GPIO_TA_2 = 5
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.IN)
    #GPIO.setup(PIN_NUM,GPIO.OUT)
    pass

root = tk.Tk()
root.title("Solar Monitor")
root.minsize(300,300)
root.geometry("1280x768")
root.configure(background='#ffffff')

#A pieno schermo?
#root.attributes("-fullscreen", True)   #http://effbot.org/tkinterbook/wm.htm

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
print "Screen width = ", str(screen_width)
print "Screen height = ", str(screen_height)

canvas = tk.Canvas(root)
canvas.config(background=WHITE)
canvas.place(x=0, y=0, height=screen_height, width=screen_width)

#La seguente riga di codice traccia una diagonale sullo schermo. Utile per vedere l'overscan.
#canvas.create_line(0,0,screen_width,screen_height) 

##btnExit = tk.Button(root)
##btnExit.place(x=30, y=260, height=46, width=207)
##btnExit.configure(activebackground="#d9d9d9")
##btnExit.configure(command=root.destroy)
##btnExit.configure(font=fontButton)
##btnExit.configure(text='''Exit''')

lblDescr1 = tk.Label(root)
lblDescr1.place(x=300, y=40, height=60, width=791)
lblDescr1.configure(background=WHITE, anchor='w')
lblDescr1.configure(font=fontDescrLabel)
lblDescr1.configure(text='''Simulator 1''')
canvas.create_line(300,101,1091,101)
canvas.create_line(300,102,1091,102)
canvas.create_line(300,103,1091,103) 
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

lblDescr2 = tk.Label(root)
lblDescr2.place(x=300, y=300, height=60, width=791)
lblDescr2.configure(background=WHITE, anchor='w')
lblDescr2.configure(font=fontDescrLabel)
lblDescr2.configure(text='''Simulator 2''')
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

lblBottom = tk.Label(root)
lblBottom.place(x=30, y=560, height=90, width=screen_width-30-30)
lblBottom.configure(background="#808080")
lblBottom.configure(font=fontBottomLabel)
lblBottom.configure(text='''Solar Monitor''')
 
#TProgressbar1 = tk.Progressbar(root)
#TProgressbar1.place(relx=0.37, rely=0.26, relwidth=0.62, relheight=0.0, height=19)
#TProgressbar1.configure(length="790")
# 
#TProgressbar2 = tk.Progressbar(root)
#TProgressbar2.place(relx=0.37, rely=0.70, relwidth=0.62, relheight=0.0, height=19)
#TProgressbar2.configure(length="790")

lblClock = tk.Label(root, font=("Helvetica", 36))
lblClock = tk.Label(text='Waiting function call...')
lblClock.place(x=300, y=260, height=20, width=791)

lblLogo = tk.Label(root)
lblLogo.place(x=20, y=485, height=238, width=226)
#lblLogo.configure(background="#ffffff")
root._img1 = tk.PhotoImage(file="./socomec_logo-ba-service_160x145.png")
lblLogo.configure(image=root._img1)
lblLogo.configure(text="")
lblLogo.bind("<Button-1>",click_lblLogo)

#btnEmergency = tk.Button(root, text='EMERGENCY', width=25, command=root.destroy)
#btnEmergency.place(x = 10, y = 10 , width=100, height=55)

setup_GPIO()
event_logger("System","Boot")
timer_fast()
timer_slow()

root.mainloop()
