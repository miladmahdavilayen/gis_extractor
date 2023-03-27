from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from pathlib import Path
import random
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path # this will get you the path variable
from loguru import logger



path = Path.cwd()

def get_api_nums():
    gis_data = pd.read_csv(path /'gis_data.csv', header=0)
    api_numbers = []
    for api in gis_data["API NO."]:
        api = str(api)
        if len(api) < 8:
            api = "0" + api
        api_numbers.append(api)
    return api_numbers


def generate_driver():
    while True:
        service_object = Service(binary_path)
        driver = webdriver.Chrome(service=service_object)
        try:
            driver.get("https://gis.rrc.texas.gov/GISViewer/")
            time.sleep(1)
            return driver
        except:
            logger.warning("Website loader crashed.. Sleeping for 60 seconds and will try again..")
            driver.quit()
            time.sleep(60)
            continue
        

def start_driver(data):
    
    output = pd.DataFrame()
    for api in data:
        driver = generate_driver()
        logger.info(f'Retrieving Api number: {api} ...') 
        time.sleep(2)  # Let the user actually see something!
        username = driver.find_element(By.ID, 'searchField')
        username.clear()
        time.sleep(1)
        username.send_keys(api)
        time.sleep(1)
        username.send_keys(Keys.ENTER)
        time.sleep(1)

        driver.find_element(by='id', value='identifyButton').click()
        time.sleep(1)

        driver.find_element(by='id', value='dijit_rrcGisAnchorMenuItem_0').click()

        time.sleep(2)
       
        # ActionChains(driver).move_by_offset(715, 290).context_click().perform()
        ActionChains(driver).move_by_offset(719, 284).click().perform()
        # ActionChains(driver).move_by_offset(300, 150).context_click().perform()
        
        time.sleep(2)
     
        try:
            table = driver.find_element(by='id', value='printIdentifyWellDiv')
        except:
            logger.warning(f"Api {api} could not be found! Adding to the note file for further investigation!")
            open('note.txt', 'a').write(api+"\n")
            continue
       
        time.sleep(1)
        
        
        data = table.text
        
        with open("file.txt", 'a') as f:
            f.write(data + "\n")
            f.write("################# next #################")
            f.close()



        well_records = {'api':{}, 'lat NAD83':{}, 'long NAD83':{} }
        well_records['api'] = api
        with open('file.txt', 'r') as gis:
            for line in gis.readlines():
                if "GIS LAT (NAD83)" in line:
                    well_records['lat NAD83'] = line.split(" ")[3][:-1]
                if "GIS LONG (NAD83)" in line:
                    well_records['long NAD83'] = line.split(" ")[3][:-1]
            gis.close()


        
        
           
        with open('api_records.txt', 'a') as file:
            file.write(str(well_records)+"\n")
            file.close()
        
        
        df_dictionary = pd.DataFrame([well_records])
        output = pd.concat([output, df_dictionary], ignore_index=True)
        output.to_csv('records.csv', index=False)
       

        driver.quit()
        time.sleep(random.randint(3, 10))



if __name__ == "__main__":
    
    api_list = get_api_nums()
    start_driver(api_list)