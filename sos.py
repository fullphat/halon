# SOS for Python
# Copyright (c) 2017 full phat products
#
import sys

_curDev = ""

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Terminal colours
#
class bcolors:
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def sos_warn(text):
    global _curDev
    s = bcolors.WARNING
    if _curDev != "":
        s = s + "       {" + _curDev + "} "
    print s + "[WARN] " + text + bcolors.ENDC

def sos_fail(text):
    global _curDev
    s = bcolors.FAIL
    if _curDev != "":
        s = s + "       {" + _curDev + "} "
    print s + "[FAIL] " + text + bcolors.ENDC

def sos_ok(text):
    global _curDev
    s = bcolors.OKGREEN
    if _curDev != "":
        s = s + "       {" + _curDev + "} "
    print s + "[ OK ] " + text + bcolors.ENDC

def sos_info(text):
    global _curDev
    s = bcolors.OKBLUE
    if _curDev != "":
        s = s + "       {" + _curDev + "} "
    print s + "[INFO] " + text + bcolors.ENDC

def sos_print(text):
    global _curDev
    s = ""
    if _curDev != "":
        s = s + "       {" + _curDev + "} "
    print s + "[INFO] " + text

def sos_bold(text):
    global _curDev
    s = bcolors.WHITE
    if _curDev != "":
        s = s + "       {" + _curDev + "} "
    print s + text + bcolors.ENDC

def SetDevice(text):
    global _curDev
    _curDev = text

def ClrDevice():
    global _curDev
    _curDev = ""
