from datetime import date
from os import link
from re import findall
from numpy import append, select
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import time
from bs4.builder import HTML_5
from pandas.io import html
from bs4 import BeautifulSoup
import pandas as pd

startTime = time.time()

yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d%m%Y')
today = datetime.datetime.now().strftime('%d%m%Y')

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

keywords = ['data cent', 'data storage', 'datacent', 'data']

mainList = []

wait = WebDriverWait(driver, 10)

kildareLink = 'http://webgeo.kildarecoco.ie/planningenquiry'
for keyword in keywords:

    driver.get(kildareLink)

    try:

        driver.find_element_by_id('cbDateSearch').click()
        dateFrom = driver.find_element_by_id('dateFrom')
        dateFrom.send_keys(yearAgo)
        dateTo = driver.find_element_by_id('dateTo')
        dateTo.send_keys(today)
    
        search = driver.find_element_by_id('txtPlDevDesc')
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)

        grid = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="plGrid"]/div[2]/table'))
        )
                                                
        button = driver.find_element_by_xpath('//*[@id="plGrid"]/div[3]/span[1]/span')
        button.click()
        button.send_keys('a')
        button.send_keys(Keys.RETURN)
        
        list = []
        rows = grid.find_elements_by_tag_name("tr")
        for row in rows:
            cells = row.find_elements_by_tag_name("td")
            
            for cell in cells:
                celldata = cell.text
                list.append(celldata)

        splitList = [list[i:i + 5] for i in range(0, len(list), 5)]

        for list in splitList:
            list.append('No Description')
            list.append(kildareLink)
            list.append(keyword)

        for list in splitList:
            mainList.append(list)

    except Exception:
        pass

df = pd.DataFrame(mainList,columns=['File Number','Local Authority Name','Applicant Name','Development Address','Received Date','Development Description', 'URL', 'Search Term'])
reorderDf = df[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
reorderDf.loc[:,'Received Date'] = pd.to_datetime(reorderDf.loc[:, 'Received Date'], format='%d/%m/%Y')
reorderDf['File Number'] = reorderDf['File Number'].astype(str)
clean_df = reorderDf.drop_duplicates(subset=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL'],keep= 'last')
kildare_df = clean_df.sort_values(['Received Date', 'Local Authority Name'], ascending=[False, True])
kildare_df.to_csv ('kildare.csv', index = False)

driver.quit()

endTime = time.time()

timeDiff = endTime - startTime
print(f'Completed in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')
