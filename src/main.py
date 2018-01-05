import termios, fcntl, sys, os
import time
import serial


fd = sys.stdin.fileno()  # Start system to gather text
oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)



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
print ("LCD AWAKE")
lcdprint("TEST TEST TEST")
print("Starting text grabber")

try:

    while 1:
        try:
            c = sys.stdin.read(1)
            print "Got character", repr(c)
        except IOError:
            pass
finally:
    print("Crashing out")
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
