#-*- coding:utf8 -*-
#Author:kenny @ 2013.4.4
#ChangeLog-2013.4.6
#1.新增精華欄位(使用特徵credit.png做特徵定位)
#2.新增詞語轉換 簡->繁 & 修正某些字詞
#ChangeLog-2013.4.5
#新增儲存到Database功能,並且存成繁體，還有個小Bug:作者欄位存進DB時會有多一空格
#未來DB要加上精華"欄位",方便搜尋精華文章(可抓<span class="stars5 starstop) 來判斷
#明天還要加上詞語轉換!  ->可用2個List(待轉換、轉換) 1個for迴圈 再配合str.replace實做
import requests,os,sys
from pyquery import PyQuery as pq
import DBControl
from jianfan import jtof #簡轉繁
from jianfan import ftoj #繁轉簡
import ConvertWords


DebugMode = True

Customheaders = {
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31',
              'Connection': 'keep-alive',
              'Referer': 'http://www.wooyun.org/',
              'Accept-Encoding': 'gzip,deflate,sdch',
              'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
              'Accept-Charset': 'Big5,utf-8;q=0.7,*;q=0.3'
              }

def DbgPrint(msg):
  if msg.find('[Info]'):
    print '%s' % msg
    return
  elif DebugMode:
    print '%s' % msg


def DownloadPic(Url,Path):
  res = requests.get(Url,headers = Customheaders)
  #抓取檔案名稱
  FileNameIndex =  Url.rfind('/') +1
  FileName = Url[FileNameIndex:]

  if res.status_code == 200:
      with open(Path + FileName, 'wb') as f:
          for chunk in res.iter_content(1024):
              f.write(chunk)
      DbgPrint('Done:%s' % Url)

#取得圖片連結
def GetPicLink(HtmlContent):
  PicList = []
  ParserTarget = pq(HtmlContent)
  Picurl = ParserTarget('a').map(lambda i, e: pq(e)('a').attr('href'))#把所有<a href>後面的內容全抓出來
  for u in Picurl:
    if u.find('/upload/20') != -1: #找圖片地址 圖片連接都是以/upload/20開頭，故當特徵
      PicList.append(u)
  return PicList


#取得要放進DB中的資訊
def GetDBInfo(HtmlContent,WooyunNumber):
  DBInfoList = []
  ParserTarget = pq(HtmlContent)
  Content = ParserTarget('h3').map(lambda i,e: pq(e).text()) #抓到所有H3內的標籤

  for i,x in enumerate(Content):
    NoSpacestr =  x.encode('utf8').replace('\n', '').replace('\t', '') #替換多餘空格
    TmpList = NoSpacestr.split('：')#陣列[1]即為所要的內容
    if i == 0:#特別為漏洞編號設的，因為從網頁內抓會少個0,直接用檔案名稱就OK
      DBInfoList.append(WooyunNumber)
      continue
    Big5Str = jtof(TmpList[1])#簡體轉繁體
    #詞語轉換!,否則注入->註入!!
    Big5Str = ConvertWords.Convert(Big5Str)
    #DbgPrint('Big5Str:%s' % Big5Str.encode('utf8') )
    DBInfoList.append(Big5Str) #存繁體!!
  
  #抓取是否為精華文章的判斷()
  
  

  return DBInfoList

#取得文章連結
def GetArticleLink(Url):
  ArticleList = []
  HotArticleFlagList = []
  ParserTarget = pq(url=Url)
  

  url = ParserTarget('a').map(lambda i, e: pq(e)('a').attr('href')) #把所有<a href>後面的內容全抓出來

  for u in url:
      if u.find('/bugs/wooyun-') == 0 and u.find('comment') == -1: #找文章連結
        #DbgPrint u
        StartIndex = ParserTarget.html().find(u)
        EndIndex = ParserTarget.html().rfind(u)
        #print 'StartIndex:%d  EndIndex:%d' % (StartIndex,EndIndex)
        HotFlagIndex = ParserTarget.html()[ StartIndex:EndIndex ].find('credit.png')#精華文章圖案(從文章連接中找)
        if HotFlagIndex != -1:
          #print 'HotArticle!!!!!!!!!!!!!!!!'
          HotArticleFlagList.append(True)#熱門文章標記List
        else:
          #print 'Not Hot Article'
          HotArticleFlagList.append(False)
        ArticleList.append(u)


  return ArticleList,HotArticleFlagList

#抓整個文章內容
def GetPageContent(Url,HotArticleFlag):
  res = requests.get(Url,headers = Customheaders)
  if res.status_code == 200:
    HtmlFileNameIndex = Url.rfind('/') + 1
    HtmlFileName = Url[HtmlFileNameIndex:]


    #另存文章
    HtmlContent = ""
    with open(HtmlFileName + '.html', 'wb') as f:
          for chunk in res.iter_content(1024):
              f.write(chunk)
              HtmlContent += chunk #網頁內容
    if len(HtmlContent) == 0:
      return False

    #解析文章內容，取得網頁資訊,並存進DB
    TmpList = GetDBInfo(HtmlContent,HtmlFileName)
    DBInfoList = []
    for i , x in enumerate(TmpList):  #enumerate函數可以同時取得計數i and x內容
      if(i+1) == 13:#總共12條紀錄
        break
      #uni = unicode(x,'utf8') #還要先強制轉換成Unicode 才可以放到DB中，否則會錯誤 ===>不需要了,因為簡轉繁模組就會轉成unicode
      x = x.lower() #全轉為小寫，這樣搜尋就不會有問題
      DBInfoList.append(x)#放到List中  
    #最後一欄位是標記是否為熱門文章
    DBInfoList.append(HotArticleFlag)


    InsertTupleData =  list(DBInfoList) #把List 轉換成 Tuple
    WooyunDB.InsertData(InsertTupleData) #插入資料庫中
    


    #解析圖片連結
    PicList = GetPicLink(HtmlContent)
    if PicList == []: #代表沒有圖片...就不繼續下載圖片了
      return True
    #為圖片開資料夾
    DirectoryIndex = PicList[0].rfind('/')
    DirectoryPath = PicList[0][0:DirectoryIndex]
    DbgPrint(DirectoryPath)
    if not os.path.exists(r'%s' % DirectoryPath):
      os.makedirs(DirectoryPath)
      DbgPrint('Create Dir OK!')
    else:
      DbgPrint('Dir exists!')
    #下載&儲存圖片
    for pic in PicList:
      PicUrl = 'http://wooyun.org' + pic
      DbgPrint(PicUrl)
      DownloadPic(PicUrl,DirectoryPath + '/')
    return True
  else:
    return False


def main():
  
  try:
    ArticleList,HotArticleFlagList = GetArticleLink('http://wooyun.org/bugs/new_public/page/490')
  except Exception as e:
    DbgPrint('[ConnectError]:%s \nEnd....!!' % e)
    sys.exit(0)

  for i,aiticle in enumerate(ArticleList):
    #檢查是否已經存於資料庫-若有的話則不繼續抓
    WooyunNumberIndex = aiticle.rfind('/') + 1
    WooyunNumber = aiticle[WooyunNumberIndex:]

    bRet = WooyunDB.CheckExists('vulnerable_number',WooyunNumber)#前面是欲查詢欄位名稱,後面是查詢數值
    if bRet:#資料庫已存在(若想重抓覆蓋資料的話，改這就行)
      DbgPrint('Get last Record!!')
      break
    else: #資料庫沒有，開始抓
      try:
        bRet = GetPageContent( ('http://wooyun.org' + aiticle) , HotArticleFlagList[i])
      except Exception as e:
        DbgPrint('[ConnectError]:%s \nEnd....!!' % e)
        sys.exit(0)
      if bRet:
        DbgPrint('[Info]SuccessDownload:%s' % WooyunNumber)

    


if __name__ == '__main__':
  #建立DB
  WooyunDB = DBControl.DBControler()
  WooyunDB.CreateTable()

  #test查詢
  #bRet = WooyunDB.CheckExists('author',' 路人甲')#大小寫有區別
  #if bRet:
  #  print '111111111111'
  main()
  #GetPageContent('http://wooyun.org/bugs/wooyun-2011-01338')
  #ArticleList,HotArticleFlagList = GetArticleLink('http://wooyun.org/bugs/new_public/page/4')

