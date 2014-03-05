#!/usr/bin/python

# Clonpi Hdd Duplicator v1.0 Open source code by Z3ro0ne
#Blog : z3ro0ne.blogspot.com
#Email : Saadousfar59@gmail.com
#Fb : https://www.facebook.com/Z3ro0ne
# Enjoy ..
#
# for wiring check plz https://github.com/Z3rO0ne/clonpi/tree/master/wiring



#import
import RPi.GPIO as GPIO
import time
import os
import subprocess
import socket
import fcntl
import struct
import datetime


# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18


# Define GPIO for button Controls

ABORT_EXIT = 3
IPSHOW = 14
LEFT = 4
MENU_SET = 2
RIGHT = 17

#read disks list
f=os.popen("fdisk -l |grep Disk")
hdd1 = f.readlines()
hdd1 = hdd1[-2]
HDD1 = hdd1[6:13]+"1"
f=os.popen("fdisk -l |grep Disk")
hdd2 = f.readlines()
hdd2 = hdd2[-4]
HDD2 = hdd2[6:13]+"1"



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
  disks_list()
def disks_list():
    #read disks list
    f=os.popen("fdisk -l |grep Disk")
    hdd1 = f.readlines()
    hdd1 = hdd1[-2]
    HDD1 = hdd1[6:13]
    f=os.popen("fdisk -l |grep Disk")
    hdd2 = f.readlines()
    hdd2 = hdd2[-4]
    HDD2 = hdd2[6:13]    #home()
    home()



def home():
    hd1 = "Hdd #1:"
    hd2 = "Hdd #2:"
    f=os.popen("fdisk -l |grep Disk " )
    size1 = f.readlines()
    #print(size1)
    size1 = size1[-4]
    size1 = size1[15:22]
    line1 = hd1 + size1
    print(size1)
    #size2 = ""
    f=os.popen("fdisk -l |grep Disk ")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = hd2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       home()
      if ( GPIO.input(LEFT) == False):
       home()
      if ( GPIO.input(MENU_SET) == False):
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
    if ( GPIO.input(LEFT) == False):
     off()
    if ( GPIO.input(MENU_SET) == False):
     copy_hdd1_to_hdd2()
    if ( GPIO.input(RIGHT) == False):
     erase()
    if ( GPIO.input(ABORT_EXIT) == False):
     home()

def copy_hdd1_to_hdd2():
    hd1 = "Hdd #1:"
    hd2 = "To Hdd #2:"
    f=os.popen("fdisk -l |grep Disk " )
    size1 = f.readlines()
    #print(size1)
    size1 = size1[-4]
    size1 = size1[15:22]
    line1 = hd1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("fdisk -l |grep Disk ")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = hd2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       copy_hdd2_to_hdd1()
      if ( GPIO.input(LEFT) == False):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == False):
       copy_cmd_1()
      if ( GPIO.input(ABORT_EXIT) == False):
       menu()

def copy_hdd2_to_hdd1():
    hd1 = "Hdd #2:"
    hd2 = "To Hdd #1:"
    f=os.popen("fdisk -l |grep Disk ")
    size1 = f.readlines()
    size1 = size1[-4]
    size1 = size1[15:-22]
    line1 = hd1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("fdisk -l |grep Disk ")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = hd2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       copy_hdd2_to_hdd1()
      if ( GPIO.input(LEFT) == False):
       copy_hdd2_to_hdd1()
      if ( GPIO.input(MENU_SET) == False):
       copy_cmd_2()

def copy_cmd_1():
    string1 = "Hdd #1:"
    string2 = "To Hdd #2:"
    string3 = "?"
    f=os.popen("fdisk -l |grep Disk ")
    size1 = f.readlines()
    size1 = size1[-4]
    size1 = size1[15:22]
    line1 = string1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("fdisk -l |grep Disk ")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = string2 + size2 + string3
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       home()
      if ( GPIO.input(LEFT) == False):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == False):
       copy_cmd_1_confirmation()

def copy_cmd_1_confirmation():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(ABORT_EXIT) == False):
    menu()
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
  cmd_list = ['dc3dd','if=/dev/sda1', 'of=/dev/sdb1']
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
      if ( GPIO.input(ABORT_EXIT) == False):
       home()
      if ( GPIO.input(MENU_SET) == False):
       menu()

def copy_cmd_2():
    string1 = "Hdd #2:"
    string2 = "To Hdd #1:"
    string3 = "?"
    f=os.popen("fdisk -l |grep Disk ")
    size1 = f.readlines()
    size1 = size1[-4]
    size1 = size1[15:22]
    line1 = string1 + size1
    #print(size1)
    #size2 = ""
    f=os.popen("fdisk -l |grep Disk ")
    size2 = f.readlines()
    #mytime = mytime.strip()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = string2 + size2 + string3
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       home()
      if ( GPIO.input(LEFT) == False):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == False):
       copy_cmd_1_confirmation()

def copy_cmd_2_confirmation():
  time.sleep(0.5)
  while(1):
   if ( GPIO.input(ABORT_EXIT) == False):
    menu()
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
  cmd_list = ['dc3dd','if=/dev/sdb1', 'of=/dev/sda1']
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
      if ( GPIO.input(ABORT_EXIT) == False):
       home()
      if ( GPIO.input(MENU_SET) == False):
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
def quick_erase1():
    string1 = "Erase"
    string2 = "Hdd #1:"
    string3 = "?"
    f=os.popen("fdisk -l |grep Disk ")
    size1 = f.readlines()
    size1 = size1[-4]
    size1 = size1[15:22]
    line1 = string1 + string3
    f=os.popen("fdisk -l |grep Disk ")
    size2 = f.readlines()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = string2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       home()
      if ( GPIO.input(LEFT) == False):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == False):
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
  cmd_list = ['dc3dd','if=/dev/zero', 'of=/dev/sda1']
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
      if ( GPIO.input(ABORT_EXIT) == False):
       home()
      if ( GPIO.input(MENU_SET) == False):
       menu()
def quick_erase2():
    string1 = "Erase"
    string2 = "Hdd #2:"
    string3 = "?"
    f=os.popen("fdisk -l |grep Disk ")
    size1 = f.readlines()
    size1 = size1[-4]
    size1 = size1[15:22]
    line1 = string1 + string3
    f=os.popen("fdisk -l |grep Disk ")
    size2 = f.readlines()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = string2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       home()
      if ( GPIO.input(LEFT) == False):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == False):
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
  cmd_list = ['dd','if=/dev/zero', 'of=/dev/sdb1']
  a = subprocess.Popen(cmd_list,stderr=out_fd) # notice stderr
  a.communicate()
  erase_log3()
def erase_log3():

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
      if ( GPIO.input(ABORT_EXIT) == False):
       home()
      if ( GPIO.input(MENU_SET) == False):
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
     systeminfo()
    if ( GPIO.input(RIGHT) == False):
     menu()

def systeminfo():
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
      lcd_string("< Show Ip address >",2)
   else:
    if ( GPIO.input(LEFT) == False):
     erase()
    if ( GPIO.input(MENU_SET) == False):
     showIp()
    if ( GPIO.input(RIGHT) == False):
     menu()
def showIp():
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

   else:
    if ( GPIO.input(LEFT) == False):
     erase()
    if ( GPIO.input(MENU_SET) == False):
     systeminfo()
    if ( GPIO.input(RIGHT) == False):
     menu()

def hdd1Info():
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
      lcd_string("< Show hdd info >",2)
   else:
    if ( GPIO.input(LEFT) == False):
     erase()
    if ( GPIO.input(MENU_SET) == False):
     systeminfo()
    if ( GPIO.input(RIGHT) == False):
     menu()
def hdd1():
    string1 = "hd1:"
    string2 = "Sn:"

    f=os.popen("hdparm -I /dev/sda1 |grep Model")
    size1 = f.readlines()
    size1 = size1[-4]
    size1 = size1[15:22]
    line1 = string1 + size1
    f=os.popen("hdparm -I /dev/sda1 |grep Serial")
    size2 = f.readlines()
    size2 = size2[-1]
    size2 = size2[15:22]
    line2 = string2 + size2
    print(size2)
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string(line1,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(line2,1)
    while(1):
      if ( GPIO.input(RIGHT) == False):
       home()
      if ( GPIO.input(LEFT) == False):
       copy_hdd1_to_hdd2()
      if ( GPIO.input(MENU_SET) == False):
       erase_cmd_1_confirmation()
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
  else:

   if ( GPIO.input(LEFT) == False):
          erase()
   if ( GPIO.input(MENU_SET) == False):
          systeminfo()
   if ( GPIO.input(RIGHT) == False):
         dd()

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
