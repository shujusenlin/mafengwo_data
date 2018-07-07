# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 16:46:19 2018

@author: dell
"""

import os  
from urllib.request import  urlopen  
from urllib  import request  
from bs4 import BeautifulSoup    
import pandas as pd
from pyecharts import Bar,Geo 

os.chdir('D:/爬虫/蚂蜂窝')

## 获得城市url内容
def get_static_url_content(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}      
    req=request.Request(url,headers=headers)  
    html=urlopen(req)  
    bsObj=BeautifulSoup(html.read(),"html.parser")
    return bsObj

## 获得城市信息
def get_city_info(city_name,city_code):
    this_city_base = get_city_base(city_name,city_code)
    this_city_jd = get_city_jd(city_name,city_code)
    this_city_jd['city_name'] = city_name
    this_city_jd['total_city_yj'] = this_city_base['total_city_yj']
    try:
        this_city_food = get_city_food(city_name,city_code)
        this_city_food['city_name'] = city_name
        this_city_food['total_city_yj'] = this_city_base['total_city_yj']
    except:
        this_city_food=pd.DataFrame()
    return this_city_base,this_city_food,this_city_jd



## 获得城市各类标签信息
def get_city_base(city_name,city_code):
    url = 'http://www.mafengwo.cn/xc/'+str(city_code)+'/'
    bsObj = get_static_url_content(url)
    node =  bsObj.find('div',{'class':'m-tags'}).find('div',{'class':'bd'}).find_all('a') 
    tag_node = bsObj.find('div',{'class':'m-tags'}).find('div',{'class':'bd'}).find_all('em') 
    tag_count = [int(k.text) for k in tag_node]
    par = [k.attrs['href'][1:3] for k in node]
    tag_all_count = sum([int(tag_count[i]) for i in range(0,len(tag_count))])
    tag_jd_count = sum([int(tag_count[i]) for i in range(0,len(tag_count)) if par[i]=='jd'])
    tag_cy_count = sum([int(tag_count[i]) for i in range(0,len(tag_count)) if par[i]=='cy'])
    tag_gw_yl_count = sum([int(tag_count[i]) for i in range(0,len(tag_count)) if par[i] in ['gw','yl']])
    url = 'http://www.mafengwo.cn/yj/'+str(city_code)+'/2-0-1.html '
    bsObj = get_static_url_content(url)  
    total_city_yj = int(bsObj.find('span',{'class':'count'}).find_all('span')[1].text)
    return {'city_name':city_name,'tag_all_count':tag_all_count,'tag_jd_count':tag_jd_count,
            'tag_cy_count':tag_cy_count,'tag_gw_yl_count':tag_gw_yl_count,
            'total_city_yj':total_city_yj}

## 获得城市食物信息
def get_city_food(city_name,city_code):
    url = 'http://www.mafengwo.cn/cy/'+str(city_code)+'/gonglve.html'
    bsObj = get_static_url_content(url)
    food=[k.text for k in bsObj.find('ol',{'class':'list-rank'}).find_all('h3')]
    food_count=[int(k.text) for k in bsObj.find('ol',{'class':'list-rank'}).find_all('span',{'class':'trend'})]
    return pd.DataFrame({'food':food[0:len(food_count)],'food_count':food_count})


## 获得城市景点信息
def get_city_jd(city_name,city_code):
    url = 'http://www.mafengwo.cn/jd/'+str(city_code)+'/gonglve.html'
    bsObj = get_static_url_content(url)
    node=bsObj.find('div',{'class':'row-top5'}).find_all('h3')
    jd = [k.text.split('\n')[2] for k in node]
    node=bsObj.find_all('span',{'class':'rev-total'})
    jd_count=[int(k.text.replace(' 条点评','')) for k in node]
    return pd.DataFrame({'jd':jd[0:len(jd_count)],'jd_count':jd_count})
    

## 执行函数    
city_list = pd.read_excel('城市编号.xlsx')
city_base = pd.DataFrame()
city_food = pd.DataFrame()
city_jd =  pd.DataFrame()

for i in range(0,city_list.shape[0]): 
    try:
        k = city_list.iloc[i]
        this_city_base,this_city_food,this_city_jd=get_city_info(k['city_name'],k['city_code'])
        city_base=city_base.append(this_city_base,ignore_index=True)
        city_food = pd.concat([city_food,this_city_food],axis=0)
        city_jd = pd.concat([city_jd,this_city_jd],axis=0)
        print('正确:'+k['city_name'])
        print(i)
    except:
        print('错误:'+k['city_name'])
        print(i)
        continue

## 绘制图片
city_base.sort_values('total_city_yj',ascending=False,inplace=True)
city_jd.sort_values('jd_count',ascending=False,inplace=True)
city_food.sort_values('food_count',ascending=False,inplace=True)
attr = city_base['city_name'][0:10]
v1 = city_base['total_city_yj'][0:10]
bar = Bar("游记总数量TOP10")
bar.add("游记总数", attr, v1, is_stack=True)
bar.render('游记总数量TOP10.html')
data=[(city_base['city_name'][i],city_base['total_city_yj'][i]) for i in range(0,
       city_base.shape[0])]
geo = Geo('全国城市旅游热力图', title_color="#fff",
          title_pos="center", width=1200,
          height=600, background_color='#404a59')
attr, value = geo.cast(data)
geo.add("", attr, value, visual_range=[0, 30000], visual_text_color="#fff",
        symbol_size=15, is_visualmap=True,is_roam=False)
geo.render('蚂蜂窝游记热力图.html')








