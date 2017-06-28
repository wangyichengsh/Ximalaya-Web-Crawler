# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 22:32:06 2017

@author: ASUS
"""

from pyquery import PyQuery as pq
import sys, os
import json
import requests
from contextlib import closing

'''
下载进度
'''
class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (
            self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
            self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)
def download(n ='王奕晟'):
    ReportList = []
    c = pq(url='http://www.ximalaya.com/search/'+n+'/t2',headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
    DomTree = c('.report_listView a')
    for my_div in DomTree.items():
        if my_div.hasClass('soundReport_soundname'):
            URL = 'http://www.ximalaya.com' + my_div.attr('href')
            r = my_div.html()
            l = my_div.attr('href').split('/')[-1]
            ReportList.append({'url': URL, 'name': r,'id': l})

    downloadurl = []
        
    for report in ReportList:
        URL = 'http://www.ximalaya.com/tracks/'+report['id']+'.json'
        jsondata = pq(url=URL,headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}).html()
        objectid = json.loads(jsondata)["play_path_64"]
        downloadurl.append({'url':objectid,'name':report['name']})

    if not os.path.exists('./Video'):
        os.makedirs('./Video')
    for item in downloadurl:
        url = item['url']
        name = item['name']
        with closing(requests.get(url, stream=True)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            file_D='./Video/' + name + '.mp3'
            if(os.path.exists(file_D)  and os.path.getsize(file_D)==content_size):
                print('跳过'+name)
            else:
                progress = ProgressBar(name, total=content_size, unit="KB", chunk_size=chunk_size, run_status="正在下载",fin_status="下载完成")
                with open(file_D, "wb") as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        progress.refresh(count=len(data))

if __name__ == '__main__':
    download()
    
    