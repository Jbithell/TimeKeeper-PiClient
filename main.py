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
    print "pressed", repr(event.char)

root = tk.Tk()
app = mainApp(root)
frame = tk.Frame(root)
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

powerOffLabel = tk.Label(frame, image=powerOffImage, bg='black')
powerOffLabel.image = powerOffImage
loadingLabel = tk.Label(frame, image=loadingImage, bg='black')
loadingLabel.image = loadingImage



while True:
    root.update_idletasks()
    root.update()

    if keyOn() != True:
        mode = 0
    if mode == 0 and keyOn():
        GPIO.output(2, GPIO.HIGH) #Power on light
        mode = 1 #boot

    if mode == 0:
        # System Shut Down
        GPIO.output(2, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)

        for item in frame.winfo_children():
            #Clear the frame
            item.pack_forget()
        root.configure(background='black')  # Set window background colour
        powerOffLabel.pack(fill=tk.BOTH, expand=1)  # Show closed image
    elif mode == 1:
        for item in frame.winfo_children():
            #Clear the frame
            item.pack_forget()
        root.configure(background='white')  # Set window background colour
        loadingLabel.pack(fill=tk.BOTH, expand=1)

        time.sleep(2) #Loading

        mode = 2 #Skip straight to timekeeper from main menu
    elif mode == 2:
        frame.configure(background='white')  # Set window background colour
        for item in frame.winfo_children():
            #Clear the frame
            item.pack_forget()
        #Main program logic
        if stopOn():
            GPIO.output(17, GPIO.HIGH)
        else:
            GPIO.output(17, GPIO.LOW)
    elif mode == 3:
        root.configure(background='black')  # Set window background colour
        for item in frame.winfo_children():
            #Clear the frame
            item.pack_forget()
        #Main program logic
        if stopOn():
            GPIO.output(17, GPIO.HIGH)
        else:
            GPIO.output(17, GPIO.LOW)
    else:
        sys.exit()