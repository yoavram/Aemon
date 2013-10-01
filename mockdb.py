# -*- coding: utf-8 -*-
from datetime import datetime
from flask.ext.pymongo import ObjectId
DATE_FORMAT = "%d/%m/%Y"

def datetime_from_string(string):
	return datetime.strptime(string, DATE_FORMAT)

class MockDb:
	def __init__(self, data):
		self.data = data

	def insert(self, post):
		_id = ObjectId()
		post['_id'] = _id
		self.data.append(post)
		return _id


	def find(self, spec=None, sort=None):
		if spec:
			data = []
			for d in self.data:
				match = True
				for k,v in spec.items():
					if d[k] != v:
						match = False
						break
				if match:
					data.append(d)
			return data
		else:
			return self.data


	def find_one(self, spec=None, sort=None):
		data = self.find(spec, sort)
		if len(data)>0:
			return data[0]
		else:
			return None


	def rewind(self):
		return self


	def __iter__(self):
		return self.data.__iter__()


	def count(self):
		return len(self.data)


	def remove(self, _id):
		for x in self.data:
			if x['_id'] == _id:
				return self.data.remove(x)

questions = MockDb([
			{'_id':ObjectId(), 'group':'Satisfaction', 'title':'Public health systems', 'order':1, 'comments':['Very dissatisfied','','','','Very satisfied']},
			{'_id':ObjectId(), 'group':'Satisfaction', 'title':'Agencies of internal security', 'order':2},
			{'_id':ObjectId(), 'group':'Satisfaction', 'title':'Social welfare systems', 'order':3},
			{'_id':ObjectId(), 'group':'Trust', 'title':'Public health systems', 'order':1},
			{'_id':ObjectId(), 'group':'Trust', 'title':'Agencies of internal security', 'order':2},
			{'_id':ObjectId(), 'group':'Trust', 'title':'Social welfare systems', 'order':3}
		])
groups = MockDb([
			{'_id':ObjectId(), 'name':'Satisfaction', 'title':'Below is a list of public institutions and organizations that deliver various services to the public. Please circle the number from 1 to 5 that best reflects your satisfaction with their services. If you are not familiar with some of the subjects below, please try to express a general impression that most closely reflects your opinion.', 'order':1},
			{'_id':ObjectId(), 'name':'Trust', 'title':'In the following section you will find a list of various agencies and organizations. Please circle the number from 1 to 5 that best reflects the trust you have in each of them.', 'order':2}
		])	