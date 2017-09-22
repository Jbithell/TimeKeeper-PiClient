import RPi.GPIO as GPIO
import time
import tkinter as tk
from PIL import ImageTk, Image
import os
import sys


#       SETUP TKINTER
class mainApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        pad = 3
        self._geom = '200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))
        master.configure(background='black')
    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom


def keyboardInput(event):
    key = str(event.char)

    if key == '\x08':
        key = "!" #Manually correct key backspace to exclamation mark otherwise it doesn't work

    if key != '':
        print(key)


root = tk.Tk()
app = mainApp(root)
frame = tk.Frame(root)
frame.focus_set() #Give it focus so keyboard works
frame.bind("<Key>", keyboardInput)
frame.pack(fill=tk.BOTH, expand=True)


#       SETUP BUTTONS
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(2,GPIO.OUT) #YellowLed
GPIO.setup(17,GPIO.OUT) #RedLed

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP) #EmergencyStop
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Key
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Start

#                       Starting Values
GPIO.output(2, GPIO.LOW) #Start low so it's not so startling!
GPIO.output(17, GPIO.LOW)
mode = 0 #Modes (0OFF,1MAINMENU,2PROJECTSELECT,3=TRACKINGTIME)
previousMode = 0
labels = {} #Images etc.
#                       Functions
def keyOn():
    global GPIO
    if GPIO.input(3) == False:
        return True
    else:
        return False
def startOn():
    global GPIO
    if GPIO.input(17) == False:
        return True
    else:
        return False
def stopOn():
    global GPIO
    return GPIO.input(4)


#   MAIN PROGRAM

image = Image.open("images/powerOff.jpg")
powerOffImage = ImageTk.PhotoImage(image)
image = Image.open("images/loading.jpg")
loadingImage = ImageTk.PhotoImage(image)

labels["powerOff"] = tk.Label(frame, image=powerOffImage, bg='black')
labels["powerOff"].image = powerOffImage
labels["loading"] = tk.Label(frame, image=loadingImage, bg='black')
labels["loading"].image = loadingImage

def setMode(newMode):
    global mode, previousMode,root,frame,labels,GPIO
    previousMode = mode
    mode = newMode
    print("Moved to " + str(mode) + " mode")
    for item in frame.winfo_children():
        item.pack_forget() #Clear the frame

    if mode == 0:
        GPIO.output(2, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)
        labels["powerOff"].pack(fill=tk.BOTH, expand=1)  # Show closed image
        root.configure(background='black')  # Set window background colour
    elif mode == 1:
        root.configure(background='black')  # Set window background colour
        labels["loading"].pack(fill=tk.BOTH, expand=1)
    elif mode == 2:
        root.configure(background='white')
    elif mode == 3:
        pass

setMode(0) #You have to "boot" into the powered off state
while True:
    root.update_idletasks()
    root.update()

    if keyOn() is False and mode != 0:
        setMode(0) #Powerdown system
    elif mode == 0: #Powered off
        if keyOn():
            GPIO.output(2, GPIO.HIGH)  # Power on light
            setMode(1) #Turn it on
    elif mode == 1: #Main Menu
        for i in range(1,20):
            GPIO.output(2, GPIO.LOW)
            time.sleep(0.05)
            GPIO.output(2, GPIO.HIGH)
            time.sleep(0.05)
        setMode(2) #Skip straight to timekeeper from main menu
    elif mode == 2: #Select project screen
        pass
    elif mode == 3: #Timing screen
        pass
    else:
        sys.exit()
