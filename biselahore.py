# Code By Kanwar Adnan
# API Link : https://26d24a.deta.dev/
import requests
from bs4 import BeautifulSoup as bs4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from time import time

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_html(roll_no: int):
  url = "http://result.biselahore.com/"
  payload = {
  "__LASTFOCUS": "",
  "__EVENTTARGET": "",
  "__EVENTARGUMENT": "",
  "__VIEWSTATE": "/wEPDwUKLTg2MzYzNDE2OGQYAQUJdHh0Rm9ybU5vDw88KwAHAGRk5uJsx1/RskDg70iU3ZrBbsvWYjIexg/pxZ1e7t2Vw9I=",
  "__VIEWSTATEGENERATOR": "CA0B0334",
  "rdlistCourse": "SSC",
  "txtFormNo": roll_no,
  "ddlExamType": 2,
  "ddlExamYear": 2018,
  "Button1": "View Result"
  }
  response = requests.post(url , data= payload)
  html = response.content
  return html

def get_result(html):
  soup = bs4(html,'html.parser')
  table = soup.find("table")
  roll_no = table.find("label",{"id" : "lblRollNoval"}).text
  reg_no = table.find("label",{"id" : "lblRegNum"}).text
  session_info = table.find("label",{"id" : "lblSession"}).text
  session_info.split(",")
  group = table.find("label" , {"id" : "lblGroup"}).text
  name = table.find("label",{"id" : "Name"}).text
  father_name = table.find("label",{"id" : "lblFatherName"}).text
  dob = table.find("label",{"id" : "lblDOB"}).text
  institution_district = table.find("label",{"id" : "lblExamCenter"}).text
  try:
    roll_no = int(roll_no)
  except:
    pass

  student_info = {"roll_no" : roll_no , "reg_no" : reg_no , "session_info" : session_info , "group" : group , "name" : name , 
                  "father_name" : father_name , "dob" : dob , "institution_district" : institution_district}

  student_data = soup.find("table",{"id" : "GridStudentData"})
  subjects_marks = student_data.findAll("tr")
  subjects_marks.pop(0) # Removing Extras
  subjects_marks.pop(0) # Removing Extras
  result = subjects_marks.pop()
  student_marks = {}
  student_marks_9th = {}
  student_combined = {}

  for subject_data in subjects_marks:
    subject_data = subject_data.findAll("td")

    subject_name = subject_data[0].text
    subject_total_marks = subject_data[1].text
    subject_practical_marks = subject_data[2].text
    subject_total_marks_2 = subject_data[3].text
    subject_obtained_marks_1 = subject_data[4].text
    subject_obtained_marks_2 = subject_data[5].text
    subject_obtained_practical_marks = subject_data[6].text
    subject_obtained_total = subject_data[7].text
    subject_status = subject_data[8].text

    try:
      subject_obtained_practical_marks = int(subject_obtained_practical_marks)
    except:
      subject_obtained_practical_marks = None
    try:
      subject_practical_marks = int(subject_practical_marks)
    except:
      subject_practical_marks = None

    total_9 = int(subject_total_marks.split('+')[0])
    total_10 = int(subject_total_marks.split('+')[1].split('=')[0])
    full_total = total_10
    full_obtained = int(subject_obtained_marks_2)

    if subject_practical_marks:
      full_total += subject_practical_marks
      full_obtained += subject_obtained_practical_marks

    student_marks_9th[subject_name] = {"9th" : {} , "10th" : {},"result" : {}}

    student_marks_9th[subject_name]["9th"].update({
        "total" : total_9 , 
        "obtained" : int(subject_obtained_marks_1) ,
      }
    )

    student_marks_9th[subject_name]["10th"].update({
        "total" : total_10 , 
        "practical" : subject_practical_marks , 
        "obtained" : int(subject_obtained_marks_2),
        "obtained_in_practical" : subject_obtained_practical_marks,
      }
    )

    student_marks_9th[subject_name]["result"].update({
      "total" : int(subject_total_marks_2), 
      "obtained" : int(subject_obtained_total)
      })

  student_info.update({
      "marks" : student_marks_9th})
  res_data = result.findAll('td')
  total = res_data[1].text
  result = res_data[2].text
  result = result.split("MARKS OBTAINED:")[1]
  status = result.split(' ')[0]
  obtained = result.split(' ')[1]
  grade = result.split(' ')[2]
  student_info.update({
      "result" : {
          "total" : int(total),
          "status" : status,
          "obtained" : int(obtained),
          "grade" : grade
      }
  })

  return student_info


@app.get(path="/{roll_no}")
async def deep_search(roll_no: int):
  t1 = time()
  html = get_html(roll_no)
  t2 = time()

  fetching_time = round(t2 - t1,2)
  result = get_result(html)
  t4 = time()

  parsing_time = round(t4 - t2,2)
  result.update({
    "time" : {"fetching_time" : fetching_time , "parsing_time" : parsing_time}
    })
  return result

@app.get(path="/")
async def developer_info():
  return  {
    "developer" : {"name" : "Kanwar Adnan","contact" : "kanwaradnanrajput@gmail.com"}
    }
