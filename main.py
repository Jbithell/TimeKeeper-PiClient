import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)
print "LED on"
GPIO.output(17,GPIO.HIGH)
'''

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
input_state = GPIO.input(18)
if input_state == False:
    print('Stop Button Pressed')
    time.sleep(0.2)
'''
