from sqlalchemy import create_engine, Integer, Float, String, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import Counter
import time

#创建数据库连接
engine = create_engine("mysql+pymysql://root:jtwhgx22@192.168.1.103:3306/lagou?charset=utf8", pool_pre_ping=True)

#操作数据库
Session = sessionmaker(bind=engine)

#声明一个基类
Base = declarative_base()

class Lagoutables(Base):
	#表名称
	__tablename__ = 'lagou_data_python'

	#id 整数 主键 自增 
	id = Column(Integer, primary_key=True, autoincrement=True)
	#岗位ID 整数 不为空
	positionId = Column(Integer, nullable=True)
	#经度
	longitude = Column(Float, nullable=True)
	#纬度
	latitude = Column(Float, nullable=True)
	#职位名称
	positionName = Column(String(length=50), nullable=True)
	#工作年限
	workYear = Column(String(length=20), nullable=True)
	#学历
	education = Column(String(length=20), nullable=True)
	#岗位性质
	jobNature = Column(String(length=20), nullable=True)
	#公司类型
	financeStage = Column(String(length=30), nullable=True)
	#公司规模
	companySize = Column(String(length=30), nullable=True)
	#业务方向
	industryField = Column(String(length=30), nullable=True)
	#所在城市
	city = Column(String(length=10), nullable=True)
	#岗位标签
	positionAdvantage = Column(String(length=200), nullable=True)
	#公司简称
	companyShortName = Column(String(length=50), nullable=True)
	#公司全称
	companyFullName = Column(String(length=200), nullable=True)
	#公司所在区
	district = Column(String(length=20), nullable=True)
	#公司福利标签
	companyLabelList = Column(String(length=200), nullable=True)
	#工资
	salary = Column(String(length=20), nullable=True)
	#爬取日期
	crawl_date = Column(String(length=20), nullable=True)

if __name__ == '__main__':
	#创建表,必须确保mysql有远程连接的权限
	'''步骤：1.mysql -u root -p密码
	2.use mysql
	3.update user set host = '%'where user = 'root';
	4.FLUSH PRIVILEGES;'''
	Lagoutables.metadata.create_all(engine)

class HandleLagouData(object):

	def __init__(self):
		self.mysql_session = Session()
		self.date = time.strftime("%Y-%m-%d", time.localtime())

	def insert_item(self, item):
		date = time.strftime("%Y-%m-%d", time.localtime())
		#插入信息的方式是通过对创建MySQL数据库的类进行赋值
		data = Lagoutables(
			longitude = item['longitude'], 
			positionId = item['positionId'], 
			latitude = item['latitude'], 
			positionName = item['positionName'], 
			workYear = item['workYear'], 
			education = item['education'], 
			jobNature = item['jobNature'], 
			financeStage = item['financeStage'], 
			companySize = item['companySize'], 
			industryField = item['industryField'], 
			city = item['city'], 
			positionAdvantage = item['positionAdvantage'], 
			companyShortName = item['companyShortName'], 
			companyFullName = item['companyFullName'], 
			district = item['district'], 
			companyLabelList = ','.join(item['companyLabelList']), 
			salary = item['salary'], 
			crawl_date = date
			)

		#查询是否有岗位信息
		query_result = self.mysql_session.query(Lagoutables).filter(Lagoutables.crawl_date==date, 
																	Lagoutables.positionId==item['positionId']).first()
		if query_result:
			print('该岗位信息已存在{}:{}:{}'.format(item['positionId'], item['city'], item['positionName']))
		else:
			self.mysql_session.add(data)
			self.mysql_session.commit()
			print('新增岗位信息{}'.format(item['positionId']))

	def count_result(self):
		info = {}
		info['all_count'] = self.mysql_session.query(Lagoutables).count()
		info['today_count'] = self.mysql_session.query(Lagoutables).filter(Lagoutables.crawl_date==self.date).count()
		return info

	def query_industryField_result(self):
		info = {}
		result = self.mysql_session.query(Lagoutables.industryField).all()
		result_list = [x[0].split(',')[0] for x in result]
		result_list2 = [x.split('、')[0] for x in result_list]
		result_list3 = [x.split(' ')[0] for x in result_list2]
		result_list4 = [x for x in Counter(result_list3).most_common(7) if x[1]>140]
		data = [{"name": x[0], "value": x[1]} for x in result_list4]
		name_list = [name['name'] for name in data]
		info['x_name'] = name_list
		info['data'] = data
		return info


	def query_salary_result(self):
		info = {}
		data = {}
		result = self.mysql_session.query(Lagoutables.salary).all()
		result_list_min = [int(x[0].split('-')[0].replace('k', '').replace('K', '')) for x in result]
		result_list_max = [int(x[0].split('-')[1].replace('k', '').replace('K', '')) for x in result]
		result_list = []
		for i in range(len(result_list_min)):
			salary_mean = (result_list_max[i] + result_list_min[i])/2
			result_list.append(salary_mean) 
		result_list = sorted(result_list)
		salary_list = ['24k', '20k', '16k', '12k', '8k', '4k', '4k以下']
		info['x_name'] = salary_list
		salary_range = [0, 0, 0, 0, 0, 0, 0]
		for salary in result_list:
			if salary > 26:
				salary_range[0] += 1
			elif salary > 22:
				salary_range[1] += 1
			elif salary > 18:
				salary_range[2] += 1
			elif salary > 14:
				salary_range[3] += 1
			elif salary > 10:
				salary_range[4] += 1
			elif salary > 6:
				salary_range[5] += 1
			else:
				salary_range[6] += 1
		salary_data = [[], [], [], [], [], [], []]
		for i in range(len(salary_range)):
			salary_data[i].append(salary_list[i])
			salary_data[i].append(salary_range[i])
		data = [{"name": x[0], "value": x[1]} for x in salary_data]
		info['x_name'] = salary_list
		info['data'] = data
		print(salary_list)
		print(data)
		return info

	def query_education_result(self):
		info = {}
		result = self.mysql_session.query(Lagoutables.education).all()
		result_list = [x[0] for x in result]
		result_list2 = [x for x in Counter(result_list).items()]
		data = [{"name": x[0], "value": x[1]} for x in result_list2]
		name_list = [name["name"] for name in data]
		info['x_name'] = name_list
		info['data'] = data
		return info

	def query_city_result(self):
		info = {}
		result = self.mysql_session.query(Lagoutables.city).all()
		result_list = [x[0] for x in result]
		result_list2 = [x for x in Counter(result_list).most_common(100)]
		data = [{"name": x[0], "value": x[1]} for x in result_list2]
		name_list = [name["name"] for name in data]
		info['x_name'] = name_list
		info['data'] = data
		return info

	def query_workYear_result(self):
		info = {}
		data = []
		result = self.mysql_session.query(Lagoutables.workYear).all()
		result_list = [x[0] for x in result]
		result_list2 = [x for x in Counter(result_list).most_common(100)]
		name_list = ['应届毕业生', '1-3年', '3-5年', '5-10年', '10年以上']
		for name in name_list:
			for x in result_list2:
				if x[0] == name:
					data.append({"name": name, "value": x[1]})
		info['x_name'] = name_list
		info['data'] = data
		print(info)
		return info

	def query_financeStage_result(self):
		info = {}
		result = self.mysql_session.query(Lagoutables.financeStage).all()
		result_list = [x[0] for x in result]
		result_list2 = [x for x in Counter(result_list).most_common(100)]
		data = [{"name": x[0], "value": x[1]} for x in result_list2]
		name_list = [name["name"] for name in data]
		info['x_name'] = name_list
		info['data'] = data
		return info

	def query_companySize_result(self):
		info = {}
		result = self.mysql_session.query(Lagoutables.companySize).all()
		result_list = [x[0] for x in result]
		result_list2 = [x for x in Counter(result_list).most_common(100)]
		data = [{"name": x[0], "value": x[1]} for x in result_list2]
		name_list = [name["name"] for name in data]
		info['x_name'] = name_list
		info['data'] = data
		return info

	def query_jobNature_result(self):
		info = {}
		result = self.mysql_session.query(Lagoutables.jobNature).all()
		result_list = [x[0] for x in result]
		result_list2 = [x for x in Counter(result_list).most_common(100)]
		data = [{"name": x[0], "value": x[1]} for x in result_list2]
		name_list = [name["name"] for name in data]
		info['x_name'] = name_list
		info['data'] = data
		return info

	def query_positionName_result(self):
		info = {}
		result = self.mysql_session.query(Lagoutables.positionName).all()
		result_list = [x[0] for x in result]
		result_list2 = [x for x in Counter(result_list).most_common(10)]
		data = [{"name": x[0], "value": x[1]} for x in result_list2]
		name_list = [name["name"] for name in data]
		info['x_name'] = name_list
		info['data'] = data
		print(info)
		return info

mysql_lagou = HandleLagouData()










