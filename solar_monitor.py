#!/usr/bin/python
# -*- coding: utf-8 -*-

#Python 2.7 (perchè GPIO su BananaPI non è supportato da Python 3
#FAX 12/12/2016

'''
Installing GPIO library on Banana Pi:

LINK: http://wiki.lemaker.org/BananaPro/Pi:GPIO_library

git clone https://github.com/LeMaker/RPi.GPIO_BP -b bananapi
sudo apt-get update
sudo apt-get install python-dev
cd RPi.GPIO_BP
python setup.py install                 
sudo python setup.py install
'''

#import RPi.GPIO as GPIO   #https://github.com/LeMaker/RPi.GPIO_BP
import Tkinter as tk   #tkinter -> python 3 ; Tkinter -> python 2.7
import time

#PIN_NUM = 7
counter = 0 

RED =   "#ff0000"
GREEN = "#00ff00"
BLUE =  "#0000ff"
WHITE = "#ffffff"
BLACK = "#000000"

STANDBY_INIT = "Standby..."
STANDBY = "Standby"
ARMED_INIT = "Armed..."
ARMED = "Armed"
ARMING_INIT = "Arming..."
ARMING = "Arming"
HOLE_INIT = "Hole..."
HOLE = "Hole!"

status_simulator_1 = STANDBY_INIT
status_simulator_2 = STANDBY_INIT

def timer_fast():
    #global root
    global counter
    counter += 1
    root.after(50,timer_fast)

def timer_slow():
    main_logic()
    update_debug_labels()
    update_labels()
    root.after(700,timer_slow)

def click_lblSim1(event=None):
    global counter
    counter = 0
    lblBottom.configure(text=event)
    global status_simulator_1
    status_simulator_1=ARMED_INIT
    
def click_btnDisarm():
    global status_simulator_1
    status_simulator_1=STANDBY_INIT

def main_logic():
    global status_simulator_1
    global status_simulator_2
    status_simulator_1 = update_logic(status_simulator_1,1)
    status_simulator_2 = update_logic(status_simulator_2,1)


def update_logic(status, data):
    if status == STANDBY_INIT:
        status = STANDBY
    elif status == STANDBY:
        pass
    elif status == ARMED_INIT:
        status = ARMED
    elif status == ARMED:
        pass
    elif status == ARMING_INIT:
        status = ARMING
    elif status == ARMING:
        pass
    else:
        pass
    return status

def update_debug_labels():
    global counter
    time_now = time.strftime('%H:%M:%S')
    time_time = time.time()
    time.sleep(0.002)
    time_time2 = time.time()
    time_clock = time.clock() * 1000
    delta = time_time2 - time_time
    stringone = "Now:" + str(time_now) + " | Time:" + str(time_time) + "s | Processor: " + str(time_clock) + "ms | Counter: " + str(counter) + " ticks | Delta: " + str(delta*1000) + " ms"
    lblClock.config(text=stringone)
    
def update_labels():
    lblSim1.config(text=status_simulator_1)
    #lblSim1.configure(background=WHITE)
    lblSim2.config(text=status_simulator_2)
    #lblSim2.configure(background=WHITE)

#GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(PIN_NUM,GPIO.IN)

fontButton = "-family {Cantarell} -size 24 -weight bold -slant roman -underline 0 -overstrike 0"
fontDescrLabel  = "-family {Nimbus Sans L} -size 34 -slant roman -underline 0 -overstrike 0"
fontLabel  = "-family {Nimbus Sans L} -size 94 -weight bold -slant roman -underline 0 -overstrike 0"
fontBottomLabel  = "-family {Nimbus Sans L} -size 74 -weight bold -slant roman -underline 0 -overstrike 0"

root = tk.Tk()
root.title("Solar Monitor")
root.minsize(300,300)
root.geometry("1280x768")
root.configure(background='#ffffff')
#root.attributes("-fullscreen", True)   #http://effbot.org/tkinterbook/wm.htm

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
#print "Screen width = ", str(screen_width)
#print "Screen height = ", str(screen_height)

canvas = tk.Canvas(root)
canvas.config(background=WHITE)
canvas.place(x=0, y=0, height=screen_height, width=screen_width)
canvas.create_line(0,0,screen_width,screen_height) 

lblLogo = tk.Label(root)
lblLogo.place(x=20, y=20, height=238, width=226)
lblLogo.configure(background="#ffffff")
root._img1 = tk.PhotoImage(file="./socomec_logo-ba-service_160x145.png")
lblLogo.configure(image=root._img1)
lblLogo.configure(text="")

btnExit = tk.Button(root)
btnExit.place(x=30, y=260, height=46, width=207)
btnExit.configure(activebackground="#d9d9d9")
btnExit.configure(command=root.destroy)
btnExit.configure(font=fontButton)
btnExit.configure(text='''Exit''')

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
lblSim1.bind("<Button-1>",click_lblSim1)
btnDisarm1 = tk.Button(root)
btnDisarm1.place(x=800, y=40, height=60, width=291)
btnDisarm1.configure(activebackground="#d9d9d9")
btnDisarm1.configure(takefocus="0")
btnDisarm1.configure(command=click_btnDisarm)
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
btnDisarm2.configure(takefocus="0")
btnDisarm2.configure(text='''Disarm''')

lblBottom = tk.Label(root)
lblBottom.place(x=30, y=560, height=90, width=screen_width-30-30)
lblBottom.configure(background=GREEN)
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

#btnEmergency = tk.Button(root, text='EMERGENCY', width=25, command=root.destroy)
#btnEmergency.place(x = 10, y = 10 , width=100, height=55)

timer_fast()
timer_slow()

root.mainloop()
