import termios, fcntl, sys, os
import time
import serial
#fd = sys.stdin.fileno()  # Start system to gather text

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
while True:
    print("1")