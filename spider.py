import requests
import re
import time
from datetime import datetime
import json
import citycache
import gzip
from pyquery import PyQuery as pq
class Spider():
  def __init__(self):

    self.cityCode=''
    self.lon=''
    self.lat=''
    self.proxys={
      "http": "60.211.166.42:63000",
      "http": "221.5.54.6:808",
      "http": "61.184.41.18:3128",
      "http": "49.71.90.230:8118",
      "http": "61.135.217.7:80",
      "http": "122.114.31.177:808",
      "http": "111.155.116.238:8123",
      "http": "221.222.30.253:8118",
      "http": "114.230.202.228:8118",
      "http": "112.227.76.29:8118",
      "http": "218.59.75.60:8118"
    }
    self.userAgent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    self.headers = {
      'user-agent': self.userAgent
    }
    pass
  def setPos(self,lat,lon):
    self.lat=lat
    self.lon=lon
  def setCityCode(self,code):
    self.cityCode=code
  def convertTime(self):
    curTime=datetime.strptime(time.asctime(time.localtime(time.time())), '%a %b %d %H:%M:%S %Y')
    strTime = curTime.strftime('%Y-%m-%d %H:%M:%S')

    timeArray = time.strptime(strTime, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))*1000
    return timeStamp
  def getNewsDataByCode(self):
    timestamp=self.convertTime()
    code=self.cityCode[0:5]
    newsStruct={
      'code':code
    }
    print('https://e.weather.com.cn/mpub/new_wap/%s.htm?_=%d'%(code,timestamp),5555555555555555555555)
    with requests.get('https://e.weather.com.cn/mpub/new_wap/%s.htm?_=%d'%(code,timestamp),headers=self.headers) as res:
      text=res.content.decode(encoding='utf-8',errors='ignore')
      reg=re.compile('.*?\"articles\"\:\[(.*?)\]}.*?',re.S)
      mstr=reg.findall(text)
      print(mstr)
      newsD=json.loads(mstr[0])
      newsStruct={**newsStruct,**newsD}
      with requests.get('https://e.weather.com.cn%s'%(newsStruct['urls']),headers=self.headers) as resa:
        textd=resa.content.decode(encoding='utf-8',errors='ignore')
        regd=re.compile('.*?\<div class=\"news-detail\"\>(.*?)\s*?</div>\s*<div class="sixd-box-ad">.*?',re.S)
        mstrd=regd.findall(textd)
        newsStruct['html']=mstrd[0]
        return newsStruct;
        print(newsStruct,88888888888888)
  def getChartData(self,wedatac):
    wedata=wedatac['od2']
    whdataD = {
      'data': [],
      'tem': [],
      'humidity': [],
      'rain': [],
      'windLevel': [],
      'windAngle': [],
      'windDirection': [],
    }
    for x in range(0,24):
      r = wedata[x]

      whdataD['data'].append(r['od21'])
      whdataD['tem'].append(r['od22'])
      whdataD['humidity'].append(r['od27'])
      whdataD['rain'].append(r['od26'])
      whdataD['windLevel'].append(r['od25'])
      whdataD['windAngle'].append(r['od23'])
      whdataD['windDirection'].append(r['od24'])
    # if(not citycache.checkCity(wedatac['od1'])):
    #   citycache.addCityCode(wedatac['od1'],wedatac)
    return whdataD
  def getLifeInfo(self):

    with requests.get('https://m.weather.com.cn/d/town/today?lat=%s&lon=%s&station=%s'%(self.lat,self.lon,self.cityCode)) as today:
      today=today.content.decode(encoding='utf-8',errors='ignore')
      reg=re.compile(r'.*?生活指数</h2>\s*?(.*?)\s*</article>.*?',re.S)
      reg1=re.compile(r'.*?id="day-tianqi">\s*(.*?)\s*</article>.*?',re.S)
      text1=reg1.findall(today)
      text=reg.findall(today)
      doc1=pq(text1[0])
      dls=doc1.find('dl')
      doc=pq(text[0])
      tds=doc.find('td')
      zhishus=[]
      jiagshui=[]
      for dl in dls.items():
        weainfo={}
        weainfo['img']=dl.find('img').attr('src')
        weainfo['name']=dl.find('p').text()
        weainfo['time']=dl.find('time').text()
        jiagshui.append(weainfo)
      for td in tds.items():
        shzl = {}
        reg1 = re.compile(r'.*?svnicon iconli (.*?)"/>.*?')
        print(td.html())
        cls = reg1.findall(td.html())
        shzl['iconcls'] = cls[0]
        shzl['title'] = td.find('p').text()
        shzl['name'] = td.find('span').text()
        zhishus.append(shzl)
      return {'zhishus':zhishus,'jiagshui':jiagshui}

  def getCityCodeByCity(self,cityarr,citylist):
    sstr=[x['ref'] for x in citylist]

    code=None
    cityarr=[x.replace('县','').replace('区','').replace('市','').replace('省','') for x in cityarr]
    if(len(citylist)==1):
      return citylist[0]
    elif(len(citylist)>1):
      for x in sstr:
        if(x.find(cityarr[0])!=-1 and (x.find(cityarr[1])!=-1 or x.find(cityarr[2])!=-1)):
          code=citylist[sstr.index(x)]
          break
    return code

  def getHtmlCodeByCity(self,city,cityarr):
    # if(citycache.checkCity(city)):
    #   weatherD=citycache.getCityCode(city)
    #   return self.getChartData(weatherD['data'])
    timestrap=self.convertTime()
    url = "http://toy1.weather.com.cn/search?cityname=%s&callback=success_jsonpCallback&_=%d" % (city, timestrap)
    print(url)

    with requests.get(url,headers=self.headers) as res:
      htmlstr=res.text
      reg=re.compile('.*?success_jsonpCallback.*?\((.*?)\).*?',re.S)
      mstr=reg.findall(htmlstr)
      citylist=json.loads(mstr[0])
      code=self.getCityCodeByCity(cityarr,citylist)
      citycode=code['ref'].split('~')[0]
      self.setCityCode(citycode)
      self.url='http://www.weather.com.cn/weather1d/%s.shtml'%(citycode)
      print(self.url,77777777777)
      with requests.get(self.url,headers=self.headers) as rests:
        hml=rests.content.decode('utf-8')
        reg1 = re.compile('.*?observe24h_data = (.*?);.*?', re.S)
        mstr1 = reg1.findall(hml)
        jsondata = json.loads(mstr1[0])
        return self.getChartData(jsondata['od'])

if(__name__=='__main__'):
  spider=Spider()
  spider.setPos(39.90469,116.40717)
  spider.setCityCode('101011600')
  text=spider.getNewsDataByCode()
