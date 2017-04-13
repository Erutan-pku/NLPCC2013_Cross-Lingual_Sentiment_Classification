#coding=utf-8
#-*- coding: UTF-8 -*- 
import sys
import requests
import re
from bs4 import BeautifulSoup
  
# 参考：http://www.cnblogs.com/wnzhong/p/6666911.html

def tidySentence(inputs) :
    inputs = re.sub(u'&quot;', '"', inputs)
    inputs = re.sub(u'&lt;', '<', inputs)
    inputs = re.sub(u'&gt;', '>', inputs)
    inputs = re.sub(ur'&.*?( |;)', ' ', inputs)
    return inputs

def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except:
        print("Get HTML Text Failed!")
        return 0
  
def google_translate_EtoC(to_translate, from_language="en", to_language="ch-CN"):
    #根据参数生产提交的网址
    base_url = u"https://translate.google.cn/m?hl={}&sl={}&ie=UTF-8&q={}"
    url = base_url.format(to_language, from_language, tidySentence(to_translate))
      
    #获取网页
    html = getHTMLText(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
      
    #解析网页得到翻译结果   
    try:
        result = soup.find_all("div", {"class":"t0"})[0].text
    except:
        try :
            print len(to_translate), unicode(to_translate)
        except :
            print len(to_translate), 'Not_a_str'
        print("Translation Failed!")
        result = to_translate
          
    return result
 
def google_translate_CtoE(to_translate, from_language="ch-CN", to_language="en"):
    #根据参数生产提交的网址
    base_url = u"https://translate.google.cn/m?hl={}&sl={}&ie=UTF-8&q={}"
    url = base_url.format(to_language, from_language, tidySentence(to_translate))
      
    #获取网页
    html = getHTMLText(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
      
    #解析网页得到翻译结果   
    try:
        result = soup.find_all("div", {"class":"t0"})[0].text
    except:
        try :
            print len(to_translate), unicode(to_translate)
        except :
            print len(to_translate), 'Not_a_str'
        print("Translation Failed!")
        result = to_translate
          
    return result
 
if __name__ == '__main__':
    print google_translate_EtoC(u'Chinese to Englisth is 1, English to Chinese is 2:    ')
    print google_translate_CtoE(u'我在天安门广场吃着炸鸡。')