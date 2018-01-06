import termios, fcntl, sys, os
import time
import serial
import RPi.GPIO as GPIO

#                   Start setting up LEDs and physical components
GPIO.setmode(GPIO.BCM)
yellowLED = 2
redLED = 17
keySWITCH = 3
startBUTTON = 27
stopSWITCH = 4

GPIO.setup(yellowLED,GPIO.OUT)
GPIO.output(yellowLED,GPIO.LOW)

GPIO.setup(redLED,GPIO.OUT)
GPIO.output(redLED,GPIO.LOW)

GPIO.setup(keySWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(startBUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stopSWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#                   Start setting up system to log text
fd = sys.stdin.fileno()  # Start system to gather text
oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
#                   End

#                   Start setting up LCD
print("Waking LCD")
port = serial.Serial(
    "/dev/ttyUSB0",
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    writeTimeout = 0,
    timeout = 10,
    rtscts=False,
    dsrdtr=False,
    xonxoff=False)
print(port.isOpen())
print("LCD Port Opened - Arduino Starting Up")
for i in range(1,11): #Wait 11 seconds
    print(str(11-i) + " seconds remaining")
    time.sleep(1)
print("Arduino Started Up")

def lcdprint(text):
    global port
    port.write(str(text) + "$")
    print("Data sent to LCD: " + str(text))
lcdprint("   TIMEKEEPER      SYSTEM ONLINE")
print ("LCD AWAKE")
#                      End



while 1:
    if (GPIO.input(keySWITCH)):
        GPIO.output(redLED, GPIO.HIGH)
        GPIO.output(yellowLED, GPIO.HIGH)
    else:
        GPIO.output(redLED, GPIO.LOW)
        GPIO.output(yellowLED, GPIO.LOW)
    '''
    try:
        c = sys.stdin.read(1)
        print "Got character", repr(c)
    except IOError:
        pass
    '''
