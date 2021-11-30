# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 15:27:17 2020

@author: knutankv
"""

from selenium import webdriver
import os
import glob
import zipfile
import time

def good_zip(zip_file):
    try:
      x = zipfile.ZipFile(zip_file)
      x.close()
      return 1
    except:
      return 0

#%% Initial definitions
web_page = "https://bird.unit.no/resources/3e040fe0-dd69-47ca-af8a-683282a2845f/content"
download_path = 'c:\\bird_temp'

logfile = 'c:\\bird_temp\\status.log'

max_simultaneous = 4
remove_first = 2
sleep_time_between_checks = 5   #when max number of downloads is reached
min_sleep_between_clicks = 0.5

#%% Setup
options = webdriver.ChromeOptions()
prefs = {}

if not os.path.isdir(download_path):
    os.makedirs(download_path)
    
if os.path.isdir(logfile):
    os.remove(logfile)
    
prefs["profile.default_content_settings.popups"] = 0
prefs["profile.content_settings.exceptions.automatic_downloads.*.setting"] = 1

prefs["download.default_directory"] = download_path
options.add_experimental_option("prefs", prefs)

#%% Open browser, go to bird place, navigate to "Innhold"
driver = webdriver.Chrome('C:/Users/knutankv/git-repos/open-bridge-data/chromedriver.exe', options=options)
driver.get(web_page)

driver.implicitly_wait(10)   #allow for 10 seconds loading time

# Go too "Innhold"
innhold_list = driver.find_elements_by_xpath("//*[contains(text(), 'Innhold')]")
innhold_list[0].click()
driver.implicitly_wait(10)   #allow for 10 seconds loading time

#%% 
list_links = driver.find_elements_by_xpath("//*[contains(text(), 'Last ned')]")
list_links = list_links[remove_first:]
all_good = []
all_bad = []

for list_link in list_links:
    downloading = glob.glob(download_path + '\\*.crdownload')
    
    while len(downloading) >= max_simultaneous: 
        print(f'{max_simultaneous} simultaneous downloads - waiting for {sleep_time_between_checks} seconds.')
        time.sleep(sleep_time_between_checks)
        downloading = glob.glob(download_path + '\\*.crdownload')
        
    ready = glob.glob(download_path + '\\*.zip')
    
    good = [file for file in ready if good_zip(file)]
    bad = [file for file in ready if not good_zip(file)]
    all_good += good
    all_bad += bad
    
    __ = [os.remove(file) for file in ready]   
    
    with open(logfile, 'a') as f:
        for file in good:
            f.write(os.path.split(file)[1] + ' is ok' + '\n')
        for file in bad:
            f.write(os.path.split(file)[1] + ' is corrupt' + '\n')  
    
    time.sleep(min_sleep_between_clicks)
    list_link.click()    