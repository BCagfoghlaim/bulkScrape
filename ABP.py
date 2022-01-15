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

#PATH = 'C:\Program Files (x86)\chromedriver.exe'
#driver = webdriver.Chrome(PATH)

cards = ['1','2','3','4']
iterations = []
for item in cards:
    iterations.append(item)


def ABP(cards, iterations):
    startTime = time.time()
    sixthdriver = webdriver.Chrome(ChromeDriverManager().install())
    sid_df = pd.DataFrame(columns=['File Number', 'Due Date', 'Development Description', 'Received Date', 'Local Authority Name', 'URL', 'Search Term'])
    single_df = pd.DataFrame(columns=['File Number', 'Received Date', 'Local Authority Name', 'Applicant Name', 'Development Address', 'Development Description', 'URL', 'Search Term'])

    this_year = str(datetime.datetime.now().year)

    link = 'https://www.pleanala.ie/en-ie/lists/cases?list=I&year='+this_year
   
    sixthdriver.get(link)
    try:
        no_cookies = WebDriverWait(sixthdriver, 25).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="ccc-reject-settings"]/span'))
                        )
        no_cookies.click()
    except:
        pass
    
    for item in reversed(iterations):
        try:
            # print('1st bash')
            card = WebDriverWait(sixthdriver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div['+item+']/a'))
                        )
            print('Card ' +item+ ' found - move on to scrape')
            break
        except:
            print('ABP - Card ' + item + ' not found')
            cards.pop()
            print(cards)
            print(iterations)
            try:
                no_results = WebDriverWait(sixthdriver, 25).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/p'))
                                )
                if no_results.text == "No weekly lists found": 
                    no_results_df = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name', 'Deadline', 'Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])
                    no_results_df.to_csv('ABP Function.csv', index = False)
                    endTime = time.time()
                    timeDiff = endTime - startTime
                    print(f'Completed An Bord Pleanala (No Results) in {timeDiff:.2f} seconds')
                    return None
                else:
                    pass
            except:
                print('Not Enough Results')
                notEnoughResults_df = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name', 'Deadline', 'Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])
                notEnoughResults_df.to_csv('ABP Function.csv', index = False)
                endTime = time.time()
                timeDiff = endTime - startTime
                print(f'Completed An Bord Pleanala (ERROR: Not Enough Results) in {timeDiff:.2f} seconds')
                return None
            
    for item in cards:
        sixthdriver.get(link)
        
        try:
            no_cookies = WebDriverWait(sixthdriver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="ccc-reject-settings"]/span'))
                            )
            no_cookies.click()
        except:
            pass
       
        # sixthdriver.find_element_by_xpath('//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div['+item+']/a').click()
        card = WebDriverWait(sixthdriver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div['+item+']/a'))
                        )
        card.click()

        html = sixthdriver.page_source
        soup = BeautifulSoup(html, "lxml")

        try:
            multipleHeaders = sixthdriver.find_element_by_css_selector('h2')
        
            addresses = []
            locations = soup.findAll("span", {"class":"title"})  
            for location in locations:
                info = location.get_text(strip=True)
                addresses.append(info)

            applicants = []
            parties = sixthdriver.find_elements_by_xpath('//*[@id="maincontent"]/div/div/div/div/div/div/div/div/div/a/div/ul/li[1]')
            for party in parties:
                info = party.text
                applicants.append(info)

            list = []
            cells = soup.findAll("span", {"class":"details"})   
            for cell in cells:
                data = cell.get_text(strip=True)
                list.append(data)

            splitList = [list[i:i + 6] for i in range(0, len(list), 6)]

            currentLink = sixthdriver.current_url

            for list in splitList:
                list.append('An Bord Pleanala - SID')
                currentLink = 'https://www.pleanala.ie/en-ie/case/'+str(list[0])
                list.append(currentLink)
                list.append('N/A for SID')
            temp_df = pd.DataFrame(splitList, columns = ['File Number', 'Due Date', 'Development Description', 'Received Date', 'EIAR', 'NIS', 'Local Authority Name', 'URL', 'Search Term'])
            temp_df['Applicant Name'] = applicants
            temp_df = temp_df.drop(columns =['EIAR', 'NIS'])
            temp_df['Development Address'] = addresses
            sid_df = sid_df.append(temp_df, ignore_index=True)
        
        except:      
            row = []
            titleText = soup.find("p", {"class":"address"}).text
            titleSplit = titleText.split(":")
            fileNumber = titleSplit[0].strip()
            address = titleSplit[1].strip()
            receivedDate = soup.find("strong").text.strip()
            councilName = 'An Bord Pleanala - SID'
            applicant = sixthdriver.find_element_by_xpath('//*[@id="maincontent"]/div/div/div/div/div/div/div[1]/div/div[6]/div[2]/ul/li[1]/p').text
            description = soup.find("p", {"class":"case-summary"}).text
            url = 'https://www.pleanala.ie/en-ie/case/'+fileNumber
            searchTerm = 'N/A for SID'

            row.append(fileNumber)
            row.append(receivedDate)
            row.append(councilName)
            row.append(applicant)
            row.append(address)
            row.append(description)
            row.append(url)
            row.append(searchTerm)

            row_series = pd.Series(row, index = single_df.columns)
            single_df = single_df.append(row_series, ignore_index=True)

    sixthdriver.quit()                
    sid_df['File Number'] = sid_df['File Number'].str.replace('Case reference:','')
    sid_df['URL'] = sid_df['URL'].str.replace('Case reference:','')
    sid_df['Received Date'] = sid_df['Received Date'].str.replace('Date lodged:','')
    sid_df['Received Date'] = sid_df['Received Date'].str[:10]
    sid_df['Development Description'] = sid_df['Development Description'].str.replace('Description:','')
    sid_df = sid_df[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    sid_df = sid_df.append(single_df, ignore_index=True)
    sid_df['Received Date'] = pd.to_datetime(sid_df['Received Date'], format='%d/%m/%Y')
    sid_df['Deadline'] = sid_df['Received Date'] + pd.Timedelta(days=39)
    sid_df = sid_df[['File Number','Received Date','Local Authority Name', 'Deadline', 'Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    sid_df.to_csv('ABP Function.csv', index = False)
    endTime = time.time()
    timeDiff = endTime - startTime
    print(f'Completed An Bord Pleanala in {timeDiff:.2f} seconds')
    #return sid_df

ABP(cards, iterations)
