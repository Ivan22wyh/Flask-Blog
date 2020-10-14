from flaskblog.resources_data.handle_lagou_data import mysql_lagou
from flaskblog.models import Account
from flask import Blueprint, render_template, jsonify, request

data = Blueprint('data', __name__)

@data.route("/lagou")
def lagou():
	result = mysql_lagou.count_result()
	return render_template('/resources/python_job_data.html', result=result)

@data.route('/get_echart_data')
def get_echart_data():
	info = {}
	info['echart_1'] = mysql_lagou.query_industryField_result()
	info['echart_2'] = mysql_lagou.query_salary_result()
	info['echart_31'] = mysql_lagou.query_financeStage_result()
	info['echart_32'] = mysql_lagou.query_companySize_result()
	info['echart_33'] = mysql_lagou.query_jobNature_result()
	info['echart_4'] = mysql_lagou.query_positionName_result()
	info['echart_5'] = mysql_lagou.query_workYear_result()
	info['echart_6'] = mysql_lagou.query_education_result()
	info['map'] = mysql_lagou.query_city_result()
	return jsonify(info)

@data.route('/article')
def article():
	account = Account.query.get(1)
	return render_template('/resources/article.html', title='article', account=account)

@data.route('/article/spider')
def spider():
	chp = request.args.get('chp', 1, type=int)
	return render_template('/resources/spider_{}.html'.format(str(chp)), title='spider tutorial')