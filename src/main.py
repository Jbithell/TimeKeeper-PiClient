import termios, fcntl, sys, os
import time
import serial
import RPi.GPIO as GPIO
import urllib, json
import MFRC522
import signal

print(sys.version)
#                   Start setting up LEDs and physical components
GPIO.setmode(GPIO.BOARD)
yellowLED = 3
redLED = 11
keySWITCH = 5  # Reversed
startBUTTON = 13  # Reversed
stopSWITCH = 7

GPIO.setup(yellowLED, GPIO.OUT)
GPIO.output(yellowLED, GPIO.LOW)

GPIO.setup(redLED, GPIO.OUT)
GPIO.output(redLED, GPIO.LOW)

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
#                   Start setting up RFID logger
def signalEndReadFunction(signal, frame):
    GPIO.cleanup()


signal.signal(signal.SIGINT, signalEndReadFunction)
MIFAREReader = MFRC522.MFRC522()
#                   End
#                   Start setting` up LCD
print("Waking LCD")
port = serial.Serial(
    "/dev/ttyUSB0",
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    writeTimeout=0,
    timeout=10,
    rtscts=False,
    dsrdtr=False,
    xonxoff=False)
print(port.isOpen())
print("LCD Port Opened - Arduino Starting Up")
for i in range(1, 11):  # Wait 11 seconds
    print(str(11 - i) + " seconds remaining")
    time.sleep(1)
print("Arduino Started Up")


def lcdprint(text):
    global port
    port.write(str(text) + "$")
    # print("Data sent to LCD: " + str(text))


lcdprint("   TIMEKEEPER      SYSTEM ONLINE")
print("LCD AWAKE")
#                   End

#                   Start setting up data connection
sessionRunning = False
sessionTimer = 0
sessionLastStart = 0  # Last time a session was started
sessionStartTime = 0 # When the timer started initially
sessionTimerRunning = False
sessionData = []


def webRequest(path, paramstring):
    if (len(paramstring) > 0):
        paramstring = "?" + paramstring + "&"
    else:
        paramstring = "?"
    url = "https://" + "jbithell.com/projects/timekeeper/api/v4/" + path + paramstring + "USERKEY=" + str(
        os.getenv('USERKEY', '')) + "&USERSECRET=" + str(os.getenv('USERSECRET', ''))
    print(url)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data


def endSession():
    global sessionRunning, sessionTimer, sessionLastStart, sessionTimerRunning, sessionData, sessionInitiatorTag
    if sessionTimerRunning:
        sessionTimer = time.time() - sessionLastStart
        sessionTimerRunning = False
        sessionLastStart = 0
        GPIO.output(redLED, GPIO.LOW)
    sessionRunning = False
    # Session timer now accurately represents the time for this session
    request = webRequest("sessions/start/", "projectid=" + str(sessionData[0]) + "&trigger=" + "Jbithell/TimeKeeper-PiClient" + "|" + "TAG:" + str(sessionInitiatorTag) + "&start=" + str(sessionStartTime) + "&duration=" + str(sessionTimer) + "&end=" + str(time.time()))
    sessionTimer = 0
    sessionData = False
    sessionRunning = False
    if request["result"]:
        return True
    else:
        return False


def getSessionData(projectID, cardReadID):
    global sessionInitiatorTag
    if cardReadID == False:
        request = webRequest("projects/get/", "id=" + str(projectID))
    elif projectID == False:
        request = webRequest("projects/get/", "RFIDid=" + str(cardReadID))
    if request["result"]:
        # Param 1: projectid, 2: 16 characters of title (exactly 16 - pad with spaces if less), 3 is the number of seconds the project currently has a its total
        if len(request["result"]["NAME"]) > 16:
            request["result"]["NAME"] = request["result"]["NAME"][0:16]
        elif len(request["result"]["NAME"]) < 16:
            for x in range(0, 16 - len(request["result"]["NAME"])):
                request["result"]["NAME"] = str(request["result"]["NAME"]) + " "  # Add spaces

        if request["result"]["RFIDTAG"] != "":
            sessionInitiatorTag = request["result"]["RFIDTAG"]
        else:
            sessionInitiatorTag = False
        return [request["result"]["ID"], request["result"]["NAME"], request["result"]["TOTALTIME"]]
    else:
        return False


def is_int(input):
    try:
        num = int(input)
    except ValueError:
        return False
    return True


def hoursMinutesSeconds(input):
    # https://stackoverflow.com/questions/775049/python-time-seconds-to-hms
    m, s = divmod(input, 60)
    h, m = divmod(m, 60)

    s = int(round(s))
    m = int(round(m))
    h = int(round(h))

    if (h < 1):
        h = "00"
    if (m < 1):
        m = "00"
    if (s < 1):
        s = "00"

    if (h < 10):
        h = "0" + str(h)  # Pad
    if (m < 10):
        m = "0" + str(m)  # Pad
    if (s < 10):
        s = "0" + str(s)  # Pad
    return (str(h), str(m), str(s))


#                   End

#                   Start main loop
currentMode = 0  # powered off
while True:
    if GPIO.input(keySWITCH):  # System is powered down
        if currentMode != 0:  # If it's doing anything else power it down
            print("Powering down")
            time.sleep(0.1)  # Big old debounce
            # System has literally just been powered down on this iteration of main loop
            GPIO.output(redLED, GPIO.LOW)
            GPIO.output(yellowLED, GPIO.LOW)
            if sessionRunning:
                endSession()  # Just in case you left one running when powering down
            lcdprint("   TIMEKEEPER                 v6")
            currentMode = 0
    elif currentMode == 0:  # Keyswitch is on but system technically powered down
        # System is getting powered on
        print("Powering up")
        time.sleep(0.05)  # Debounce
        GPIO.output(yellowLED, GPIO.HIGH)  # this is the power indicator
        lcdprint("   TIMEKEEPER   ENTER PROJECT ID")
        currentMode = 1  # Entry menu
        projectIDEntered = ""
        cardReadID = ""
        while True:
            #      Keypad
            try:
                c = sys.stdin.read(1)
                if is_int(c):
                    projectIDEntered += str(c)
                    print("Got " + str(c))
                    lcdprint("   TIMEKEEPER   " + projectIDEntered)
                    time.sleep(0.01)  # Debounce
                elif c == "\n" and len(projectIDEntered) > 0:  # Can't hit enter immediately
                    break
            except IOError:
                pass
            # EndKeypad

            #       RFID
            (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                cardReadID = (str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3]))
                print(cardReadID)
                break
            # EndRFID

            if GPIO.input(keySWITCH):  # Power key has been turned to off
                time.sleep(0.2)  # Debounce
                print("Key switched back")
                projectIDEntered = ""
                cardReadID = ""
                break
        if GPIO.input(keySWITCH) != True and (
                        len(projectIDEntered) > 0 or len(
                    cardReadID) > 0):  # Check we didn't break because of power switch
            if len(cardReadID) > 0:
                # They've swiped an RFID thing not actually used a project ID so we can ignore the project ID and make a slightly different request
                print("Loading RFID " + cardReadID)
                lcdprint("TIMEKEEPER LOAD+" + "   RFID SWIPE   ")
                sessionData = getSessionData(False, cardReadID)
            else:
                print("Loading " + projectIDEntered)
                lcdprint("TIMEKEEPER  LOAD" + projectIDEntered)
                sessionData = getSessionData(projectIDEntered, False)
            if sessionData:
                lcdprint(sessionData[1] + "{}:{}:{}".format(*hoursMinutesSeconds(sessionData[2])) + "   READY")
                currentMode = 2  # Session start/running page
            else:
                currentMode = 0
    elif currentMode == 2:
        if sessionRunning:
            # There's a session running so we want to check for various stuff

            if GPIO.input(startBUTTON) != True:
                # Someone wants to end the session
                print("Ending session")
                time.sleep(0.2)  # Debounce
                endSession()
                currentMode = 0
            elif GPIO.input(stopSWITCH) and sessionTimerRunning:
                # So we're still running the timer but it needs to be paused
                print("Pause")
                time.sleep(0.05)  # Debounce
                sessionTimer += time.time() - sessionLastStart  # add the time to the thing
                sessionTimerRunning = False
                GPIO.output(redLED, GPIO.LOW)
            elif GPIO.input(stopSWITCH) != True and sessionTimerRunning != True:
                # Need to restart the timer
                print("Resume")
                time.sleep(0.05)  # Debounce
                sessionLastStart = time.time()
                sessionTimerRunning = True
                GPIO.output(redLED, GPIO.HIGH)
            # Print the status of the timer with a countup
            if sessionTimerRunning:
                sessionTimerTemp = sessionTimer + (time.time() - sessionLastStart)
                GPIO.output(redLED, GPIO.HIGH)
                time.sleep(0.3)  # Try not to kill LCD by constantly sending it updates
                GPIO.output(redLED, GPIO.LOW)
                time.sleep(0.3)  # Try not to kill LCD by constantly sending it updates
            else:
                #Timer is paused
                sessionTimerTemp = sessionTimer
                time.sleep(0.5)  # Try not to kill LCD by constantly sending it updates

            if sessionRunning: #Session could have been stopped by the time you get down here
                lcdprint(sessionData[1] + "{}:{}".format(
                    *hoursMinutesSeconds(sessionData[2] + sessionTimerTemp)) + "   " + "{}:{}:{}".format(
                    *hoursMinutesSeconds(sessionTimerTemp)))  # Keep screen updated


        else:
            if GPIO.input(stopSWITCH):
                time.sleep(0.2) #Debounce
                print("Release stop")
                lcdprint("  RELEASE STOP  !!!!!!!!!!!!!!!!") #We can't start a session when the stop thing is pressed down
                while GPIO.input(stopSWITCH):
                    #Basically sit in a huge loop until either stop is released or they power down
                    if GPIO.input(keySWITCH):
                        time.sleep(0.05) #Debounce
                        #Poweroff basically
                        break
                if GPIO.input(keySWITCH) != True:
                    time.sleep(0.5)  # Debounce
                    lcdprint(sessionData[1] + "{}:{}:{}".format(*hoursMinutesSeconds(sessionData[2])) + "   READY")
            elif GPIO.input(startBUTTON) != True:
                #Start running session
                print("Starting")
                time.sleep(2)  # Debounce - this one tends to be problematic
                sessionLastStart = time.time()
                sessionStartTime = time.time()
                sessionTimerRunning = True
                sessionRunning = True
                GPIO.output(redLED, GPIO.HIGH)

            #      Keypad to detect back button
            try:
                c = sys.stdin.read(1)
                print(c)

            except IOError:
                pass
            # EndKeypad