from re import L
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

yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d/%m/%Y')
today = datetime.datetime.now().strftime('%d/%m/%Y')
dateRange = yearAgo+' - '+today
print(dateRange)
data_frame = pd.DataFrame(columns=['Applicant Name', 'DECISION DATE', 'FINAL GRANT DATE', 'Development Address', 'File Number', 'Development Description',	'Received Date', 'Local Authority Name', 'URL', 'Search Term'])

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
councils = ['fingal', 'dunlaoghaire']
keywords = ['data cent', 'data storage', 'datacent', 'data','tunnel']

for council in councils:
    for keyword in keywords:
        link = 'https://planning.agileapplications.ie/'+council+'/search-applications/results?criteria=%7B%22openApplications%22:%22false%22,%22proposal%22:%22'+keyword+'%22,%22registrationDateFrom%22:%222020-07-08%22,%22registrationDateTo%22:%222021-07-08%22%7D'
        driver.get(link)

        try:
            cookies = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#header > sas-cookie-consent > section > section > div.alert.alert-info > button'))
            )
            cookies.click()
        except Exception:
            pass

        try:
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="no_results"]'))
            )

            print('No '+council+' results for '+keyword)
            blankDf = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])
            blankDf.to_csv ('dunlaoghaire-fingal.csv', index = False)
        except:

            driver.set_window_size(480, 600)
            # time.sleep(5)
            try:
                
                seeMore = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-view"]/search-applications-results/section/sas-table/div[2]/div[4]/div/div/a/em'))
                    )
                i=0
                while seeMore.is_displayed() == True:
                    seeMore.click()
                    time.sleep(2)

                print('Clicked'+i+'times')
                i= i + 1
            except:
                print('Single page of results')

            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")

            tbl = soup.find("tbody")
            rows = soup.findAll("tr")

            list = []
            for row in rows:
                cells = row.findAll("td")   
                for cell in cells:
                    data = cell.get_text(strip=True)
                    list.append(data)

            del list[:8]
            startPosition = int((len(list)-8)/2)
            endPosition = int(startPosition + 8)

            try:
                del list[startPosition:endPosition]
            except Exception:
                pass
            splitList = [list[i:i + 7] for i in range(0, len(list), 7)]
            for section in splitList:
                if 'fingal' in link:
                    section.append('Fingal Co. Co.')
                    # print('FINGAL IN LINK')
                    section.append(link)
                    section.append(keyword)
                elif 'dunlaoghaire' in link:
                    section.append('Dun Laoghaire Co. Co.')
                    # print('DUN LAOGHAIRE IN LINK')
                    section.append(link)
                    section.append(keyword)
                else:
                    section.append(link)

            tempdf = pd.DataFrame(splitList,columns=['File Number',	'Development Description',	'Development Address',	'Received Date', 'DECISION DATE', 'FINAL GRANT DATE', 'Applicant Name',	'Local Authority Name', 'URL', 'Search Term'])
            df = tempdf.drop_duplicates()
            cleanDf = df.drop(columns =['DECISION DATE', 'FINAL GRANT DATE'])
            data_frame = data_frame.append(cleanDf, ignore_index=True)

data_frame = data_frame.drop_duplicates()
data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
sorted_df = data_frame.sort_values(['Received Date', 'Local Authority Name'], ascending=[False, True])
reorderDf = sorted_df[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
reorderDf.to_csv ('fingal-dunlaoghaire.csv', index = False)
   
# finally:
driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')
