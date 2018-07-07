# -*- coding: utf-8 -*-
"""
Created on Tue May 29 21:53:47 2018

@author: dell
"""
 
import os   
import time
from urllib.request import  urlopen  
from urllib  import request  
from bs4 import BeautifulSoup  
import pandas as pd
from selenium import webdriver 

os.chdir('D:/爬虫/蚂蜂窝')

## 获得地区url地址
def find_cat_url(url):  
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}      
    req=request.Request(url,headers=headers)  
    html=urlopen(req)  
    bsObj=BeautifulSoup(html.read(),"html.parser")
    bs = bsObj.find('div',attrs={'class':'hot-list clearfix'}).find_all('dt')
    cat_url = []
    cat_name = []
    for i in range(0,len(bs)):
        for j in range(0,len(bs[i].find_all('a'))):
            cat_url.append(bs[i].find_all('a')[j].attrs['href'])
            cat_name.append(bs[i].find_all('a')[j].text)
    cat_url = ['http://www.mafengwo.cn'+cat_url[i] for i in range(0,len(cat_url))]   
    return cat_url

## 获得城市url地址
def find_city_url(url_list):
    city_name_list = []
    city_url_list = []
    for i in range(0,len(url_list)):             
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = url_list[i].replace('travel-scenic-spot/mafengwo','mdd/citylist')
        driver.get(url)
        while True:
            try:
                time.sleep(2)
                bs = BeautifulSoup(driver.page_source,'html.parser')
                url_set = bs.find_all('a',attrs={'data-type':'目的地'})
                city_name_list = city_name_list +[url_set[i].text.replace('\n','').split()[0] for i in range(0,len(url_set))]
                city_url_list = city_url_list+[url_set[i].attrs['data-id'] for i in range(0,len(url_set))]                
                js="var q=document.documentElement.scrollTop=800"  
                driver.execute_script(js)
                time.sleep(2)
                driver.find_element_by_class_name('pg-next').click()
            except:
                break
        driver.close()
    return city_name_list,city_url_list

    


## 执行代码
url = 'http://www.mafengwo.cn/mdd/'
url_list = find_cat_url(url)
city_name_list,city_url_list=find_city_url(url_list)
city = pd.DataFrame({'city':city_name_list,'id':city_url_list})




