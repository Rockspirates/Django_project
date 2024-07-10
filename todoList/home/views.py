from django.shortcuts import render
from django.contrib import messages 
from home import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

'''
Login and Registration Page functions
'''
def login_page(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if not User.objects.filter(username=username).exists():
            messages.error(request, "Invalid username")
            return render(request, "login_page.html")
        
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "Invalid password")
            return render(request, "login_page.html")
        else:
            login(request, user)
            return render(request, "home.html")
        
    return render(request, "login_page.html")

def logout_page(request):
    logout(request)
    return render(request, "login_page.html")

def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username Already Taken.")
            return render(request, "register.html")

        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            username = username,
        )

        user.set_password(password)
        user.save()
        messages.success(request, "Account created succefully.")
        return render(request, "register.html")

    return render(request, "register.html")

"""
Login required functions
"""

@login_required(login_url="/")
def home(request):
    context = {'success' : False}
    if request.method == "POST":
        task = request.POST['task']
        desc = request.POST['desc']
        deadline = request.POST['deadline']
        ins = models.TASK(user = User.objects.filter(username = request.user)[0],taskTitle=task, taskDesc=desc, deadline = deadline)
        ins.save()
        context = {'success' : True}

    return render(request, 'home.html', context)

@login_required(login_url="/")
def task(request):

    if request.method == "POST":
        deadline = request.POST['deadline']
        corrected_deadline = deadline.replace('p.m.', 'PM').replace('a.m.', 'AM')
        date_format = '%B %d, %Y, %I:%M %p'
        parsed_date = datetime.strptime(corrected_deadline, date_format)
        formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S+00:00')

        req_task = models.TASK.objects.get(user = User.objects.filter(username = request.user)[0], 
                                        taskTitle = request.POST['taskTitle'],
                                        taskDesc = request.POST['taskDesc'],
                                        deadline = formatted_date
                                        )
        print(User.objects.filter(username = request.user)[0], request.POST['taskTitle'], request.POST['taskDesc'], formatted_date)
        req_task.delete()


    alltasks = models.TASK.objects.filter(user = User.objects.filter(username = request.user)[0])
    alltasks = alltasks.order_by('deadline')
    context = {'tasks' : alltasks}
    return render(request, 'task.html', context)


"""
Web Scrapping functions
"""

import requests
import bs4

@login_required(login_url='/')
def cp(request):
    urls = ["https://codeforces.com/contests", "https://atcoder.jp/contests/"]
    contests = []

    '''
    Scrapping Codeforces
    '''
    html_1 = requests.get(urls[0])
    scrapval_1 = bs4.BeautifulSoup(html_1.text, "html.parser")
    table_1 = scrapval_1.find('div', class_='datatable')
    contest_rows_1 = table_1.find_all('tr', {'data-contestid': True})
    

    for row in contest_rows_1:
        contest_name = row.find_all('td')[0].text.strip()
        start_time = row.find('span', class_='format-time').text.strip()
        start_time = msk_to_ist(start_time)
        length = row.find_all('td')[3].text.strip()
        
        contests.append({
            'name': contest_name,
            'start_time': start_time,
            'length': length,
            'url' : urls[0]
        })
    

    '''
    Scraping AtCoder
    '''
    html_2 = requests.get(urls[1])
    scrapval_2 = bs4.BeautifulSoup(html_2.text, "html.parser")
    table_2 = scrapval_2.find_all('div', id="contest-table-upcoming")
    contest_rows_2 = table_2[0].find_all('tr')
    contest_rows_2.pop(0)
    for x in contest_rows_2:
        contest_name = x.find_all('td')[1].find_all('a')[0].text.strip()
        start_time = x.find_all('td')[0].find_all('a')[0].text.strip()
        start_time = convert_to_ist(start_time)
        length = x.find_all('td')[2].text.strip()

        contests.append({
            'name': contest_name,
            'start_time': start_time,
            'length': length,
            'url' : urls[1]
        })

    context = {'contests' : contests}

    return render(request, 'cp.html', context)

"""
General Helper functions
"""

from datetime import datetime, timedelta

def convert_to_ist(time_str):
  """
  Converts a time string in the format "YYYY-MM-DD HH:MM:SS+OFFSET" 
  to Indian Standard Time (IST) with the format "MMM/DD/YYYY HH:MM"
  """
  original_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S%z")
  utc_time = original_time - timedelta(hours=int(time_str[-4:-2]), minutes=int(time_str[-2:]))
  ist_time = utc_time + timedelta(hours=5, minutes=30)

  return ist_time.strftime("%b/%d/%Y %H:%M")

def msk_to_ist(time_str):
  """
  Converts a time string in Moscow Time (MSK) format (MMM/DD/YYYY HH:MM) 
  to Indian Standard Time (IST) with the same format.
  """
  msk_time = datetime.strptime(time_str, "%b/%d/%Y %H:%M")
  utc_time = msk_time - timedelta(hours=3)
  ist_time = utc_time + timedelta(hours=5, minutes=30)

  return ist_time.strftime("%b/%d/%Y %H:%M")