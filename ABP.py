import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4.builder import HTML_5
from pandas.io import html
from bs4 import BeautifulSoup
import pandas as pd
from os import link
from numpy import datetime64, select, split
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

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

this_year = str(datetime.datetime.now().year)

link = 'https://www.pleanala.ie/en-ie/lists/cases?list=I&year='+this_year

driver.get(link)

no_cookies = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="ccc-reject-settings"]/span'))
                    )
no_cookies.click()
driver.find_element_by_xpath('//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div[1]/a/span[3]/em').click()

html = driver.page_source
soup = BeautifulSoup(html, "lxml")

sections = soup.findAll("h2", {"class":"cell"})

addresses = []
locations = soup.findAll("span", {"class":"title"})  
for location in locations:
    info = location.get_text(strip=True)
    addresses.append(info)

applicants = []
parties = driver.find_elements_by_xpath('//*[@id="maincontent"]/div/div/div/div/div/div/div/div/div/a/div/ul/li[1]')
for party in parties:
    info = party.text
    applicants.append(info)

list = []
cells = soup.findAll("span", {"class":"details"})   
for cell in cells:
    data = cell.get_text(strip=True)
    list.append(data)

splitList = [list[i:i + 6] for i in range(0, len(list), 6)]

currentLink = driver.current_url

for list in splitList:
    list.append('An Bord Pleanala - SID')
    list.append(currentLink)
    list.append('Not Required for SID')
    
df = pd.DataFrame(splitList, columns = ['File Number', 'Due Date', 'Development Description', 'Received Date', 'EIAR', 'NIS', 'Local Authority Name', 'URL', 'Search Term'])
df['Applicant Name'] = applicants
df = df.drop(columns =['EIAR', 'NIS'])
df['Development Address'] = addresses
sid_df = df[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
sid_df['File Number'] = sid_df['File Number'].str.replace('Case reference:','')
sid_df['Received Date'] = sid_df['Received Date'].str.replace('Date lodged:','')
sid_df['Development Description'] = sid_df['Development Description'].str.replace('Description:','')
sid_df['Received Date'] = pd.to_datetime(sid_df['Received Date'], format='%d/%m/%Y')
driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed An Bord Pleanala in {timeDiff:.2f} seconds')

sid_df.to_csv ('sid.csv', index = False)
       
