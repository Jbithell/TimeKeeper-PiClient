import RPi.GPIO as GPIO
import time
import tkinter as tk
from PIL import ImageTk, Image
import os



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

root = tk.Tk()
app = mainApp(root)
frame = tk.Frame(root)
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

    if keyOn():
        root.configure(background='white')  # Set window background colour
        loadingLabel.pack(fill=tk.BOTH, expand=1)
        powerOffLabel.pack_forget()

        GPIO.output(2, GPIO.HIGH)
        #Main program logic
        if stopOn():
            GPIO.output(17, GPIO.HIGH)
        else:
            GPIO.output(17, GPIO.LOW)
    else:
        #System Shut Down
        GPIO.output(2, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)

        root.configure(background='black')  # Set window background colour
        powerOffLabel.pack(fill=tk.BOTH, expand=1) #Show closed image
        loadingLabel.pack_forget()
