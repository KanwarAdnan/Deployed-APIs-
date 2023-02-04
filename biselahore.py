# Code By Kanwar Adnan
# API Link : https://26d24a.deta.dev/
import requests
from bs4 import BeautifulSoup as bs4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

class HtmlFetcher:
  def get_html(self , html_fetcher , roll_no):
    return html_fetcher.get_html(roll_no)

class DataProcessor:
  def get_result(self , data_processor , html):
    return data_processor.get_result(html)

class BiseLahore:
  def __init__(self, url = "http://result.biselahore.com/"):
    self.url = url

  def get_html(self , roll_no):
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

    response = requests.post(self.url , data = payload)
    return response.content # html

class BiseLahoreParser:
  def get_student_info(self , table):
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
    return student_info

  def get_student_marks(self , subjects_marks):
    subjects_marks.pop(0) # Removing Extras
    subjects_marks.pop(0) # Removing Extras

    student_marks = {}

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

      student_marks[subject_name] = {"9th" : {} , "10th" : {},"result" : {}}

      student_marks[subject_name]["9th"].update({
          "total" : total_9 , 
          "obtained" : int(subject_obtained_marks_1) ,
        }
      )

      student_marks[subject_name]["10th"].update({
          "total" : total_10 , 
          "practical" : subject_practical_marks , 
          "obtained" : int(subject_obtained_marks_2),
          "obtained_in_practical" : subject_obtained_practical_marks,
        }
      )

      student_marks[subject_name]["result"].update({
        "total" : int(subject_total_marks_2), 
        "obtained" : int(subject_obtained_total)
        })

    return student_marks

  def get_student_result(self, result):
    res_data = result.findAll('td')
    total = res_data[1].text
    result = res_data[2].text
    result = result.split("MARKS OBTAINED:")[1]
    status = result.split(' ')[0]
    obtained = result.split(' ')[1]
    grade = result.split(' ')[2]
    result = {
        "total" : int(total),
        "status" : status,
        "obtained" : int(obtained),
        "grade" : grade
      }
    return result

  def parse_html(self, html):
    soup = bs4(html,'html.parser')
    table = soup.find("table")
    student_data = soup.find("table",{"id" : "GridStudentData"})
    subjects_marks = student_data.findAll("tr")
    result = subjects_marks.pop()

    student_info = self.get_student_info(table)
    student_marks = self.get_student_marks(subjects_marks)
    student_result = self.get_student_result(result)

    student_info.update({
        "marks" : student_marks,
        "result" : student_result
    })

    return student_info

  def get_result(self, html):
    return self.parse_html(html)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

biselahore = BiseLahore()
biselahore_parser = BiseLahoreParser()
html_fetcher = HtmlFetcher()
data_processor = DataProcessor()

@app.get(path="/{roll_no}")
async def deep_search(roll_no: int):
  html = html_fetcher.get_html(biselahore , roll_no)
  result = data_processor.get_result(biselahore_parser , html)
  return result

@app.get(path="/")
async def developer_info():
  return  {
    "developer" : {"name" : "Kanwar Adnan","contact" : "kanwaradnanrajput@gmail.com"}
    }
