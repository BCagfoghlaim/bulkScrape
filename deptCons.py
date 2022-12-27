import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from tkinter import *  
from tkinter import messagebox
from selenium.common.exceptions import TimeoutException
import gspread
from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials
from webdriver_manager.chrome import ChromeDriverManager
from googleapiclient import discovery
from threading import Thread
import os
import webbrowser
import sys
import re

# PATH = 'C:\Program Files (x86)\chromedriver.exe'
# driver = webdriver.Chrome(PATH)
driver = webdriver.Chrome(ChromeDriverManager().install())

yearAgoString = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d/%m/%Y')
yearAgo = time.strptime(yearAgoString, "%d/%m/%Y")

def deptCons():
    startTime = time.time()

    deptCons_df = pd.DataFrame(columns=['Received Date''Development Description'])

    seventhdriver = webdriver.Chrome(ChromeDriverManager().install())

    link = 'https://www.gov.ie/en/search/?type=consultations&organisation=department-of-the-environment-climate-and-communications'

    seventhdriver.get(link)
    
    pages = seventhdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/div[2]/div/div/div[2]')
    pagetext = pages.text
    pagenum = pagetext.split("/ ")
    totalPageNum = int(pagenum[1])
    
    finalList = []

    page = 0
    while page < totalPageNum:
        html = seventhdriver.page_source
        soup = BeautifulSoup(html, "lxml")
                    
        tbl = soup.findAll("ul")
        consList = tbl[6]
        descriptons = []
        deets = []
        links = []
        descriptonTags = consList.findAll("a")
        deetTags = consList.findAll("p")
        for desc in descriptonTags:
            descriptons.append(desc.text)
        for deet in deetTags:
            data = deet.extract()
            deets.append(data)
        for link in consList.find_all('a'):
            url = link['href']
            links.append(url)
       
        deets = [str(deet) for deet in deets]
        deets = [deet.replace('Department of Agriculture, Food and the Marine;','') for deet in deets]
        
        links = ['https://www.gov.ie' + url for url in links]

        listToStr = ';'.join([str(elem) for elem in deets])
        details = listToStr.split(";")
        
        splitList = [details[i:i + 5] for i in range(0, len(details), 5)]
        dates = []
        for list in splitList:
            dates.append(list[1])
        
        try:
            seventhdriver.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/div[2]/div/div/div[3]/a/span[2]').click()
        except:
            pass
        
        i = 0
        while i < len(dates):
            thisDate = dates[i].strip()
            realDate = datetime.datetime.strptime(thisDate, '%d %B %Y').strftime('%d/%m/%Y')
            actualDate = time.strptime(realDate, "%d/%m/%Y")
            if actualDate  > yearAgo:
                finalList.append(dates[i])
                finalList.append(descriptons[i])
                finalList.append(links[i])
                i = i + 1

            else:
                page = totalPageNum
                i = len(dates)

        page = page+1

    seventhdriver.quit()
    newSplit = [finalList[i:i + 3] for i in range(0, len(finalList), 3)]
    deptCons_df = pd.DataFrame(newSplit, columns = ['Received Date', 'Development Description', 'URL'])
    deptCons_df['Received Date'] = deptCons_df['Received Date'].str.strip()
    deptCons_df['Received Date'] = pd.to_datetime(deptCons_df['Received Date'])
    # deptCons_df['Received Date'] = pd.to_datetime(deptCons_df['Received Date'], format='%d/%m/%Y')
    deptCons_df['File Number'] = 'N/A for DECC'
    deptCons_df['Local Authority Name'] = 'Dept. Environment/Climate'
    deptCons_df['Applicant Name'] = 'Gov Consultation'
    deptCons_df['Development Address'] = 'N/A for DECC'
    deptCons_df['Search Term'] = 'N/A for DECC'
    
    deptCons_df['Deadline'] = deptCons_df['Received Date'] + pd.Timedelta(days=25)
    deptCons_df = deptCons_df[['File Number','Received Date','Local Authority Name','Deadline','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]

    deptCons_df.to_csv ('Dept Consultation.csv', index = False)
    
    endTime = time.time()

    timeDiff = endTime - startTime
    print(f'Completed Dept Consultations in {timeDiff:.2f} seconds')
    # return deptCons_df

deptCons()
