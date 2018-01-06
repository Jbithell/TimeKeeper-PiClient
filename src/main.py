import termios, fcntl, sys, os
import time
import serial
import RPi.GPIO as GPIO

#                   Start setting up LEDs and physical components
GPIO.setmode(GPIO.BCM)
yellowLED = 2
redLED = 17
keySWITCH = 3 #Reversed
startBUTTON = 27 #Reversed
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
#                   End

#                   Start setting up data connection
sessionRunning = False
sessionTimer = 0
sessionLastStart = 0 #Last time a session was started
sessionTimerRunning = False
sessionData = []
def endSession():
    global sessionRunning, sessionTimer, sessionLastStart, sessionTimerRunning
    if sessionTimerRunning:
        sessionTimer = time.time() - sessionLastStart
        sessionTimerRunning = False
        sessionLastStart = 0
        GPIO.output(redLED, GPIO.LOW)
    sessionRunning = False
    #Session timer now acuratley represents the time for this session


    sessionTimer = 0
    return True
    #End a session if theres on running
def getSessionData(projectID):
    print(projectID)
    return [projectID, "TEST TEST TEST"]
    #Get data on a session that's about to begin
#                   End

#                   Start main loop
currentMode = 0 #powered off
while True:
    print("MODE " + str(currentMode))
    if GPIO.input(keySWITCH): #System is powered down
        if currentMode != 0:
            #System has literally just been powered down on this iteration of main loop
            GPIO.output(redLED, GPIO.LOW)
            GPIO.output(yellowLED, GPIO.LOW)
            endSession() #Just in case you left one running when powering down
            lcdprint("   TIMEKEEPER                 v6")
            currentMode = 0
    elif currentMode == 0: #Keyswitch is on but system technically powered down
        #System is getting powered on
        GPIO.output(yellowLED, GPIO.HIGH) #this is the power indicator
        lcdprint("   TIMEKEEPER   ENTER PROJECT ID")
        currentMode = 1 #Entry menu
        projectIDEntered = ""
        while True:
            try:
                c = sys.stdin.read(1)
                print(str(c))
                if isinstance(c, (int, long)):
                    projectIDEntered += str(c)
                    lcdprint("   TIMEKEEPER   " + projectIDEntered)
                elif c == "\n":
                    break
            except IOError:
                pass
            if GPIO.input(keySWITCH): #Power key has been turned to off
                break
        if GPIO.input(keySWITCH) != True: #Check we didn't break because of power switch
            lcdprint("TIMEKEEPER  LOAD" + projectIDEntered)
            sessionData = getSessionData(projectIDEntered)
            lcdprint(sessionData[1])
            currentMode = 2 #Session start/running page
    elif currentMode == 2:
        if sessionRunning:
            #There's a session runnig so we want to check for various stuff
            if GPIO.input(startBUTTON) != True:
                #Someone want's to end the session
                endSession()
                currentMode = 0
            elif GPIO.input(stopSWITCH) and sessionTimerRunning:
                #So we're still running the timer but it needs to be paused
                sessionTimer += time.time()-sessionLastStart #add the time to the thing
                sessionTimerRunning = False
                GPIO.output(redLED, GPIO.LOW)
            elif GPIO.input(stopSWITCH) != True and sessionTimerRunning != True:
                #Need to restart the timer
                sessionLastStart = time.time()
                sessionTimerRunning = True
                GPIO.output(redLED, GPIO.HIGH)
        else:
            if GPIO.input(stopSWITCH):
                lcdprint("  RELEASE STOP  !!!!!!!!!!!!!!!!") #We can't start a session when the stop thing is pressed down
            elif GPIO.input(startBUTTON) != True:
                #Start running session
                sessionLastStart = time.time()
                sessionTimerRunning = True
                sessionRunning = True
                GPIO.output(redLED, GPIO.HIGH)