import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(2,GPIO.OUT) #YellowLed
GPIO.setup(17,GPIO.OUT) #RedLed
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP) #EmergencyStop
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Key
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Start



while True:
    if GPIO.input(4):
        print('Stop Button Pressed')
    if GPIO.input(3) == False:
        print('Key Switched')
    if GPIO.input(27) == False:
        print('Start Button Pressed')

    GPIO.output(17, GPIO.LOW)
    GPIO.output(2, GPIO.LOW)
    time.sleep(1)