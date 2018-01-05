import termios, fcntl, sys, os
import time
import Adafruit_CharLCD as LCD

fd = sys.stdin.fileno()  # Start system to gather text

# Raspberry Pi configuration:
lcd_rs = 27  # Change this to pin 21 on older revision Raspberry Pi's
lcd_en = 22
lcd_d4 = 25
lcd_d5 = 24
lcd_d6 = 23
lcd_d7 = 18
lcd_red = 4
lcd_green = 17
lcd_blue = 7  # Pin 7 is CE1

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                              lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue)

print("DATA")
while True:
    lcd.set_color(1.0, 0.0, 0.0)
    lcd.clear()
    lcd.message('RED')
    time.sleep(3.0)

    lcd.set_color(0.0, 1.0, 0.0)
    lcd.clear()
    lcd.message('GREEN')
    time.sleep(3.0)

    lcd.set_color(0.0, 0.0, 1.0)
    lcd.clear()
    lcd.message('BLUE')
    time.sleep(3.0)

    lcd.set_color(1.0, 1.0, 0.0)
    lcd.clear()
    lcd.message('YELLOW')
    time.sleep(3.0)

    lcd.set_color(0.0, 1.0, 1.0)
    lcd.clear()
    lcd.message('CYAN')
    time.sleep(3.0)

    lcd.set_color(1.0, 0.0, 1.0)
    lcd.clear()
    lcd.message('MAGENTA')
    time.sleep(3.0)

    lcd.set_color(1.0, 1.0, 1.0)
    lcd.clear()
    lcd.message('WHITE')
    time.sleep(3.0)

    '''

oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

try:
    while 1:
        try:
            c = sys.stdin.read(1)
            print "Got character", repr(c)
        except IOError: pass
finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

'''