from student import *
import os
import time
import degreePlanner

def clear():
    os.system("cls")


class Interface:
    def __init__(self):
        
        
        self.student = None

    def run(self):

        clear()

        while True:
            
            if self.student is None:
                studentName = "None" 
            else:
                studentName = self.student.name

            print(f"Currently working on student: {studentName}")
            print("Select an option:")
            print("1. Display student information.")
            print("2. Update student information with current files.")


            userInput = input("> ")

            if userInput == "1":
                if self.student != None:
                    
                    text = self.student.getInformation()
                    degreePlanner.writeTxt(text)
                    degreePlanner.openTxt()
                    clear()
                else:
                    clear()
                    print("No student information is loaded.\n")


            if userInput == "2":
                self.student = Student()
                clear()
                print("Student Information Updated\n")

            