import time
from student import *
from interface import *
import os
import subprocess
import json

def clear():
    os.system("cls")

def writeTxt(lines):
    os.system("TASKKILL /F /IM notepad.exe")
    clearTxt()
    with open('student.txt', 'a') as f:
        f.writelines('\n'.join(lines))

def openTxt():
    filename = r"student.txt"
    os.system('notepad.exe ' + filename)
    

def clearTxt():
    file = open("student.txt","w")
    file.close()


def gatherText(student):
    text = student.getInformation()
    writeTxt(text)
    openTxt()


def getCourseCode(courseText):
    text = ''
    for char in courseText:
        if char == "-":
            break
        else:
            if char == " ":
                pass
            else:
                text += char
    return text


