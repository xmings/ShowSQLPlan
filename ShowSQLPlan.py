import os, uuid, re
import cx_Oracle, time
from colorama import init

class ShowSQLPlan(object):
	def __init__(self, dbConnStr):
		self.db = cx_Oracle.connect(dbConnStr)
		self.cursor = self.db.cursor()
		self.internalSQL = None
		self.cursor.setoutputsize

	def remouldSQL(self, sqlStr):
		if sqlStr.find("/*+gather_plan_statistics*/") > 0:
			sqlStr = sqlStr.replace("/*+gather_plan_statistics*/", "")
			
		self.keyStr = " /*" + str(uuid.uuid1()) + "*/" + " /*+gather_plan_statistics*/ "
			
		sqlStr = 'Select' + self.keyStr + re.split('select', sqlStr.lstrip(' '), flags=re.I)[1]
		return sqlStr
		
		
	def showPlan(self, sqlStr, statisMode='normal'):
		sqlStr = self.remouldSQL(sqlStr)
		self.internalSQL = sqlStr
		
		result = self.cursor.execute(sqlStr)
		result.fetchall()
		
		#查找上面执行的SQL的SQL_Id和Child_Number
		sqlStr = "select sql_id,child_number from gv$sql "\
		    + "where sql_text like '%"+ self.keyStr +"%' and sql_text NOT LIKE '%gv$sql%' "\
		    + "order by last_load_time desc"
		result = self.cursor.execute(sqlStr)
		result = result.fetchone()
		
		
		#根据SQL_Id和Child_Number查找对应执行计划
		
		if statisMode == 'normal':
			option = 'ADVANCED ALLSTATS LAST PEEKED_BINDS'
		sqlStr = "select * from table(dbms_xplan.display_cursor('%s',%d,'%s'))" % (result[0], result[1], option)
		PPrint(sqlStr)
		result = self.cursor.execute(sqlStr)
		#打印执行计划
		for r in result.fetchall():
			PPrint(r[0])
			
		PPrint("\n\n执行计划输出完毕!!\n\n", "warning")
		
	def exit(self):	
		self.cursor.close()	
		self.db.close()
		
def PPrint(text, level='main'):
	if level == 'main':
		text = '\033[0;32;40m ' + text + ' \033[0;31;40m'
	elif level == 'warning':
		text = '\033[5;31;40m ' + text + ' \033[0;31;40m'
	else:
		text = '\033[1;31;40m ' + text + ' \033[0;31;40m'

	print(text)
	
def SQLConsole(dbConnStr=None):
	os.system('color 04')
	showPlan = None
	init()
	while True:
		if not dbConnStr:
			dbConnStr = input("请输入ORACLE连接串:")
		try:
			showPlan = ShowSQLPlan(dbConnStr)
			break
		except:
			PPrint("\n\n* 数据库连接失败,请重新输入ORACLE连接串.\n\n", 'warning')

	while True:
		sqlStr = input("请输入SQL:")
		if sqlStr.upper() == 'EXIT':
			break
		elif not sqlStr.upper().lstrip(' ').startswith('SELECT') and\
		     not sqlStr.upper().lstrip(' ').startswith('WITH'):
			PPrint("\n\n* 禁止任何非查询语句,请重新输入SQL\n\n", 'warning')
			continue

		try:
			showPlan.showPlan(sqlStr)
		except Exception as e:
			PPrint(e.args)
			PPrint("\n\n* 输入SQL异常,请重新输入SQL.\n\n", 'warning')
	showPlan.exit()
			
if __name__ == '__main__':
	SQLConsole()
	

			
		
		
	
				
			
			
			
		
		
		
