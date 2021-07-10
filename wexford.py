from re import L, findall
from pandas.core.frame import DataFrame
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from bs4.builder import HTML_5
from pandas.io import html
from bs4 import BeautifulSoup
import pandas as pd

startTime = time.time()

data_frame = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

# keywords = ['roof','fence','data','gas','tunnel']
keywords = ['house']

link = 'https://dms.wexfordcoco.ie/advanced.php'

for keyword in keywords:
    tempdf = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])

    driver.get(link)

    try:
        cookies = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#welcome > div > table > tbody > tr > td:nth-child(1) > a'))
        )
        cookies.click()
    except Exception:
        pass

    select = Select(driver.find_element_by_id('lr'))
    select.select_by_visible_text('Within 1 year from today')
    
    search = driver.find_element_by_id('pp')
    search.send_keys(keyword)
    search.send_keys(Keys.RETURN)
    time.sleep(5)

    select = Select(driver.find_element_by_css_selector('#grd > div > div.pDiv > div.pDiv2 > div:nth-child(1) > select'))
    select.select_by_visible_text('100  ')
    time.sleep(4)

    pageNumber = int(driver.find_element_by_css_selector('#grd > div > div.pDiv > div.pDiv2 > div:nth-child(5) > span > span').text)
    result = 1

    fileNumbers = []
    dates = []
    applicants = []
    addresses = []

    while result <= pageNumber:
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        
        tds = soup.find_all('div', style='text-align: left; width: 75px; white-space: normal;')
        for td in tds:
            data = td.get_text(strip=True)
            fileNumbers.append(data)

        
        tds = soup.find_all('div', style='text-align: left; width: 65px; white-space: normal;')
        for td in tds:
            data = td.get_text(strip=True)
            dates.append(data)

        
        tds = soup.find_all('div', style='text-align: left; width: 190px; white-space: normal;')
        for td in tds:
            data = td.get_text(strip=True)
            applicants.append(data)   

        
        tds = soup.find_all('div', style='text-align: left; width: 275px; white-space: normal;')
        for td in tds:
            data = td.get_text(strip=True)
            addresses.append(data)

        driver.find_element_by_css_selector("#grd > div > div.pDiv > div.pDiv2 > div:nth-child(7) > div.pNext.pButton > span").click()
        time.sleep(2)
        result = result + 1

        pageNumber = int(driver.find_element_by_css_selector('#grd > div > div.pDiv > div.pDiv2 > div:nth-child(5) > span > span').text)
        print(f'pagenumber during: {pageNumber:.2f}')
        print(f'result during: {result:.2f}')
    
    tempdf['File Number'] = fileNumbers
    tempdf['Received Date'] = dates
    tempdf['Local Authority Name'] = 'Wexford Co. Co.'
    tempdf['Applicant Name'] = applicants
    tempdf['Development Address'] = addresses
    tempdf['Development Description'] = 'No Description'
    tempdf['URL'] = link
    tempdf['Search Term'] = keyword
    data_frame = data_frame.append(tempdf, ignore_index=True)

#CHOP UP DATAFRAME
data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
data_frame['File Number'] = data_frame['File Number'].astype(str)
clean_df = data_frame.drop_duplicates(subset=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL'],keep= 'last')
wexford_df = clean_df.sort_values(['Received Date', 'Local Authority Name'], ascending=[False, True])
wexford_df.to_csv ('wexford.csv', index = False)

# finally:
driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')
