# -*- coding: utf-8 -*-
from datetime import datetime
from flask.ext.pymongo import ObjectId
DATE_FORMAT = "%d/%m/%Y"

def datetime_from_string(string):
	return datetime.strptime(string, DATE_FORMAT)

class MockList(list):
	def sort(self, key='_id', direction=1):
		return list.sort(self, key=lambda x: x[key], reverse=direction==2)
	

class MockDb:
	def __init__(self, data):
		self.data = MockList(data)
		
	def insert(self, post):
		_id = ObjectId()
		post['_id'] = _id
		self.data.append(post)
		return _id

	def update(self, post):
		_id = post['_id']
		if type(_id) == str:
			_id = ObjectId(_id)
		for p in self.data:
			if p['_id'] == _id:
				p.update(post)
				return True
		return False

	def find(self, spec=None, sort=None):
		if spec:
			cursor = MockList([])
			for d in self.data:
				match = True
				for k,v in spec.items():
					if d[k] != v:
						match = False
						break
				if match:
					cursor.append(d)
			return cursor
		else:
			return self.data


	def find_one(self, spec=None, sort=None):
		cursor = self.find(spec, sort)
		if len(cursor) > 0:
			return cursor[0]
		else:
			return None

	def rewind(self):
		return self


	def __iter__(self):
		return self.data.__iter__()


	def count(self):
		return len(self.data)


	def remove(self, spec):		
		for x in self.data:			
			if x['_id'] == spec['_id']:
				y = self.data.remove(x)
				return True
		return False

questions = MockDb([
			{'_id':ObjectId(), 'group':'Satisfaction', 'title':'Public health systems', 'order':1, 'levels':5, 'comments':['Very dissatisfied','','','','Very satisfied']},
			{'_id':ObjectId(), 'group':'Satisfaction', 'title':'Agencies of internal security', 'order':2, 'levels':5, 'comments':[]},
			{'_id':ObjectId(), 'group':'Satisfaction', 'title':'Social welfare systems', 'order':3, 'levels':5, 'comments':[]},
			{'_id':ObjectId(), 'group':'Trust', 'title':'Public health systems', 'order':1, 'levels':5, 'comments':[]},
			{'_id':ObjectId(), 'group':'Trust', 'title':'Agencies of internal security', 'order':2, 'levels':5, 'comments':[]},
			{'_id':ObjectId(), 'group':'Trust', 'title':'Social welfare systems', 'order':3, 'levels':5, 'comments':[]}
		])
groups = MockDb([
			{'_id':ObjectId(), 'name':'Satisfaction', 'title':'Below is a list of public institutions and organizations that deliver various services to the public. Please circle the number from 1 to 5 that best reflects your satisfaction with their services. If you are not familiar with some of the subjects below, please try to express a general impression that most closely reflects your opinion.', 'order':1},
			{'_id':ObjectId(), 'name':'Trust', 'title':'In the following section you will find a list of various agencies and organizations. Please circle the number from 1 to 5 that best reflects the trust you have in each of them.', 'order':2}
		])	
answers = MockDb([])
users = MockDb([])