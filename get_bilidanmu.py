# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 10:58:54 2020

@author: KANITAN___
"""
import requests
import re
import datetime
import pandas as pd
import random
import time
import bilibili_detailpage as detail
import os

# 配置文件输出路径
out_dir=''
# in_file存放av号。内容以av开头，一行一个号，文件utf-8无BOM
in_file='av.txt'


def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates 

def get_time(pubdate):
    dt = datetime.datetime.fromtimestamp(pubdate)
    beginDate=dt.strftime('%Y-%m-%d')
    endDate=time.strftime("%Y-%m-%d", time.localtime())
    return dateRange(beginDate, endDate)


# 获取
def get_danmu(aid,out_dir):
    video_time=[]
    abstime=[]
    userid=[]
    comment_content=[]  
    #获取视频信息：cid，标题，上传时间
    av_detail=detail.get_bilibili_detail(aid)
    cid=av_detail['cid']
    title=av_detail['视频标题']
    uptime=av_detail['上传时间']
    #视频发布时间～当日
    search_time=get_time(uptime)

    headers = {
        'Host': 'api.bilibili.com', 
		'Connection': 'keep-alive', 
		'Content-Type': 'text/xml', 
		'Upgrade-Insecure-Requests': '1',   
		'User-Agent': '',   
		'Origin': 'https://www.bilibili.com',   
		'Accept-Encoding': 'gzip, deflate, br', 
		'Accept-Language': 'zh-CN,zh;q=0.9',
    #		'Cookie': 'finger=edc6ecda; LIVE_BUVID=AUTO1415378023816310; stardustvideo=1; CURRENT_FNVAL=8; buvid3=0D8F3D74-987D-442D-99CF-42BC9A967709149017infoc; rpdid=olwimklsiidoskmqwipww; fts=1537803390'
            }
    #cookie用火狐浏览器找，以字典形式写入
    cookie={           
           '_dfcaptcha':'2dd6f170a70dd9d39711013946907de0',
           'bili_jct':'0e4b9c410994c3b19c2b9ba4aa4b0412',
           'buvid3':'E63976A6-062A-4E5D-BB57-41DDD6CAD05933691infoc',
           'CURRENT_FNVAL':'16',
           'DedeUserID':'21270960',
           'DedeUserID__ckMd5':'e14dd5193388f5f7',
           'LIVE_BUVID':'AUTO6315421125315777; fts=1542112657',
           'rpdid':'|(m~m~JR|kR0J\'ullY|kJ~||',
           'SESSDATA':'87c740f4%2C1581992481%2C069dfb11',
           'sid':'9xhluqpa',
           'stardustvideo':'1',
            }   

    url='https://api.bilibili.com/x/v2/dm/history?type=1&oid=%s&date={}'%(cid)  

    for search_data in search_time:
        print('正在爬取{}的弹幕'.format(search_data))
        full_url=url.format(search_data)
        res=requests.get(full_url,headers=headers,timeout=10,cookies=cookie)
        res.encoding='utf-8'  
        data_number=re.findall('d p="(.*?)">',res.text,re.S)
        data_text=re.findall('">(.*?)</d>',res.text,re.S)

        comment_content.extend(data_text)
        for each_numbers in data_number:
            each_numbers=each_numbers.split(',')
            video_time.append(each_numbers[0])           
            abstime.append(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(int(each_numbers[4]))))      
            userid.append(each_numbers[6])
        time.sleep(random.random()*3)   

    print(len(comment_content))
    print('爬取完成')
    result={'用户id':userid,'评论时间':abstime,'视频位置(s)':video_time,'弹幕内容':comment_content} 

    filename=aid+'_'+title+'.csv'
    results=pd.DataFrame(result)
    final= results.drop_duplicates()
    final.info()
    final.to_csv(os.path.join(out_dir,filename),encoding='gbk')




if __name__=='__main__': 
    # aid='83906533'
    # get_danmu(aid,out_dir)
    with open(in_file,'r') as instream:
        aid_list=instream.readlines()
        for i in range(len(aid_list)):
            aid_list[i]=aid_list[i].strip()
        print(aid_list)
        for aid in aid_list:
            try:
                get_danmu(aid,out_dir)
            except Exception as e:
                print(e)

            