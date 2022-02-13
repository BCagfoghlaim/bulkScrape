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
#from webdriver_manager.chrome import ChromeDriverManager
from googleapiclient import discovery
from threading import Thread
import os
import webbrowser
import sys

from selenium import webdriver

beginTime = time.time()

variables[ 'Error' ] = 'Test Error'

sheet_url = 'https://docs.google.com/spreadsheets/d/1ajEtdL9kquS-zB01gf1JR_L6gW0U7_yc8GzcAyLNZp8/export?format=csv&gid=0'
existing_df = pd.read_csv(sheet_url)
existing_df.to_csv ('Existing Applications.csv', index = False)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0')

keywords =['data storage', 'gas', 'gas plant', 'data hall', 'data cent', 'datacent', 'data-cent', 'energy cent', 'kv substation']

driver = webdriver.Chrome(options = options)
driver.set_page_load_timeout(30)

#--------------------------- BULK -------------------------
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
    'https://www.eplanning.ie/LimerickCCC/SearchExact/Description',
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
def bulk(keywords,standardLinks):
    startTime = time.time()
    data_frame = pd.DataFrame(columns=['File Number','Application Status','Decision Due Date','Decision Date','Decision Code','Received Date','Applicant Name','Development Address','Development Description','Local Authority Name', 'URL', 'Search Term'])

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
            data_frame = pd.concat([data_frame,tempdf])
            
            #PAGINATION
            while soup.find('li',{"class":"PagedList-skipToNext"}):
                driver.find_element_by_link_text("»").click()
                html = driver.page_source
                soup = BeautifulSoup(html, "lxml")

                tbl = soup.find("table",{"class":"table"})

                tempdf = pd.read_html(str(tbl))[0]
                tempdf['URL'] = link
                tempdf['Search Term'] = keyword
                data_frame = pd.concat([data_frame,tempdf])       

    driver.quit()
    data_frame = data_frame.drop(columns =['Application Status','Decision Due Date','Decision Date','Decision Code'])
    data_frame = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term']]
    data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'], format='%d/%m/%Y')
    data_frame['File Number'] = data_frame['File Number'].astype(str)
    data_frame['URL'] = data_frame['URL'].str.replace('SearchExact/Description','AppFileRefDetails/')
    data_frame['URL']=data_frame['URL'] + data_frame['File Number'] + '/0'
    bulk_df = data_frame
    bulk_df.to_csv ('Bulk Function.csv', index = False)
    endTime = time.time()
    timeDiff = endTime - startTime
    print(f'Completed Bulk in {timeDiff:.2f} seconds')
    # return bulk_df

try:
    bulk(keywords,standardLinks)
except:
    variables[ 'Error' ] = 'Error in Bulk Function'

#--------------------------- Kildare -------------------------
def KildareScript(keywords,attempts):
    startTime = time.time()
    #seconddriver =  webdriver.Chrome(ChromeDriverManager().install())
    seconddriver = webdriver.Chrome(options = options)
    kildareLink = 'http://webgeo.kildarecoco.ie/planningenquiry'
    yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d%m%Y')
    today = datetime.datetime.now().strftime('%d%m%Y')
    mainList = []
    wait = WebDriverWait(seconddriver, 10)

    while int(attempts) < 3:
        try:
            seconddriver.set_page_load_timeout(30)  
            for keyword in keywords:
   
                seconddriver.get(kildareLink)

                seconddriver.find_element_by_id('cbDateSearch').click()
                dateFrom = seconddriver.find_element_by_id('dateFrom')
                dateFrom.send_keys(yearAgo)
                dateTo = seconddriver.find_element_by_id('dateTo')
                dateTo.send_keys(today)

                search = seconddriver.find_element_by_id('txtPlDevDesc')
                search.send_keys(keyword)
                search.send_keys(Keys.RETURN)
                time.sleep(2)

                noResults = seconddriver.find_element_by_id('noResultsPlGridDiv')

                if noResults.is_displayed():
                    print('No Kildare results for '+keyword)
                    #print('-------------------------------')
                
                else:                
                    grid = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="plGrid"]/div[2]/table'))
                    )
                                                            
                    button = seconddriver.find_element_by_xpath('//*[@id="plGrid"]/div[3]/span[1]/span')
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
                    # print('success for '+keyword)
                                        
            attempts = 3
            # print('Done')

        except TimeoutException:
            print("timeout error")
            attempts = attempts + 1
            KildareScript(keywords,attempts)
        break

    seconddriver.quit()
    data_frame = pd.DataFrame(mainList,columns=['File Number','Local Authority Name','Applicant Name','Development Address','Received Date','Development Description', 'URL', 'Search Term'])
    reorderDf = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    reorderDf['Received Date'] = pd.to_datetime(reorderDf['Received Date'], format='%d/%m/%Y')
    reorderDf['File Number'] = reorderDf['File Number'].astype(str)
    kildare_df = reorderDf
    kildare_df.to_csv ('Kildare Function.csv', index = False)
    endTime = time.time()
    timeDiff = endTime - startTime
    print(f'Completed Kildare in {timeDiff:.2f} seconds')
    # return kildare_df
    
try:
    KildareScript(keywords,0)
except:
    variables[ 'Error' ] = 'Error in Kildare Function'

#-------------------------- Dublin City/Fingal/Dun Laoghaire -----------

def dublincity(keywords):
    dubCitystartTime = time.time()
    # councils = ['dublincity']
    council = 'dublincity'
#    thirdAdriver =  webdriver.Chrome(ChromeDriverManager().install())
    thirdAdriver = webdriver.Chrome(options = options)
    yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    data_frame = pd.DataFrame(columns=['Applicant Name', 'DECISION DATE', 'FINAL GRANT DATE', 'Development Address', 'File Number', 'Development Description',	'Received Date', 'Local Authority Name', 'URL', 'Search Term'])
    # for council in councils:
    for keyword in keywords:
        link = 'https://planning.agileapplications.ie/'+council+'/search-applications/results?criteria=%7B%22proposal%22:%22'+keyword+'%22,%22openApplications%22:%22false%22,%22registrationDateFrom%22:%22'+yearAgo+'%22,%22registrationDateTo%22:%22'+today+'%22%7D'
    
        thirdAdriver.get(link)

        try:
            cookies = WebDriverWait(thirdAdriver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#header > sas-cookie-consent > section > section > div.alert.alert-info > button'))
            )
            cookies.click()
        except Exception:
            pass

        try:
            WebDriverWait(thirdAdriver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="no_results"]'))
            )
            
        except:

            thirdAdriver.set_window_size(480, 600)
            
            try:
                
                seeMore = WebDriverWait(thirdAdriver, 8).until(
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
                
            html = thirdAdriver.page_source
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
                if 'dublincity' in link:
                    section.append('Dublin City Council')
                    section.append(link)
                    section.append(keyword)
                # elif 'fingal' in link:
                #     section.append('Fingal Co. Co.')
                #     section.append(link)
                #     section.append(keyword)
                # elif 'dunlaoghaire' in link:
                #     section.append('Dun Laoghaire Co. Co.')
                #     section.append(link)
                #     section.append(keyword)
                else:
                    section.append(link)

            tempdf = pd.DataFrame(splitList,columns=['File Number',	'Development Description',	'Development Address',	'Received Date', 'DECISION DATE', 'FINAL GRANT DATE', 'Applicant Name',	'Local Authority Name', 'URL', 'Search Term'])
            df = tempdf.drop_duplicates()
            cleanDf = df.drop(columns =['DECISION DATE', 'FINAL GRANT DATE'])
            data_frame = pd.concat([data_frame,cleanDf])
    
    thirdAdriver.quit()
    data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
    data_frame = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    data_frame['URL'] = data_frame['URL'].str.replace(' ','%20')
    dublinCity_df = data_frame
    dublinCity_df.to_csv ('DublinCity Function.csv', index = False)
    dubCityendTime = time.time()
    timeDiff = dubCityendTime - dubCitystartTime
    print(f'Completed Dublin-City in {timeDiff:.2f} seconds')
    # return dublinCity_df

def fingal(keywords):
    fingalstartTime = time.time()
    # councils = ['fingal']
    council = 'fingal'
#    thirdBdriver =  webdriver.Chrome(ChromeDriverManager().install())
    thirdBdriver = webdriver.Chrome(options = options)
    yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    data_frame = pd.DataFrame(columns=['Applicant Name', 'DECISION DATE', 'FINAL GRANT DATE', 'Development Address', 'File Number', 'Development Description',	'Received Date', 'Local Authority Name', 'URL', 'Search Term'])
    # for council in councils:
    for keyword in keywords:
        link = 'https://planning.agileapplications.ie/'+council+'/search-applications/results?criteria=%7B%22proposal%22:%22'+keyword+'%22,%22openApplications%22:%22false%22,%22registrationDateFrom%22:%22'+yearAgo+'%22,%22registrationDateTo%22:%22'+today+'%22%7D'
    
        thirdBdriver.get(link)

        try:
            cookies = WebDriverWait(thirdBdriver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#header > sas-cookie-consent > section > section > div.alert.alert-info > button'))
            )
            cookies.click()
        except Exception:
            pass

        try:
            WebDriverWait(thirdBdriver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="no_results"]'))
            )
            
        except:

            thirdBdriver.set_window_size(480, 600)
            
            try:
                
                seeMore = WebDriverWait(thirdBdriver, 8).until(
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
                
            html = thirdBdriver.page_source
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
                # elif 'dunlaoghaire' in link:
                #     section.append('Dun Laoghaire Co. Co.')
                #     section.append(link)
                #     section.append(keyword)
                # elif 'dublincity' in link:
                #     section.append('Dublin City Council')
                #     section.append(link)
                #     section.append(keyword)
                else:
                    section.append(link)

            tempdf = pd.DataFrame(splitList,columns=['File Number',	'Development Description',	'Development Address',	'Received Date', 'DECISION DATE', 'FINAL GRANT DATE', 'Applicant Name',	'Local Authority Name', 'URL', 'Search Term'])
            df = tempdf.drop_duplicates()
            cleanDf = df.drop(columns =['DECISION DATE', 'FINAL GRANT DATE'])
            data_frame = pd.concat([data_frame,cleanDf])
    
    thirdBdriver.quit()
    data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
    data_frame = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    data_frame['URL'] = data_frame['URL'].str.replace(' ','%20')
    fingal_df = data_frame
    fingal_df.to_csv ('Fingal Function.csv', index = False)
    fingalendTime = time.time()
    timeDiff = fingalendTime - fingalstartTime
    print(f'Completed fingal in {timeDiff:.2f} seconds')
    # return dublin_df

def dunlaoghaire(keywords):
    dunlaoghairestartTime = time.time()
    # councils = ['dunlaoghaire']
    council = 'dunlaoghaire'
    #thirdCdriver =  webdriver.Chrome(ChromeDriverManager().install())
    thirdCdriver = webdriver.Chrome(options = options)
    yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    data_frame = pd.DataFrame(columns=['Applicant Name', 'DECISION DATE', 'FINAL GRANT DATE', 'Development Address', 'File Number', 'Development Description',	'Received Date', 'Local Authority Name', 'URL', 'Search Term'])
    # for council in councils:
    for keyword in keywords:
        link = 'https://planning.agileapplications.ie/'+council+'/search-applications/results?criteria=%7B%22proposal%22:%22'+keyword+'%22,%22openApplications%22:%22false%22,%22registrationDateFrom%22:%22'+yearAgo+'%22,%22registrationDateTo%22:%22'+today+'%22%7D'
    
        thirdCdriver.get(link)

        try:
            cookies = WebDriverWait(thirdCdriver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#header > sas-cookie-consent > section > section > div.alert.alert-info > button'))
            )
            cookies.click()
        except Exception:
            pass

        try:
            WebDriverWait(thirdCdriver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="no_results"]'))
            )
            
        except:

            thirdCdriver.set_window_size(480, 600)
            
            try:
                
                seeMore = WebDriverWait(thirdCdriver, 8).until(
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
                
            html = thirdCdriver.page_source
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
                if 'dunlaoghaire' in link:
                    section.append('Dun Laoghaire Co. Co.')
                    section.append(link)
                    section.append(keyword)
                # elif 'fingal' in link:
                #     section.append('Fingal Co. Co.')
                #     section.append(link)
                #     section.append(keyword)
                # elif 'dublincity' in link:
                #     section.append('Dublin City Council')
                #     section.append(link)
                #     section.append(keyword)
                else:
                    section.append(link)

            tempdf = pd.DataFrame(splitList,columns=['File Number',	'Development Description',	'Development Address',	'Received Date', 'DECISION DATE', 'FINAL GRANT DATE', 'Applicant Name',	'Local Authority Name', 'URL', 'Search Term'])
            df = tempdf.drop_duplicates()
            cleanDf = df.drop(columns =['DECISION DATE', 'FINAL GRANT DATE'])
            data_frame = pd.concat([data_frame,cleanDf])
    
    thirdCdriver.quit()
    data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
    data_frame = data_frame[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    data_frame['URL'] = data_frame['URL'].str.replace(' ','%20')
    dunlaoghaire_df = data_frame
    dunlaoghaire_df.to_csv ('Dunlaoghaire Function.csv', index = False)
    dunlaoghaireendTime = time.time()
    timeDiff = dunlaoghaireendTime - dunlaoghairestartTime
    print(f'Completed dunlaoghaire in {timeDiff:.2f} seconds')
    # return dublin_df

try:
    dublincity(keywords)
except:
    variables[ 'Error' ] = 'Error in Dublin City Function'

try:
    fingal(keywords)
except:
    variables[ 'Error' ] = 'Error in Fingal Function'    
    
try:
    dunlaoghaire(keywords)
except:
    variables[ 'Error' ] = 'Error in Dun Laoghaire Function'

dunlaoghaire(keywords)

#------------------------------------------Wexford--------------------------------------------
def wexford(keywords):
    startTime = time.time()
    #fourthdriver =  webdriver.Chrome(ChromeDriverManager().install())
    fourthdriver = webdriver.Chrome(options = options)
    link = 'https://dms.wexfordcoco.ie/advanced.php'
    data_frame = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])
    for keyword in keywords:
        tempdf = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])

        fourthdriver.get(link)

        try:
            cookies = WebDriverWait(fourthdriver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#welcome > div > table > tbody > tr > td:nth-child(1) > a'))
            )
            cookies.click()
        except Exception:
            pass

        select = Select(fourthdriver.find_element_by_id('lr'))
        select.select_by_visible_text('Within 1 year from today')
        
        search = fourthdriver.find_element_by_id('pp')
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)
        time.sleep(5)

        select = Select(fourthdriver.find_element_by_css_selector('#grd > div > div.pDiv > div.pDiv2 > div:nth-child(1) > select'))
        select.select_by_visible_text('100  ')
        time.sleep(4)

        pageNumber = int(fourthdriver.find_element_by_css_selector('#grd > div > div.pDiv > div.pDiv2 > div:nth-child(5) > span > span').text)
        result = 1

        fileNumbers = []
        dates = []
        applicants = []
        addresses = []

        while result <= pageNumber:
            html = fourthdriver.page_source
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

            fourthdriver.find_element_by_css_selector("#grd > div > div.pDiv > div.pDiv2 > div:nth-child(7) > div.pNext.pButton > span").click()
            time.sleep(2)
            result = result + 1

            pageNumber = int(fourthdriver.find_element_by_css_selector('#grd > div > div.pDiv > div.pDiv2 > div:nth-child(5) > span > span').text)
        
        tempdf['File Number'] = fileNumbers
        tempdf['Received Date'] = dates
        tempdf['Local Authority Name'] = 'Wexford Co. Co.'
        tempdf['Applicant Name'] = applicants
        tempdf['Development Address'] = addresses
        tempdf['Development Description'] = 'No Description'
        tempdf['URL'] = link
        tempdf['Search Term'] = keyword
        data_frame = pd.concat([data_frame,tempdf])

    fourthdriver.quit()
    data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'])
    data_frame['File Number'] = data_frame['File Number'].astype(str)
    wexford_df = data_frame
    wexford_df.to_csv ('Wexford Function.csv', index = False)
    endTime = time.time()
    timeDiff = endTime - startTime
    print(f'Completed Wexford in {timeDiff:.2f} seconds')
    # return wexford_df

try:
    wexford(keywords)
except:
    variables[ 'Error' ] = 'Error in Wexford Function'    

#----------------------South Dublin------------------------

def southDublin(keywords):
    startTime = time.time()
    #fifthdriver =  webdriver.Chrome(ChromeDriverManager().install())
    fifthdriver = webdriver.Chrome(options = options)
    yearAgo = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d/%m/%Y')

    data_frame = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term'])
    tempdf = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term'])  
    
    tempdf.to_csv ('South Dublin Function.csv', index = False)
    for keyword in keywords:
        link = 'http://www.sdublincoco.ie/Planning/Applications?p=1&prop='+keyword
        fifthdriver.get(link)

        html = fifthdriver.page_source
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
            tempdf = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL', 'Search Term'])
            html = fifthdriver.page_source
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
                fifthdriver.find_element_by_xpath('//*[@id="main"]/div[2]/div/div[1]/div/div/table/caption/ul/li[4]/a').click()
            except Exception:
                pass

            tempdf['File Number'] = fileNumbers
            tempdf['Received Date'] = dates
            tempdf['Local Authority Name'] = 'South Dublin Co. Co.'
            tempdf['Applicant Name'] = applicants
            tempdf['Development Address'] = addresses
            tempdf['Development Description'] = 'No Description'
            tempdf['URL'] = link
            tempdf['Search Term'] = keyword

            data_frame = pd.concat([data_frame,tempdf])

    fifthdriver.quit()
    data_frame['Received Date'] = pd.to_datetime(data_frame['Received Date'], format='%d/%m/%Y')
    data_frame = data_frame[(data_frame['Received Date'] >= yearAgo)]
    data_frame['URL'] = data_frame['URL'].str.replace(' ','%20')
    southDublin_df = data_frame
    southDublin_df.to_csv ('South Dublin Function.csv', index = False)
    endTime = time.time()
    timeDiff = endTime - startTime
    print(f'Completed South Dublin in {timeDiff:.2f} seconds')
    # return southDublin_df

try:
    southDublin(keywords)
except:
    variables[ 'Error' ] = 'Error in South Dublin Function'    

#--------------An Bord Pleanala - SID-----------------------

cards = ['1','2','3','4']

iterations = []
for item in cards:
    iterations.append(item)

def ABP(cards, iterations):
    startTime = time.time()
    #sixthdriver = webdriver.Chrome(ChromeDriverManager().install())
    sixthdriver = webdriver.Chrome(options = options)
    sid_df = pd.DataFrame(columns=['File Number', 'Due Date', 'Development Description', 'Received Date', 'Local Authority Name', 'URL', 'Search Term'])
    single_df = pd.DataFrame(columns=['File Number', 'Received Date', 'Local Authority Name', 'Applicant Name', 'Development Address', 'Development Description', 'URL', 'Search Term'])

    this_year = str(datetime.datetime.now().year)

    link = 'https://www.pleanala.ie/en-ie/lists/cases?list=I&year='+this_year
    # link = 'https://www.pleanala.ie/en-ie/lists/cases?list=I&year=2021'

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
                pass
        # print('Not Enough Results')
        # notEnoughResults_df = pd.DataFrame(columns=['File Number','Received Date','Local Authority Name', 'Deadline', 'Applicant Name','Development Address','Development Description', 'URL', 'Search Term'])
        # notEnoughResults_df.to_csv('ABP Function.csv', index = False)
        # endTime = time.time()
        # timeDiff = endTime - startTime
        # print(f'Completed An Bord Pleanala (ERROR: Not Enough Results) in {timeDiff:.2f} seconds')
        # return None
            
    for item in cards:
        sixthdriver.get(link)
        
        try:
            no_cookies = WebDriverWait(sixthdriver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="ccc-reject-settings"]/span'))
                            )
            no_cookies.click()
        except:
            pass
        
        card = sixthdriver.find_element_by_xpath('//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div['+item+']/a')
        sixthdriver.execute_script("arguments[0].click();", card)
       
        ##sixthdriver.find_element_by_xpath('//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div['+item+']/a').click()
        #card = WebDriverWait(sixthdriver, 10).until(
         #                   EC.element_to_be_clickable((By.XPATH, '//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div['+item+']/a'))
          #              )      
        
        #card.click()
        ##//*[@id="maincontent"]/div/div/div/div/div/div/div[2]/div/div[1]/a

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
            sid_df = pd.concat([sid_df,temp_df])
        
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
            #single_df = single_df.append(row_series, ignore_index=True)
            single_df = pd.concat([single_df,row_series])
            

    sixthdriver.quit()                
    sid_df['File Number'] = sid_df['File Number'].str.replace('Case reference:','')
    sid_df['URL'] = sid_df['URL'].str.replace('Case reference:','')
    sid_df['Received Date'] = sid_df['Received Date'].str.replace('Date lodged:','')
    sid_df['Received Date'] = sid_df['Received Date'].str[:10]
    sid_df['Development Description'] = sid_df['Development Description'].str.replace('Description:','')
    sid_df = sid_df[['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    sid_df = pd.concat([sid_df,single_df])
    sid_df['Received Date'] = pd.to_datetime(sid_df['Received Date'], format='%d/%m/%Y')
    sid_df['Deadline'] = sid_df['Received Date'] + pd.Timedelta(days=39)
    sid_df = sid_df[['File Number','Received Date','Local Authority Name', 'Deadline', 'Applicant Name','Development Address','Development Description', 'URL', 'Search Term']]
    sid_df.to_csv('ABP Function.csv', index = False)
    endTime = time.time()
    timeDiff = endTime - startTime
    print(f'Completed An Bord Pleanala in {timeDiff:.2f} seconds')
    #return sid_df

try:
    ABP(cards,iterations)
except:
    variables[ 'Error' ] = 'Error in ABP Function'

#--------------Department Consultations--------------------

yearAgoString = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d/%m/%Y')
yearAgo = time.strptime(yearAgoString, "%d/%m/%Y")

def deptCons():
    startTime = time.time()

    deptCons_df = pd.DataFrame(columns=['Received Date''Development Description'])

    #seventhdriver = webdriver.Chrome(ChromeDriverManager().install())
    seventhdriver = webdriver.Chrome(options = options)

    link = 'https://www.gov.ie/en/search/?type=consultations&organisation=department-of-the-environment-climate-and-communications'

    seventhdriver.get(link)

    pages = seventhdriver.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/div[2]/div/div/div[2]')
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

try:
    deptCons()
except:
    variables[ 'Error' ] = 'Error in Dept Consultations Function'

#----------------------Threads-----------------------------
#t1 = Thread(target=bulk,args=(keywords,standardLinks,))
#t2 = Thread(target=KildareScript,args=(keywords,0))
#t3A = Thread(target=dublincity,args=(keywords,))
#t3B = Thread(target=fingal,args=(keywords,))
#t3C = Thread(target=dunlaoghaire,args=(keywords,))
#t4 = Thread(target=wexford,args=(keywords,))
#t5 = Thread(target=southDublin,args=(keywords,))
#t6 = Thread(target=ABP,args=(cards,iterations,))
#t7 = Thread(target=deptCons)

#t3A.start()
#t3B.start()
#t3C.start()
#t1.start()
#t4.start()
#t6.start()
#t2.start()
#t5.start()
#t7.start()

#t7.join()
#t5.join()
#t2.join()
#t6.join()
#t4.join()
#t1.join()
#t3A.join()
#t3B.join()
#t3C.join()

#----------------------COMBO-------------------------------

bulk_df = pd.read_csv('Bulk Function.csv')
kildare_df = pd.read_csv('Kildare Function.csv')
dubCity_df = pd.read_csv('DublinCity Function.csv')
fingal_df = pd.read_csv('Fingal Function.csv')
dunlaoghaire_df = pd.read_csv('Dunlaoghaire Function.csv')
wexford_df = pd.read_csv('Wexford Function.csv')
southDublin_df = pd.read_csv('South Dublin Function.csv')
sid_df = pd.read_csv('ABP Function.csv')
deptCons_df = pd.read_csv('Dept Consultation.csv')

initial_frames = [bulk_df, kildare_df, dubCity_df, fingal_df, dunlaoghaire_df, wexford_df, southDublin_df]
general_deadline = pd.concat(initial_frames)
general_deadline['Received Date'] = pd.to_datetime(general_deadline['Received Date'])
general_deadline['Deadline'] = general_deadline['Received Date'] + pd.Timedelta(days=32)
frames = [general_deadline, sid_df, deptCons_df]

combo_df = pd.concat(frames)
combo_df = combo_df[['File Number', 'Received Date', 'Local Authority Name', 'Deadline', 'Applicant Name', 'Development Address', 'Development Description', 'URL', 'Search Term']]
combo_df["Comments"] = ""

# existing_df = pd.read_csv('Planning Applications.csv')
sheet_url = 'https://docs.google.com/spreadsheets/d/1ajEtdL9kquS-zB01gf1JR_L6gW0U7_yc8GzcAyLNZp8/export?format=csv&gid=0'

existing_df = pd.read_csv(sheet_url)

try:
    existing_df['Received Date'] = pd.to_datetime(existing_df['Received Date'], format = '%d/%m/%Y')
    existing_df['Deadline'] = pd.to_datetime(existing_df['Deadline'], format = '%d/%m/%Y')
except Exception:
    pass

new_df = pd.concat([combo_df, existing_df])
new_df['File Number'] = new_df['File Number'].astype(str)
new_df['Received Date'] = new_df['Received Date'].astype(str)
# new_df['Deadline'] = new_df['Deadline'].astype(str)

new_df['Received Date'] = pd.to_datetime(new_df['Received Date']).dt.date
new_df['Deadline'] = pd.to_datetime(new_df['Deadline']).dt.date

new_df = new_df.drop_duplicates(subset=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description'],keep= 'last')
new_df = new_df.sort_values(['Deadline', 'Local Authority Name'], ascending=[False, True])
new_df['Comments'] = new_df['Comments'].fillna('')
new_df['Show Public'] = new_df['Show Public'].fillna('-')
new_df['Tweet Sent?'] = new_df['Tweet Sent?'].fillna('-')

new_df['Deadline']=pd.to_datetime(new_df['Deadline'])
new_df['Received Date']=pd.to_datetime(new_df['Received Date'])
new_df['test'] = (pd.to_datetime('today').normalize() - pd.to_datetime(new_df['Deadline'])).dt.days

new_df.loc[(new_df['test'] > 50), 'Draft Tweet'] = 'No Tweet'

numberOfRows = len(new_df)-3

for row in range(0,numberOfRows):
    if new_df['test'].iloc[row] <= 50:
        new_df['Draft Tweet'].iloc[row] = str('=if(and(K'+str(row+2)+'="Yes",VALUE(today()-D'+str(row+2)+')<=3),"📢 New - Public Submissions Needed 📢 "&char(10)&J'+str(row+2)+'&" proposed for "&if(F'+str(row+2)+'="N/A for DECC","DECC",F'+str(row+2)+')&char(10)&"Deadline for submissions: "&text(D'+str(row+2)+',"DD mmm")&char(10)&if(F'+str(row+2)+'="N/A for DECC","",char(10)&"Ref No: "&A'+str(row+2)+')&char(10)&"Link: "&H'+str(row+2)+'&char(10)&"How to submit: https://notherenotanywhere.com/new-planning-applications/"&char(10)&char(10)&"#NHNAsubmission","No tweet")')

#new_df = new_df.drop('test', 1) 
new_df = new_df.drop(columns='test') 

new_df['Deadline']=new_df['Deadline'].dt.strftime('%d %b %Y')
new_df['Received Date']=new_df['Received Date'].dt.strftime('%d %b %Y')

new_df['Deadline'] = new_df['Deadline'].str.replace('Sep','Sept')
new_df['Received Date'] = new_df['Received Date'].str.replace('Sep','Sept')

new_df = new_df.reset_index(drop=True)
new_df.to_csv ('Planning Applications.csv', index = False)

# Upload to Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'submissions-scraper-creds.json', scope)
    
gc = gspread.authorize(credentials)

spreadsheet_key = '1ajEtdL9kquS-zB01gf1JR_L6gW0U7_yc8GzcAyLNZp8'
wks_name = 'Sheet1'
d2g.upload(new_df, spreadsheet_key, wks_name, credentials=credentials, row_names=False)

service = discovery.build('sheets', 'v4', credentials=credentials)
#Remove ticks from tweet
request_body = {
    "requests": [
        {
            "findReplace": {
                "find": "'=",
                "searchByRegex": True,
                "range": {
                    "sheetId": 0,
                    'startRowIndex': 0,
                    'startColumnIndex': 12,
                    'endColumnIndex': 13 

                },
                "replacement": "=",
                "matchEntireCell": False,
                "includeFormulas": True
            }
        }
    ]
}
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_key,
    body=request_body
).execute()

#Remove ticks from deadline date
request_body = {
    "requests": [
        {
            "findReplace": {
                "find": "'",
                "searchByRegex": True,
                "range": {
                    "sheetId": 0,
                    'startRowIndex': 0,
                    'startColumnIndex': 3,
                    'endColumnIndex': 4 

                },
                "replacement": "",
                "matchEntireCell": False,
                "includeFormulas": True
            }
        }
    ]
}
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_key,
    body=request_body
).execute()

# Filter
request_body = {
    'requests': [
        {
            'setBasicFilter': {
                'filter': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'startColumnIndex': 0 ,
                        'endColumnIndex': 13 
                    }
                }
            }
        }
    ]
}

service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_key,
    body=request_body
).execute()

files = ['Kildare Function.csv','South Dublin Function.csv','DublinCity Function.csv','Dunlaoghaire Function.csv','Fingal Function.csv','Bulk Function.csv','Wexford Function.csv','ABP Function.csv','Dept Consultation.csv']
for file in files:
    try:
        os.remove(file)
    except:
        pass

#------------------------------------------------------------------
finishTime = time.time()
timeDiff = finishTime - beginTime

finishTime = time.time()
totalTime = finishTime - beginTime

mins = str(round((totalTime%3600)//60))
seconds = str(round((totalTime%3600)%60))
timeMsg = "Completed Total in {} mins {} seconds\nNow check the red lines in the spreadsheet".format(mins, seconds)
print(timeMsg)
