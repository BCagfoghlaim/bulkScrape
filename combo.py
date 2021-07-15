import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4.builder import HTML_5
from pandas.io import html
from bs4 import BeautifulSoup
import pandas as pd
from os import link
from numpy import select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

beginTime = time.time()

#-------------------------Bulk------------------------------------

startTime = time.time()

data_frame = pd.DataFrame(columns=['File Number','Application Status','Decision Due Date','Decision Date','Decision Code',
'Received Date','Applicant Name','Development Address','Development Description','Local Authority Name', 'URL', 'Search Term'])

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

keywords = ['data', 'gas']

standardLinks = [
    'http://www.eplanning.ie/CarlowCC/SearchExact/Description',
    'http://www.eplanning.ie/CavanCC/SearchExact/Description',
    'http://www.eplanning.ie/ClareCC/SearchExact/Description',
    'http://planning.corkcoco.ie/ePlan/SearchExact/Description',
    'http://planning.corkcity.ie/SearchExact/Description',
    'http://www.eplanning.ie/DonegalCC/SearchExact/Description',
    'https://geo.galwaycity.ie/ePlan5/SearchExact/Description',
    'http://www.eplanning.ie/GalwayCC/SearchExact/Description',
    'http://www.eplanning.ie/KerryCC/SearchExact/Description',
    'http://www.eplanning.ie/KilkennyCC/SearchExact/Description',
    'http://www.eplanning.ie/LaoisCC/SearchExact/Description',
    'http://www.eplanning.ie/LeitrimCC/SearchExact/Description',
    'http://eplan.limerick.ie/SearchExact/Description',
    'http://www.eplanning.ie/LouthCC/SearchExact/Description',
    'http://www.eplanning.ie/LongfordCC/SearchExact/Description',
    'http://www.eplanning.ie/MayoCC/SearchExact/Description',
    'http://www.eplanning.ie/MeathCC/SearchExact/Description',
    'http://www.eplanning.ie/MonaghanCC/SearchExact/Description',
    'http://www.eplanning.ie/OffalyCC/SearchExact/Description',
    'http://www.eplanning.ie/RoscommonCC/SearchExact/Description',
    'http://www.eplanning.ie/SligoCC/SearchExact/Description',
    'http://www.eplanning.ie/TipperaryCC/SearchExact/Description',
    'http://www.eplanning.ie/WaterfordCCC/SearchExact/Description',
    'http://www.eplanning.ie/WestmeathCC/SearchExact/Description',
    'http://www.eplanning.ie/WicklowCC/SearchExact/Description'
]

for keyword in keywords:
    for link in standardLinks:

        driver.get(link)

        select = Select(driver.find_element_by_id('LstTimeLimit'))
        select.select_by_visible_text('Within 1 years from today')
        
        search = driver.find_element_by_id('TxtDevdescription')
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        tbl = soup.find("table",{"class":"table"})

        tempdf = pd.read_html(str(tbl))[0]
        tempdf['URL'] = link
        tempdf['Search Term'] = keyword
        data_frame = data_frame.append(tempdf, ignore_index=True)
        
        #PAGINATION
        while soup.find('li',{"class":"PagedList-skipToNext"}):
            driver.find_element_by_link_text("»").click()
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")

            tbl = soup.find("table",{"class":"table"})

            tempdf = pd.read_html(str(tbl))[0]
            tempdf['URL'] = link
            tempdf['Search Term'] = keyword
            data_frame = data_frame.append(tempdf, ignore_index=True)

data_frame = data_frame.drop(columns =['Application Status','Decision Due Date','Decision Date','Decision Code'])
data_frame = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term']]
data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
data_frame['File Number'] = data_frame['File Number'].astype(str)
bulk_df = data_frame
    
driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed Bulk in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')

#---------------------------------KILDARE---------------------------------------------------------------

startTime = time.time()

yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d%m%Y')
today = datetime.datetime.now().strftime('%d%m%Y')

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

# keywords = ['data cent', 'data storage', 'datacent', 'data']

mainList = []

wait = WebDriverWait(driver, 10)

kildareLink = 'http://webgeo.kildarecoco.ie/planningenquiry'
for keyword in keywords:

    driver.get(kildareLink)
    time.sleep(1.5)

    driver.find_element_by_id('cbDateSearch').click()
    dateFrom = driver.find_element_by_id('dateFrom')
    dateFrom.send_keys(yearAgo)
    dateTo = driver.find_element_by_id('dateTo')
    dateTo.send_keys(today)

    search = driver.find_element_by_id('txtPlDevDesc')
    search.send_keys(keyword)
    search.send_keys(Keys.RETURN)

    try:
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

data_frame = pd.DataFrame(mainList,columns=['File Number','Local Authority Name','Applicant Name','Development Address','Received Date','Development Description', 'URL', 'Search Term'])
reorderDf = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
reorderDf['Received Date'] = pd.to_datetime(reorderDf['Received Date'])
reorderDf['File Number'] = reorderDf['File Number'].astype(str)
kildare_df = reorderDf

driver.quit()

endTime = time.time()

timeDiff = endTime - startTime
print(f'Completed Kildare in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')

#----------------------------Fingal-Dun Laoghaire--------------------------------------------

startTime = time.time()

yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d/%m/%Y')
today = datetime.datetime.now().strftime('%d/%m/%Y')
dateRange = yearAgo+' - '+today

data_frame = pd.DataFrame(columns=['Applicant Name', 'DECISION DATE', 'FINAL GRANT DATE', 'Development Address', 'File Number', 'Development Description',	'Received Date', 'Local Authority Name', 'URL', 'Search Term'])

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
councils = ['fingal', 'dunlaoghaire']

# keywords = ['data cent', 'data storage', 'datacent', 'data','tunnel']

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
            
        except:

        #  CLICK TO NEXT PAGE HERE AND SEE IF THE CODE STILL WORKS
            driver.set_window_size(480, 600)
            
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
            except Exception:
                pass
                
            #CODE -------------------------------------------------
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
                    section.append(link)
                    section.append(keyword)
                elif 'dunlaoghaire' in link:
                    section.append('Dun Laoghaire Co. Co.')
                    section.append(link)
                    section.append(keyword)
                else:
                    section.append(link)

            tempdf = pd.DataFrame(splitList,columns=['File Number',	'Development Description',	'Development Address',	'Received Date', 'DECISION DATE', 'FINAL GRANT DATE', 'Applicant Name',	'Local Authority Name', 'URL', 'Search Term'])
            df = tempdf.drop_duplicates()
            cleanDf = df.drop(columns =['DECISION DATE', 'FINAL GRANT DATE'])
            data_frame = data_frame.append(cleanDf, ignore_index=True)

data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
data_frame = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
fingalDL_df = data_frame
#-------------------------------------------------- CODE
   
driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed Fingal/Dun Laoghaire in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')

#------------------------------------Wexford--------------------------------------------------

startTime = time.time()

data_frame = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)

# keywords = ['house']

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
    
    tempdf['File Number'] = fileNumbers
    tempdf['Received Date'] = dates
    tempdf['Local Authority Name'] = 'Wexford Co. Co.'
    tempdf['Applicant Name'] = applicants
    tempdf['Development Address'] = addresses
    tempdf['Development Description'] = 'No Description'
    tempdf['URL'] = link
    tempdf['Search Term'] = keyword
    data_frame = data_frame.append(tempdf, ignore_index=True)

data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
data_frame['File Number'] = data_frame['File Number'].astype(str)
wexford_df = data_frame

driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed Wexford in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')

#----------------------COMBO-------------------------------

frames = [bulk_df, kildare_df, fingalDL_df, wexford_df]

combo_df = pd.concat(frames)

combo_df = combo_df.drop_duplicates(subset=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL'],keep= 'last')
combo_df = combo_df.sort_values(['Received Date', 'Local Authority Name'], ascending=[False, True])

combo_df.to_csv ('combo.csv', index = False)

finishTime = time.time()
totalTime = finishTime - beginTime

mins = str(round((totalTime%3600)//60))
seconds = str(round((totalTime%3600)%60))
print("Completed Total in {} mins {} seconds".format(mins, seconds))
