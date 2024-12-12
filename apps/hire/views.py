from flask import Blueprint, render_template

hire = Blueprint('hire', __name__, template_folder='templates', static_folder='static')

@hire.route('/')
def hiredate():

  
  return render_template("hire/hiredate.html")

import requests
from bs4 import BeautifulSoup

url = 'https://calendar.saramin.co.kr/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 필요한 채용 달력 정보 추출
calendar_data = soup.find_all('div', class_='calendar-event')
for event in calendar_data:
    date = event.find('span', class_='date').text
    job_title = event.find('span', class_='job-title').text
    print(f'{date}: {job_title}')