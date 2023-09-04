#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import os, json, sys
import getopt

num=100
sync_num = 5
chunk_size = 1024*1024
headers = { \
"Accept": "*/*",\
"Accept-Encoding": "gzip, deflate, br",\
"Accept-Language": "en-US,en;q=0.9",\
"Connection": "keep-alive",\
"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",\
"Host": "www.ximalaya.com",\
"sec-ch-ua": '"Chromium";v="93", " Not;A Brand";v="99"',\
"sec-ch-ua-mobile": "?0",\
"sec-ch-ua-platform": "Linux",\
"Sec-Fetch-Dest": "empty",\
"Sec-Fetch-Mode": "cors",\
"Sec-Fetch-Site": "same-origin",\
"User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 UOS"}

def get_param(argv):
    try:
        opts, args = getopt.getopt(argv, "hn:p:", ["help", "name=", "path="])
    except Exception as e:
        print(e)
    path = './download'
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('main.py -n <search name> -p <download path>')
            print('or: test_arg.py --name=<search name> --path=<path>')
            sys.exit()
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-p", "--path"):
            path = arg
    return name, path

async def search_audio(text, page):
    params = {'kw':text, 'page':page, 'spellchecker':'true','condition':'relation','rows':20,'device':'iPhone','core':'track'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.ximalaya.com/revision/search/main', headers = headers ,params = params) as resp:
                response = await resp.text()
                response.replace('\\','\\\\')
                res = json.loads(response)
                return res['data']['track']['docs']
    except Exception as e:
        print(e)

async def find_src_url(info_list, src_list):
    url = "https://www.ximalaya.com/revision/play/v1/audio"
    params = {"id":"","ptype":1}
    for item in info_list:
        params["id"] = item["id"]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers = headers ,params = params) as resp:
                    response = await resp.text()
                    response.replace('\\','\\\\')
                    res = json.loads(response)
                    src_list.append({"title":item["title"],"src":res["data"]["src"]})
        except Exception as e:
            print(e)

async def download_file(audio, download_path):
    file_name = audio['title']+'.m4a'
    file_path = os.path.join(download_path, file_name)
    src = audio['src']
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Starting download {file_name} from {src}")
            async with session.get(src) as response:
                assert response.status == 200
                with open(file_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)                        
                print(f"Downloaded {file_name} from {src}")
    except Exception as e:
        print(e)

async def main(argv):
    text, download_path = get_param(argv)
    audio_info = []
    src_list = []
    back_task1 = set()
    back_task2 = set()
    pages = int(num/20)+1
    def tmp(t):
        if t.result():
            task = asyncio.create_task(find_src_url(t.result(), src_list))
            back_task2.add(task)
            audio_info.extend(t.result())
    for i in range(1, pages+1):
        task = asyncio.create_task(search_audio(text, i))
        back_task1.add(task)
        task.add_done_callback(tmp)
    for t in back_task1:
        await t
    for t in back_task2:
        await t    
    src_list = src_list[:num]
    if not os.path.exists(download_path):
        os.mkdirs(download_path)
    for i in range(0, len(src_list),sync_num):
        back_task3 = set()
        for audio in src_list[i:i+sync_num]:
            task = asyncio.create_task(download_file(audio, download_path))
            back_task3.add(task)
        for t in back_task3:
            await t

if __name__=="__main__":
    asyncio.run(main(sys.argv[1:]))
