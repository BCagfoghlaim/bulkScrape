from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from bs4.builder import HTML_5
from pandas.io import html
from bs4 import BeautifulSoup
import pandas as pd

startTime = time.time()

data_frame = pd.DataFrame(columns=['File Number','Application Status','Decision Due Date','Decision Date','Decision Code',
'Received Date','Applicant Name','Development Address','Development Description','Local Authority Name', 'URL', 'Search Term'])

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)
keywords = ['data storage', 'data cent', 'datacent']

link = 'http://www.eplanning.ie/CarlowCC/SearchExact/Description'
test_Links = [
    'http://www.eplanning.ie/CarlowCC/SearchExact/Description',
    'http://www.eplanning.ie/CavanCC/SearchExact/Description',
    'http://www.eplanning.ie/LaoisCC/SearchExact/Description'
]
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

otherLinks = [
    'https://webapps.dublincity.ie/swiftlg/apas/run/wphappcriteria.display',
    'http://www.sdublincoco.ie/Planning/Applications',
    'https://planning.agileapplications.ie/fingal/search-applications/',
    'https://planning.agileapplications.ie/dunlaoghaire/search-applications/',
    'http://webgeo.kildarecoco.ie/planningenquiry',
    'https://dms.wexfordcoco.ie/advanced.php'
]

all_Links = [
    'http://www.eplanning.ie/CarlowCC/SearchExact/Description',
    'http://www.eplanning.ie/CavanCC/SearchExact/Description',
    'http://www.eplanning.ie/ClareCC/SearchExact/Description',
    'http://planning.corkcoco.ie/ePlan/SearchExact/Description',
    'http://planning.corkcity.ie/SearchExact/Description',
    'http://www.eplanning.ie/DonegalCC/SearchExact/Description',
    'https://webapps.dublincity.ie/swiftlg/apas/run/wphappcriteria.display',
    'http://www.sdublincoco.ie/Planning/Applications',
    'https://planning.agileapplications.ie/fingal/search-applications/',
    'https://planning.agileapplications.ie/dunlaoghaire/search-applications/',
    'https://geo.galwaycity.ie/ePlan5/SearchExact/Description',
    'http://www.eplanning.ie/GalwayCC/SearchExact/Description',
    'http://www.eplanning.ie/KerryCC/SearchExact/Description',
    'http://webgeo.kildarecoco.ie/planningenquiry',
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
    'https://dms.wexfordcoco.ie/advanced.php',
    'http://www.eplanning.ie/WicklowCC/SearchExact/Description'
]
for keyword in keywords:
    # for link in test_Links:
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
data_frame.loc[:,'Received Date'] = pd.to_datetime(data_frame.loc[:, 'Received Date'], format='%d/%m/%Y')
data_frame['File Number'] = data_frame['File Number'].astype(str)
clean_df = data_frame.drop_duplicates(subset=['File Number','Received Date','Local Authority Name','Applicant Name','Development Address','Development Description','URL'],keep= 'last')
bulk_df = clean_df.sort_values(['Received Date', 'Local Authority Name'], ascending=[False, True])
bulk_df.to_csv ('bulk.csv', index = False)
    
# finally:
driver.quit()

endTime = time.time()
timeDiff = endTime - startTime
print(f'Completed in {timeDiff:.2f} seconds (or {timeDiff/60:.2f} minutes)')
