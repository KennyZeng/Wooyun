#-*- coding:utf-8 -*-
#Author @ kenny 2013.4.6
#簡易轉換字詞


#欲修改的單辭
PreConvertList = [u'註入',u'盲註',u'註射',u'賬號',u'賬戶',u'及時',u'後臺']
#修改後的單詞
FniConvertList = [u'注入',u'盲注',u'注射',u'帳號',u'帳戶',u'即時',u'後台']

def Convert(word):
  for i,x in enumerate(PreConvertList):
		word = word.replace(x,FniConvertList[i])#替換單詞
	return word
