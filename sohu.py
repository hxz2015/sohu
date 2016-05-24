#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 14:51:36 2016
题目：
     请设计一个系统，自动完成对于手机搜狐(http://m.sohu.com/)系统可靠性的检测。具体要求：
    1. 递归检测所有m.sohu.com域名的页面以及这些页面上的链接的可达性，即有没有出现不可访问情况。
    2. m.sohu.com域名页面很多，从各个方面考虑性能优化。
    3. 对于错误的链接记录到日志中，日志包括：URL，时间，错误状态等。
    要求：不使用框架。 加分项：使用并发方式实现。
@author: 张海旭
Email: 1101549736@qq.com
"""

import time
import urllib2
import urlparse
from bs4 import BeautifulSoup
import socket
import codecs
import Queue
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf-8') # 解决编码问题

'''
<a  href="/?_once_=000107_finbottomback&amp;_smuid=FMC5F0Ka0IQrRI5LKTOEyX&amp;v=2" class="Top">回到搜狐首页</a>
<a  href="#top" class="Top">↑回顶部</a>
<a  href="?v=1&amp;_once_=sohu_version_1&amp;_smuid=FMC5F0Ka0IQrRI5LKTOEyX">普版</a>
<a  href="?v=3&amp;_once_=sohu_version_3&amp;_smuid=FMC5F0Ka0IQrRI5LKTOEyX">触版</a>
<a  href="/towww?_smuid=FMC5F0Ka0IQrRI5LKTOEyX&amp;v=2">PC</a>
'''
#不检测的链接
filterurl = ["#top", "/?_once_=000107_finbottomback&amp;_smuid=FMC5F0Ka0IQrRI5LKTOEyX&amp;v=2", "?v=1&amp;_once_=sohu_version_1&amp;_smuid=FMC5F0Ka0IQrRI5LKTOEyX", 
             "?v=3&amp;_once_=sohu_version_3&amp;_smuid=FMC5F0Ka0IQrRI5LKTOEyX", "/towww?_smuid=FMC5F0Ka0IQrRI5LKTOEyX&amp;v=2", "javascript"]  
  
# 开始域名
root_url = 'http://m.sohu.com'
new_urls = set()   # 新的 还没测试
old_urls = set()   # 旧的 已测试过  

new_urls.add(root_url)


class ThreadUrl(threading.Thread):
    def __init__(self, new_urls):
        threading.Thread.__init__(self)
        self.new_urls = new_urls
          
    def run(self):
        while(len(self.new_urls)>0):
                print '\n' + '-' * 50 + '\n'
                c=len(new_urls)
                d=len(old_urls)
                print u'待检测的链接数为: %d' % c
                print u'已检测的链接数为: %d' % d
                if c != 0:
                    new_url = new_urls.pop()
                    old_urls.add(new_url) 
                    content = get_html(new_url)
                    if content == 0:   # 读取网页html失败 
                        print u'%s 链接访问失败,将信息吸入日志 ' % new_url
                       # continue   #重新开始
                    else:
                        urls = get_links(content)  # 获取页面上的属于sohu的链接
                        for url in urls :
                            new_urls.add(url)          
                else:
                    print u'完成检测'            
            
# 将错误的链接记录到日志中    
def write_log(url, t, s):
    f1=codecs.open('log.txt','a+','utf-8')
    message = '\r\n错误链接：%s \r\n错误时间：%s \r\n错误状态: %s \r\n' % (url, t, s)
    f1.write(message)
    f1.close()
    print u'完成错误信息写入日志'
  
#获得html
def get_html(url):
    #try-except进行异常监控
    try:
        print u'正在检测链接：  %s' %  url
        #写headers
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        request = urllib2.Request(url, headers = headers) 
        response = urllib2.urlopen(request,timeout=10)
        code = response.getcode()
        # geturl() 这个返回获取的真实的URL
        tiaozhuan = response.geturl()  
        if tiaozhuan.find('m.sohu.com') == -1: #不是手机搜狐域名 
            return 0
        #if code in [200,302]:
        content = response.read().decode('utf-8')
        response.close()
        return content
           
    except socket.timeout as e:
        write_log(url, time.ctime(), str(e))
        return 0 
    
    except Exception, e:
        write_log(url, time.ctime(), str(e))
        return 0    
    
#抓取页面上的所有链接链接    
def get_links(cont):
    urls = set()       
    soup = BeautifulSoup(cont,"lxml")
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        #print u'得到新的链接： %s'% href
        new_full_url = urlparse.urljoin(root_url, href)
        #print new_full_url
        # 检测是否为空 或 已经检测过
        if href is not None and new_full_url not in old_urls:
            flag=0
            for item in filterurl:
                if href.find(item) != -1:
                    flag=1    
            if flag != 1:                
                print u'得到新的链接： %s'% new_full_url
                urls.add(new_full_url)   
        else:
            continue 
    return urls

#
def main():
    threads=[]     

    for i in range(10):
        th = ThreadUrl(new_urls)
        th.setDaemon(False)
        threads.append(th)
        th.start()
          
    for j in threads:
        j.join()

if __name__ == '__main__':
    start = time.time()         
    main()
    print u'总用时为: %s' % (time.time() - start)