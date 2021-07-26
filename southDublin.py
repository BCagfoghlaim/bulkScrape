import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4.builder import HTML_5
from pandas.io import html
from bs4 import BeautifulSoup
import pandas as pd
from os import link
from numpy import add, select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from tkinter import *  
from tkinter import messagebox, font
from selenium.common.exceptions import TimeoutException
import gspread
from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials
from webdriver_manager.chrome import ChromeDriverManager

startTime = time.time()

yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d/%m/%Y')

data_frame = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term', 'Comments'])
tempdf = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term', 'Comments'])

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

keywords = ['asjdfgjfdgkjf']

for keyword in keywords:

    link = 'http://www.sdublincoco.ie/Planning/Applications?p=1&prop='+keyword

    driver.get(link)

    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    fileNos = soup.findAll("h3",{"class":"responsiveheader"})
    rows = soup.findAll("dl")

    results = soup.find("li",{"class":"totals"})
    resultsFigure = results.get_text(strip=True)
    firstNum = resultsFigure[4:7]
    lastNum = resultsFigure[9:16]
    firstNum = int(''.join(i for i in firstNum if i.isdigit()))
    lastNum = lastNum[:lastNum.index("(")]
    lastNum = int(''.join(i for i in lastNum if i.isdigit()))

    while firstNum <= lastNum:
        tempdf = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term', 'Comments'])
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        fileNos = soup.findAll("h3",{"class":"responsiveheader"})
        rows = soup.findAll("dl")

        fileNumbers = []
        dates = []
        applicants =[]
        addresses = []

        for fileNo in fileNos:
            data = fileNo.get_text(strip=True)
            fileNumbers.append(data)

        list = []
        for row in rows:
            cells = row.findAll("dd")   
            for cell in cells:
                data = cell.get_text(strip=True)
                list.append(data)

        splitList = [list[i:i + 4] for i in range(0, len(list), 4)]

        for miniList in splitList:
            dates.append(miniList[0])
            applicants.append(miniList[2])
            addresses.append(miniList[3])

        firstNum = firstNum + 1   
        try:
            driver.find_element_by_xpath('//*[@id="main"]/div[2]/div/div[1]/div/div/table/caption/ul/li[4]/a').click()
        except Exception:
            pass

        print(fileNumbers)
        tempdf['File Number'] = fileNumbers
        tempdf['Received Date'] = dates
        tempdf['Local Authority Name'] = 'South Dublin Co. Co.'
        tempdf['Applicant Name'] = applicants
        tempdf['Development Address'] = addresses
        tempdf['Development Description'] = 'No Description'
        tempdf['URL'] = link
        tempdf['Search Term'] = keyword

        data_frame = data_frame.append(tempdf, ignore_index=True)

data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'], format='%d/%m/%Y')
data_frame = data_frame[(data_frame['Received Date'] >= yearAgo)]
data_frame.to_csv ('southDub.csv', index = False)

driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed South Dublin in {timeDiff:.2f} seconds')
