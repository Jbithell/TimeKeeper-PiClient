import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(2,GPIO.OUT) #YellowLed
GPIO.setup(17,GPIO.OUT) #RedLed

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP) #EmergencyStop
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Key
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Start

#Starting Values
GPIO.output(2, GPIO.HIGH)
GPIO.output(17, GPIO.LOW)

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

while True:
    if keyOn():
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