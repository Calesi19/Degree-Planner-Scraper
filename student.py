import pyautogui
import time
import tkinter
from bs4 import BeautifulSoup
import os
import requests
import degreePlanner
import json

class Student:
    def __init__(self):

        #Following variable will store HTML content for student's Degree Planner.
        self.DPsoup = self.getDegreePlannerSoup()

        #Following variable will store HTML content for student's Course History.
        self.CHsoup = self.getCourseHistorySoup()
        
        #Following variable will store the students name as a string.
        self.name = self.findStudentName()

        #Following variable will store the student's PATH ID as a string.
        self.pathID = self.findPathId()

        #Following variable will store the classes the student's planner is scheduling as a list of strings.
        self.coursesPlanned = self.findCoursesPlanned()

        #Following variable will indicate the amount of credits that are scheduled in the student's planner.
        self.creditsPlanned = self.findCreditsPlanned()

        #Following variable will store the courses the student's planner is scheduling as a list of strings.
        self.coursesTaken = self.findCoursesTaken()

        #Following variable will indicate the amount of credits that the student has already completed.
        self.creditsCompleted = self.findCreditsCompleted()

        #Following variable will indicate the student's catalog year.
        self.catalogYear = self.findCatalogYear()

        #Following variable will indicate the student's chosen major/degree option.
        self.degree = self.findDegree()

        #Following variable will store the student's chosen certificates as a list of strings.
        self.certificates = self.findCertificates()
        

    def getDegreePlannerSoup(self):
        url = "Degree Planner.html"
        with open("Degree Planner.html") as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        return soup



    def findCertificates(self):
        first_cert = self.DPsoup.find(True, {"class": "c1-text"}).get_text().replace('C1','')
        second_cert = self.DPsoup.find(True, {"class": "c2-text"}).get_text().replace('C2','')
        third_cert = self.DPsoup.find(True, {"class": "c3-text"}).get_text().replace('C3','')
        return [first_cert, second_cert, third_cert]


    def findDegree(self):
        return self.DPsoup.find(True, {"class":"plan-header"}).get_text()


    def getCourseHistorySoup(self):
        url = "Advisee Roster - Course History Detail _ Advisor _ Advisor _ BYU-Idaho's Personalized Access.html"
        with open(url) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        return soup


    def getCourseCode(self, courseText):
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


    def findCoursesTaken(self):
        coursesTaken = set()
        creditCount = 0
        for text in self.CHsoup.find_all(True, {"class":"footable-first-visible"}):
            if len(text.get_text()) < 14 and (text.get_text() != 'Course'): 
                course = text.get_text()
                course = self.getCourseCode(course)
                if course not in coursesTaken:
                    coursesTaken.add(course)
        return sorted(coursesTaken)


    def findCreditsCompleted(self):
        coursesTaken = set()
        creditCount = 0
        for text in self.CHsoup.find_all(True, {"class":"footable-first-visible"}):
            if len(text.get_text()) < 14 and (text.get_text() != 'Course'): 
                course = text.get_text()
                course = self.getCourseCode(course)
                if course not in coursesTaken:
                    coursesTaken.add(course)

                    nextSiblings = text.find_next_siblings("td")
                    for nextSibling in nextSiblings:
                        if "." in nextSibling.get_text() and len(nextSibling.get_text()) < 6:
                            creditCount += float(nextSibling.get_text())
        
        return creditCount


    def findPathId(self):
        studentPathId = ""
        for pathID in self.DPsoup.find(True, {"class": "id"}):
            studentID = pathID.get_text()
        for char in studentID:
            if char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                studentPathId += char
        return studentPathId


    def findCatalogYear(self):
        for year in self.DPsoup.find_all(True, {"class":"catalog-year"}):
            catalogYear = year.get_text()
        if "19" in catalogYear:
            return "2019"
        elif "2020" in catalogYear or "UG20" in catalogYear:
            return "2020"
        elif "2021" in catalogYear or "21" in catalogYear:
            return "2021"
        elif "2022" in catalogYear or "22" in catalogYear:
            return "2022"
        else:
            return None


    def findCreditsPlanned(self):
        creditCounts = []
        for credit in self.DPsoup.find_all(True, {"class":"credits"}):
            creditCounts.append(credit.get_text().replace(' credits', ''))

        semestersPlanned = 0
        creditsPlanned = 0

        for credit in creditCounts:
            if len(creditCounts[semestersPlanned]) < 3:
                creditsPlanned += int(creditCounts[semestersPlanned])
                semestersPlanned += 1
        return creditsPlanned


    def findStudentName(self):
        for name in self.DPsoup.find("p"):
            studentName = name
        return studentName


    def findCoursesPlanned(self):
        courses = set()
        for div in self.DPsoup.find_all(True, {"class":"name"}): 
            if div.get_text() != self.name:
                if 'Winter' not in div.get_text():
                    if 'Spring' not in div.get_text():
                        if 'Fall' not in div.get_text():
                            courses.add(div.get_text().replace('Not Registered','').replace('Registered',''))
        return sorted(courses)


    def checkCertificates(self):
        certificateFound = False
        text = ""

        count = 1
        missing_courses = set()
        f = open(f'certificates-{self.catalogYear}.json')
        data = json.load(f)
        cert_classes = []
        
        certificates = data[f"certificates-{self.catalogYear}"]
        coursesPlanned = set()
        coursesTakenButPlanned = []

        for coursePlanned in self.coursesPlanned:
            coursesPlanned.add(degreePlanner.getCourseCode(coursePlanned))


        for chosen_cert in self.certificates:
            if chosen_cert == "Social Media Marketing Certificate":
                pass
            else:
                for cert in certificates:
                    if cert["name"] == chosen_cert:
                        cert_classes = cert["classes"]
                        certificateFound = True

                        for course in cert_classes:
                            if degreePlanner.getCourseCode(course) not in coursesPlanned:
                                missing_courses.add(course)

                if not certificateFound:
                    text += f"\nNot able to check certificate {count}\n"


            for course in missing_courses:
                if self.getCourseCode(course) in self.coursesTaken:
                    coursesTakenButPlanned.append(course)

            for course in coursesTakenButPlanned:
                missing_courses.remove(course)


            if len(missing_courses)!= 0:
                text += f"\n**************************************************\nThese are courses not planned for certificate {count}:\n"
                for course in missing_courses:
                    text += f"{course}\n"

            coursesTakenButPlanned = [] 
            cert_classes = []
            missing_courses.clear()
            count += 1
            certificateFound = False
            
        return text




    def getInformation(self):
        text = f"""{self.name}
PATH ID: {self.pathID}

{self.degree}
Catalog Year: {self.catalogYear + '-' + str(int(self.catalogYear) + 1)}

Chosen Certificates:
1.{self.certificates[0]}
2.{self.certificates[1]}
3.{self.certificates[2]}

Showing {self.creditsPlanned} credits planned.
{f'(You are short {120 - self.creditsPlanned} credits)' if self.creditsPlanned < 120 else ""}

The following classes are scheduled in the student's planner:\n"""
        for course in self.coursesPlanned:
            text += f"{course}\n"

        text += self.checkCertificates()

        if len(self.coursesTaken) != 0:
            text += "\nThe following classes have been completed:\n"
            courseFound = False
            coursesToPrint = []
            with open('classes.txt', 'r') as f:
                allCourses = f.readlines()


            for course in self.coursesTaken:
                for catalogCourse in allCourses:
                    if self.getCourseCode(course) == self.getCourseCode(catalogCourse):
                        coursesToPrint.append(catalogCourse)
                        courseFound = True
                        break
                if not courseFound:
                    coursesToPrint.append(f"{course}\n")
                
                courseFound = False
            
            
            for course in sorted(coursesToPrint):
                text += course
        
        else:
            text += "\nStudent has no course history.\n"

        text += self.checkGenerals()

        text += self.checkReligion()        

        return text.split("\n")


    

    def checkReligion(self):

        lines = []

        missing_courses = []

        religionElectiveCount = 0

        courseFound = False

        text = ""

        with open('classes-religionCourses.txt', 'r') as f:
            eternalTruths = f.readlines()


        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "REL200C":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "REL200C":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("REL  200C - The Eternal Family")
        

        courseFound = False

        #########################################

        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "REL225C":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "REL225C":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("REL  225C - Foundations of the Restoration")
        

        courseFound = False

        #########################################

        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "REL250C":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "REL250C":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("REL  250C - Jesus Christ Everlasting Gospel")
        

        courseFound = False

        #########################################

        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "REL275C":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "REL275C":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("REL  275C - Teachings of Book of Mormon")
        

        courseFound = False
                
        ########################################


        for course in self.coursesPlanned:
            for rCourse in eternalTruths:
                if self.getCourseCode(course) == self.getCourseCode(rCourse.strip("\n")):
                    if "C" not in self.getCourseCode(course):
                        religionElectiveCount += 1

        suggestion = [
            "REL324 - Doctrine and Covenants",
            "REL325 - Doctrine and Covenants",
            "REL333 - Teachings of the Living Prophets",
            "REL261 - Introduction to Family History",
            "REL234 - Preparing for Eternal Marriage",
            "REL100 - Introduction to The Church of Jesus Christ of Latter-day Saints"
        ]


        i = 0
        index = 0
        while i < (3 - religionElectiveCount):
            for course in self.coursesPlanned:
                if self.getCourseCode(course) == self.getCourseCode(suggestion[index]):
                    courseFound = True
                    break
            
            if courseFound:
                index += 1
                courseFound = False
            else:
                missing_courses.append(f"{suggestion[index]}")
                index += 1
                i += 1

            
        
        ######YOU ARE HERE
        if len(missing_courses) != 0:
            text += "\n*****************************************\nThe following religion courses are missing:\n*****************************************\n"
            for course in missing_courses:
                text += f"{course}\n"

 
        return text




    def checkGenerals(self):
        lines = ''
        missing_courses = []
        SScount = 0
        NScount = 0
        courseFound = False

        with open('classes-socialSciences.txt', 'r') as f:
            socialSciences = f.readlines()
    

        socialSciencesCompleted = []


        with open('classes-naturalSciences.txt', 'r') as f:
            naturalSciences = f.readlines()


        naturalSciencesCompleted = []




        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "MATH108X":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "MATH108X":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("MATH 108X - Math for the Real World")
        courseFound = False

        ####################

        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "ENG150":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "ENG150":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("ENG  150 - Writing & Reasoning Foundations")
        courseFound = False

        ####################

        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "ENG301" or self.getCourseCode(course) == "BUS301":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "ENG301" or self.getCourseCode(course) == "BUS301":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("BUS  301 - Adv Writing in Pro Contexts / ENG  301 - Advanced Writing and Research")
        courseFound = False

        ####################

        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "HUM110":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "HUM110":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("HUM  110 - Introduction to the Humanities")
        courseFound = False

        ####################

        for course in self.coursesPlanned:
            if self.getCourseCode(course) == "GE103":
                courseFound = True
                break
        for course in self.coursesTaken:
            if self.getCourseCode(course) == "GE103":
                courseFound = True
                break
        if not courseFound:
            missing_courses.append("GE103 - Online University Skills")
        courseFound = False

            #######here YOU LEFT OFF

        for course in self.coursesPlanned:
            for sCourse in socialSciences:
                if self.getCourseCode(course) == self.getCourseCode(sCourse.strip("\n")):
                    SScount += 1
                    socialSciencesCompleted.append(sCourse.strip("\n"))

        for course in self.coursesPlanned:
            for sCourse in naturalSciences:
                if self.getCourseCode(course) == self.getCourseCode(sCourse.strip("\n")):
                    NScount += 1
                    naturalSciencesCompleted.append(sCourse.strip("\n"))
        
        if len(missing_courses) != 0 or SScount < 2 or NScount < 2:
            lines += "\n*****************************************\nThe following general courses are missing:\n*****************************************\n"
            for course in missing_courses:
                lines += f"{course}\n"

            if SScount < 2:
                lines += f"\nStudent is missing {2 - SScount} Social Science courses."
                if SScount != 0:
                    lines += f"\nAlready planned -> {socialSciencesCompleted[0]}\n"
                
            if NScount < 2:
                lines += f"\nStudent is missing {2 - NScount} Natural Science courses."
                if NScount != 0:
                    lines += f"\nAlready planned -> {naturalSciencesCompleted[0]}\n"
                

        else:
            lines += "\nAll generals planned."

        return lines




