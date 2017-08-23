# SOS for Python
# Copyright (c) 2017 full phat products
#
import sys
import threading

_curDev = ""


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# ConfigParser Helpers
#
#
def ConfigTryGetInt(config, section, name):
    try:
        i = config.getint(section, name)
        return True, i

    except:
        return False, ""

def ConfigTryGetFloat(config, section, name):
    try:
        f = config.getfloat(section, name)
        return True, f

    except:
        return False, ""



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

def privLog(col, level, text, bold=False):
    global threading
    global _curDev

    s = ""

    # level...
    s = s + col + "[" + level + "] " + bcolors.ENDC

    # thread name...
    s = s + "(" +  str(threading.current_thread().name) + ") "

    # current device...
    if _curDev != "":
        s = s + "{" + _curDev + "} "

    if bold:
        s = s + bcolors.WHITE

    # text...
    s = s + text

    if bold:
        s = s + bcolors.ENDC

    return s


def sos_warn(text):
    print privLog(bcolors.WARNING, "WARN", text)    


def sos_fail(text):
    print privLog(bcolors.FAIL, "FAIL", text)    


def sos_ok(text):
    print privLog(bcolors.OKGREEN, " OK ", text)    


def sos_info(text):
    print privLog(bcolors.OKBLUE, "INFO", text)    


def sos_print(text):
    sos_info(text)


def sos_note(text):
    print privLog(bcolors.OKBLUE, "INFO", text, True)



def SetDevice(text):
    global _curDev
    _curDev = text


def ClrDevice():
    global _curDev
    _curDev = ""
