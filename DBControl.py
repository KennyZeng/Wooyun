#coding=utf-8
#Author:kenny @ 2013.4.5
import sqlite3,sys

tablename = 'Wooyun_table'
DBFilename = 'Wooyun.DB'

class DBControler(object):
  
	def __init__(self):
		
		self.conn = sqlite3.connect(DBFilename)
		self.cur = self.conn.cursor()
		

	#vulnerable_number可與*.html做連結
	def CreateTable(self):
		create_table_stmt = '''
		CREATE TABLE IF NOT EXISTS %s(
		vulnerable_number TEXT,
		vulnerable_title TEXT,
		company TEXT,
		author TEXT,
		submit_time TEXT,
		public_time TEXT,
		vulnerable_type TEXT,
		level TEXT,
		rank TEXT,
		status TEXT,
		reference TEXT,
		tags TEXT,
		HotFlag INTEGER
		);''' % tablename

		create_index = 'CREATE INDEX IF NOT EXISTS idx_id ON %s (vulnerable_number);' % tablename
		self.cur.execute(create_table_stmt)
		self.cur.execute(create_index)
		self.conn.commit()

		

	def InsertData(self,Data):
		sql = u'insert into %s values (?,?,?,?,?,?,?,?,?,?,?,?,?)' % tablename
		try:
			self.cur.execute(sql,Data)
			self.conn.commit()
		except Exception as e:
			print e


	#列出數值
	def QueryData(self):
		sql = 'select * from %s' % tablename 
		self.cur.execute(sql)
		print self.cur.fetchall()

	#檢查Wooyun漏洞編號是否已存在(已經抓過資料)
	def CheckExists(self,column,Vulnumber):
		try:
			sql = "select * from %s where %s = '%s'" % (tablename,column,Vulnumber)
			self.cur.execute(sql)
			checkFlag = self.cur.fetchone()
			if checkFlag is not None:
				return True
			else:
				return False
		except Exception as e:
			print e
			print 'Exit.....!'
			sys.exit(0)

def main():
	pass
	#WooyunDB = DBControler()
	#WooyunDB.CreateTable()
	#WooyunDB.InsertData( ('1','2','3','4','5','6','7','8','9','10','11','12','13') )
	#WooyunDB.QueryData()

if __name__ == '__main__':
	main()
