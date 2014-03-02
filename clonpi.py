#!/usr/bin/python

# Clonpi Disks Duplicator code by Z3ro0ne
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
  #ip()
  test()

def test():
   #if time.time() >= timelastchecked:
    #timelastchecked = time.time()+3
    mystring = ""
    size1 = ""
    mytemp = ""
    pretemp = "0x1 ["
    hdd1 = "Hdd #1:"
    hdd2 = "Hdd #2:"
    f=os.popen("fdisk -l")
    size1 = f.readlines()
    #mytime = mytime.strip()
    size1 = size1[-1]
    size1 = size1[0:16]
    line1 = hdd1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = hdd2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)

def home():
   #if time.time() >= timelastchecked:
    #timelastchecked = time.time()+3
    mystring = ""
    size1 = ""
    mytemp = ""
    pretemp = "0x1 ["
    hdd1 = "Hdd #1:"
    hdd2 = "Hdd #2:"
    f=os.popen("df / -h")
    size1 = f.readlines()
    #mytime = mytime.strip()
    size1 = size1[-1]
    size1 = size1[16:-20]
    line1 = hdd1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = hdd2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == True):
       home()
      if ( GPIO.input(LEFT) == True):
       home()
      if ( GPIO.input(MENU_SET) == True):
       menu()
###################################
## Copy Menu                     ##
###################################

def menu():
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string("<    Copy    >",2)
   else:
    if ( GPIO.input(LEFT) == True):
     off()
    if ( GPIO.input(MENU_SET) == False):
     copy_hdd1_to_hdd2()
    if ( GPIO.input(RIGHT) == False):
     erase()
    if ( GPIO.input(ABORT_EXIT) == True):
     home()

def copy_hdd1_to_hdd2():
    hdd1 = "Hdd #1:"
    hdd2 = "To Hdd #2:"
    f=os.popen("df / -h")
    size1 = f.readlines()
    size1 = size1[-1]
    size1 = size1[16:-20]
    line1 = hdd1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = hdd2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == True):
       copy_hdd2_to_hdd1()
      if ( GPIO.input(LEFT) == True):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == True):
       copy_cmd_1()
      if ( GPIO.input(ABORT_EXIT) == True):
       copy()

def copy_hdd2_to_hdd1():
   #if time.time() >= timelastchecked:
    #timelastchecked = time.time()+3
    #mystring = ""
    #size1 = ""
    #mytemp = ""
    #pretemp = "0x1 ["
    hdd1 = "Hdd #2:"
    hdd2 = "To Hdd #1:"
    f=os.popen("df / -h")
    size1 = f.readlines()
    size1 = size1[-1]
    size1 = size1[16:-20]
    line1 = hdd1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = hdd2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == True):
       copy_hdd2_to_hdd1()
      if ( GPIO.input(LEFT) == True):
       copy_hdd2_to_hdd1()
      if ( GPIO.input(MENU_SET) == True):
       copy_cmd_2()

def copy_cmd_1():
    string1 = "Hdd #1:"
    string2 = "To Hdd #2:"
    string3 = "?"
    f=os.popen("df / -h")
    size1 = f.readlines()
    size1 = size1[-1]
    size1 = size1[16:-20]
    line1 = string1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = string2 + size2 + string3
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == True):
       home()
      if ( GPIO.input(LEFT) == True):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == True):
       copy_cmd_1_confirmation()

def copy_cmd_1_confirmation():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(ABORT_EXIT) == False):
    copy()
   if ( GPIO.input(MENU_SET) == False):
    cmd_1()
    time.sleep(8)
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("***Are you sure?***",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("< No       Yes >",2)


def cmd_1():
  out_fd = open('op_log','w')
  out_fd.write("Operation log\n")
  cmd_list = ['dc3dd','if=/dev/root', 'of=/dev/sda1']
  a = subprocess.Popen(cmd_list,stderr=out_fd) # notice stderr
  a.communicate()
  log()
def log():

  while(1):
      o= open('op_log','r')
      op_status = o.readlines()
      op_status = op_status[-12]
      string1 = op_status
      string2 = "%"
      string3 = op_status
      string4 = "Copied"
      text = string3[-34:-31] + string2 + string1[-49:-44] + string4
      if (op_status[-34:-31] == "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("Operation Compl.",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string(text,1)
      if (op_status[-34:-31] != "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("!! Operation !!",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string("!!  Failed   !!",1)
      if ( GPIO.input(ABORT_EXIT) == True):
       home()
      if ( GPIO.input(MENU_SET) == True):
       menu()

def copy_cmd_2():
    string1 = "Hdd #1:"
    string2 = "To Hdd #2:"
    string3 = "?"
    f=os.popen("df / -h")
    size1 = f.readlines()
    size1 = size1[-1]
    size1 = size1[16:-20]
    line1 = string1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = string2 + size2 + string3
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == True):
       home()
      if ( GPIO.input(LEFT) == True):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == True):
       copy_cmd_1_confirmation()

def copy_cmd_2_confirmation():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(ABORT_EXIT) == False):
    copy()
   if ( GPIO.input(MENU_SET) == False):
    cmd_1()
    time.sleep(8)
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("***Are you sure?***",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("< No       Yes >",2)


def cmd_2():
  out_fd = open('op_log_1','w')
  out_fd.write("Operation log\n")
  cmd_list = ['dc3dd','if=/dev/root', 'of=/dev/sda1']
  a = subprocess.Popen(cmd_list,stderr=out_fd) # notice stderr
  a.communicate()
  log2()
def log2():

  while(1):
      o= open('op_log_1','r')
      op_status = o.readlines()
      op_status = op_status[-12]
      string1 = op_status
      string2 = "%"
      string3 = op_status
      string4 = "Copied"
      text = string3[-34:-31] + string2 + string1[-49:-44] + string4
      if (op_status[-34:-31] == "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("Operation Compl.",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string(text,1)
      if (op_status[-34:-31] != "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("!! Operation !!",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string("!!  Failed   !!",1)
      if ( GPIO.input(ABORT_EXIT) == True):
       home()
      if ( GPIO.input(MENU_SET) == True):
       menu()
###############################
#erase menu                   #
###############################
def erase():
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string("<    Erase    >",2)
   else:
    if ( GPIO.input(LEFT) == False):
     menu()
    if ( GPIO.input(MENU_SET) == False):
     quick_erase1()
    if ( GPIO.input(RIGHT) == False):
     utility()
  ########## im stoped from here ################################################
def quick_erase1():
    string1 = "Erase"
    string2 = "Hdd #1:"
    string3 = "?"
    f=os.popen("df / -h")
    size1 = f.readlines()
    size1 = size1[-1]
    size1 = size1[16:-20]
    line1 = string1 + string3
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = string2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == True):
       home()
      if ( GPIO.input(LEFT) == True):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == True):
       erase_cmd_1_confirmation()

def erase_cmd_1_confirmation():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(ABORT_EXIT) == False):
    erase()
   if ( GPIO.input(MENU_SET) == False):
    cmd_quick_erase1()
    time.sleep(8)
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("***Are you sure?***",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("< No       Yes >",2)


def cmd_quick_erase1():
  out_fd = open('erase_log_1','w')
  out_fd.write("Operation log\n")
  cmd_list = ['dc3dd','if=/dev/root', 'of=/dev/sda1']
  a = subprocess.Popen(cmd_list,stderr=out_fd) # notice stderr
  a.communicate()
  erase_log2()
def erase_log2():

  while(1):
      o= open('erase_log_1','r')
      op_status = o.readlines()
      op_status = op_status[-12]
      string1 = op_status
      string2 = "%"
      string3 = op_status
      string4 = "Copied"
      text = string3[-34:-31] + string2 + string1[-49:-44] + string4
      if (op_status[-34:-31] == "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("Operation Compl.",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string(text,1)
      if (op_status[-34:-31] != "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("!! Operation !!",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string("!!  Failed   !!",1)
      if ( GPIO.input(ABORT_EXIT) == True):
       home()
      if ( GPIO.input(MENU_SET) == True):
       menu()
## last check
def quick_erase2():
    string1 = "Erase"
    string2 = "Hdd #2:"
    string3 = "?"
    f=os.popen("df / -h")
    size1 = f.readlines()
    size1 = size1[-1]
    size1 = size1[16:-20]
    line1 = string1 + string3
    f=os.popen("df /dev/mmcblk0p1 -h")
    size2 = f.readlines()
    size2 = size2[-1]
    size2 = size2[17:-23]
    line2 = string2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == True):
       home()
      if ( GPIO.input(LEFT) == True):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == True):
       erase_cmd_1_confirmation()

def erase_cmd_2_confirmation():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(ABORT_EXIT) == False):
    erase()
   if ( GPIO.input(MENU_SET) == False):
    cmd_quick_erase1()
    time.sleep(8)
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("***Are you sure?***",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("< No       Yes >",2)


def cmd_quick_erase2():
  out_fd = open('erase_log_1','w')
  out_fd.write("Operation log\n")
  cmd_list = ['dd','if=/dev/zero', 'of=/dev/sda2']
  a = subprocess.Popen(cmd_list,stderr=out_fd) # notice stderr
  a.communicate()
  erase_log2()
def erase_log2():

  while(1):
      o= open('erase_log_1','r')
      op_status = o.readlines()
      op_status = op_status[-12]
      string1 = op_status
      string2 = "%"
      string3 = op_status
      string4 = "Copied"
      text = string3[-34:-31] + string2 + string1[-49:-44] + string4
      if (op_status[-34:-31] == "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("Operation Compl.",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string(text,1)
      if (op_status[-34:-31] != "100"):
       lcd_byte(LCD_LINE_1, LCD_CMD)
       lcd_string("!! Operation !!",1)
       lcd_byte(LCD_LINE_2, LCD_CMD)
       lcd_string("!!  Failed   !!",1)
      if ( GPIO.input(ABORT_EXIT) == True):
       home()
      if ( GPIO.input(MENU_SET) == True):
       menu()

def utility():
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string("<    Utility    >",2)
   else:
    if ( GPIO.input(LEFT) == False):
     erase()
    if ( GPIO.input(MENU_SET) == False):
     quick_erase1()
    if ( GPIO.input(RIGHT) == False):
     menu()


def menu3():#Tweet
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string("[GO]    < Tweet ",2)
   else:
    if ( GPIO.input(LEFT) == False):
     tweetemail()
    if ( GPIO.input(MENU_SET) == False):
     menu2()

def menu3():#Tweet
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string("[GO]    < Tweet ",2)
   else:
    if ( GPIO.input(LEFT) == False):
     tweetemail()
    if ( GPIO.input(MENU_SET) == False):
     menu2()

def menu3():#Tweet
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string("[GO]    < Tweet ",2)
   else:
    if ( GPIO.input(LEFT) == False):
     tweetemail()
    if ( GPIO.input(MENU_SET) == False):
     menu2()

def menu3():#Tweet
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string("[GO]    < Tweet ",2)
   else:
    if ( GPIO.input(LEFT) == False):
     tweetemail()
    if ( GPIO.input(MENU_SET) == False):
     menu2()

def ip():
  timelastchecked = 0
  time.sleep(0.5)
  while(1):
   if time.time() >= timelastchecked:
    timelastchecked = time.time()+3
    mystring = ""
    mytime = ""
    mytemp = ""
    pretemp = "0x1 ["
    posttemp = "] "
    f=os.popen("date")
    for i in f.readlines():
     mytime += i
     mytime = mytime[11:-13]
     f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
     for i in f.readlines():
      mytemp += i
      mytemp = mytemp[5:-3]
      mystring = pretemp + mytemp + posttemp + mytime
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string(mystring,1)
      preIP = "IP "
      address = get_ip_address('eth0')
      address = preIP + address
      lcd_byte(LCD_LINE_2, LCD_CMD)
      lcd_string(address,1)
      time.sleep(4.5)
      home()







def choose2():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    target2source()
   if ( GPIO.input(MENU_SET) == False):
    copy()
   if ( GPIO.input(RIGHT) == False):
    choose3()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Hdd 2 Hdd ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO]  < Target 2 Source >",2)

def choose3():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    station3()
   if ( GPIO.input(MENU_SET) == False):
    choose2()
   if ( GPIO.input(RIGHT) == False):
    choose4()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO]    < Beat >",2)

def choose4():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    station4()
   if ( GPIO.input(MENU_SET) == False):
    choose3()
   if ( GPIO.input(RIGHT) == False):
    choose5()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO]   < Indie >",2)

def choose5():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    station5()
   if ( GPIO.input(MENU_SET) == False):
    choose4()
   if ( GPIO.input(RIGHT) == False):
    choose6()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO]    < 80's >",2)

def choose6():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    station6()
   if ( GPIO.input(MENU_SET) == False):
    choose5()
   if ( GPIO.input(RIGHT) == False):
    choose7()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO]  < Groove >",2)

def choose7():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    station7()
   if ( GPIO.input(MENU_SET) == False):
    choose6()
   if ( GPIO.input(RIGHT) == False):
    choose8()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO]  < LushFM >",2)

def choose8():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    station8()
   if ( GPIO.input(MENU_SET) == False):
    choose7()
   if ( GPIO.input(RIGHT) == False):
    choose9()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO] < DubStep >",2)

def choose9():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    station9()
   if ( GPIO.input(MENU_SET) == False):
    choose8()
   if ( GPIO.input(RIGHT) == False):
    choose10()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO]    < Jazz >",2)

def choose10():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    source2target0()
   if ( GPIO.input(MENU_SET) == False):
    choose9()
   if ( GPIO.input(RIGHT) == False):
    choose11()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO] < BMarley >",2)

def choose11():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    source2target1()
   if ( GPIO.input(MENU_SET) == False):
    choose10()
   if ( GPIO.input(RIGHT) == False):
    choose12()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO] < SlowJam >",2)

def choose12():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    source2target2()
   if ( GPIO.input(MENU_SET) == False):
    choose11()
   if ( GPIO.input(RIGHT) == False):
    copy()
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(" Choose Station ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("[GO] < CDelMar >",2)

def tweetemail():
  temp1 = ""
  f=os.popen("/opt/vc/bin/vcgencmd measure_temp")
  for i in f.readlines():
   temp1 += i
   pretemp = " Pi temperature is "
   temp1 = temp1[5:]
   temp1 = pretemp + temp1
   #Gmail account details
   USERNAME = "YOURGMAILADDRESS@gmail.com" #Your gmail email address
   PASSWORD = "YOURGMAILPASSWORD" # your gmail password
   MAILTO  = "trigger@ifttt.com" # IFTTT standard email trigger address
   #Email content
   msg = MIMEText(temp1)
   msg['Subject'] = "#RaspberryPi GPIO button tweeting from my Raspberry Pi Internet Radio -"
   msg['From'] = USERNAME
   msg['To'] = MAILTO
   #Server stuff
   server = smtplib.SMTP('smtp.gmail.com:587')
   server.ehlo_or_helo_if_needed()
   server.starttls()
   server.ehlo_or_helo_if_needed()
   server.login(USERNAME,PASSWORD)
   server.sendmail(USERNAME, MAILTO, msg.as_string())
   server.quit()
   #LCD Message
   time.sleep(0.5)
   lcd_byte(LCD_LINE_1, LCD_CMD)
   lcd_string("NERDBOX",2)
   lcd_byte(LCD_LINE_2, LCD_CMD)
   lcd_string("HAS TWEETED!",2)
   time.sleep(1)
   menu3()

def evernote():
  f=os.popen("echo 'currentsong' | nc localhost 6600 | grep -e '^Title: '")
  tracknow = ""
  for i in f.readlines():
   tracknow += i
   tracknow = tracknow[7:]
   #Gmail account details
   USERNAME = "YOURGMAILADDRESS@gmail.com"
   PASSWORD = "YOURGMAILPASSWORD"
   MAILTO  = "trigger@ifttt.com"
   #Email content
   msg = MIMEText(tracknow)
   msg['Subject'] = "#song New song to record"
   msg['From'] = USERNAME
   msg['To'] = MAILTO
   #Server stuff
   server = smtplib.SMTP('smtp.gmail.com:587')
   server.ehlo_or_helo_if_needed()
   server.starttls()
   server.ehlo_or_helo_if_needed()
   server.login(USERNAME,PASSWORD)
   server.sendmail(USERNAME, MAILTO, msg.as_string())
   server.quit()
   #LCD Message
   lcd_byte(LCD_LINE_2, LCD_CMD)
   lcd_string("SENT",2)
   time.sleep(0.3)
   lcd_byte(LCD_LINE_2, LCD_CMD)
   lcd_string("",2)
   time.sleep(0.3)
   lcd_byte(LCD_LINE_2, LCD_CMD)
   lcd_string("TO",2)
   time.sleep(0.3)
   lcd_byte(LCD_LINE_2, LCD_CMD)
   lcd_string("",2)
   time.sleep(0.3)
   lcd_byte(LCD_LINE_2, LCD_CMD)
   lcd_string("EVERNOTE",2)
   time.sleep(0.6)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])

def off():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(LEFT) == False):
    menu()
   if ( GPIO.input(RIGHT) == False):
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("Shutting Down   ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("                ",2)
    time.sleep(0.5)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("Shutting Down.  ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("                ",2)
    time.sleep(0.5)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("Shutting Down.. ",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("                ",2)
    time.sleep(0.5)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("Shutting Down...",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("                ",2)
    time.sleep(0.5)
    os.system("sudo halt")
    time.sleep(8)
   else:
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("***Shut down?***",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("< No       Yes >",2)


def lcd_init():
  # Initialise disMENU_SET
  lcd_byte(0x33,LCD_CMD)
  lcd_byte(0x32,LCD_CMD)
  lcd_byte(0x28,LCD_CMD)
  lcd_byte(0x0C,LCD_CMD)
  lcd_byte(0x06,LCD_CMD)
  lcd_byte(0x01,LCD_CMD)

def lcd_string(message,style):
  # Send string to disMENU_SET
  # style=1 LEFT justified
  # style=2 Centred
  # style=3 Right justified

  if style==1:
    message = message.ljust(LCD_WIDTH," ")
  elif style==2:
    message = message.center(LCD_WIDTH," ")
  elif style==3:
    message = message.rjust(LCD_WIDTH," ")

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

if __name__ == '__main__':
  main()
