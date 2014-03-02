#!/usr/bin/python

# Clonpi Hard Disk Duplicator code by Z3ro0ne
#Blog : z3ro0ne.blogspot.com
#Email : Saadousfar59@gmail.com
#Fb : https://www.facebook.com/Z3ro0ne
# Enjoy ..
#
# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN! We do not want the LCD to send anything to the Pi @ 5v
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V
# 16: LCD Backlight GND


#import
import RPi.GPIO as GPIO
import time
import os
import subprocess
import socket
import fcntl
import struct
import datetime
import smtplib
from email.mime.text import MIMEText

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

#define disks


# Define GPIO for button Controls

ABORT_EXIT = 3
IPSHOW = 14
LEFT = 22
MENU_SET = 2
RIGHT = 27


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

def main():
  GPIO.cleanup()
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

  GPIO.setup(RIGHT, GPIO.IN) # RIGHT Channel button
  GPIO.setup(MENU_SET, GPIO.IN) # Menu button
  GPIO.setup(LEFT, GPIO.IN) # LEFT  button

  # Initialise disMENU_SET
  lcd_init()

  # Send some test
  lcd_byte(LCD_LINE_1, LCD_CMD)
  lcd_string("Clonpi",2)
  lcd_byte(LCD_LINE_2, LCD_CMD)
  lcd_string("Duplicator",2)
  time.sleep(2)
  #home()
