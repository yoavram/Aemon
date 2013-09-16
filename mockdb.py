# -*- coding: utf-8 -*-
from datetime import datetime
from flask.ext.pymongo import ObjectId
DATE_FORMAT = "%d/%m/%Y"

def datetime_from_string(string):
	return datetime.strptime(string, DATE_FORMAT)

class MockDb:
	def __init__(self):
		self.data = [
			{'_id':ObjectId(),'name':u'uri', 'direction':'north', 'leaving':datetime_from_string('2/12/2012'), 'arriving':datetime_from_string('3/12/2012'), 'email':'uri@gmail.co', 'munged_email': 'uri [at] gmail [dot] co', 'source':'bariloche', 'destination':'al poson', 'secret':'secret1', 'comments':u"can't wait to get going, who's in?\nlet's get started"},
			{'_id':ObjectId(),'name':u'מיכל', 'direction':'south', 'leaving':datetime_from_string('12/12/2012'), 'arriving':datetime_from_string('17/12/2012'), 'email':'yoavram@gmail.com', 'munged_email': 'yoavram [at] gmail [dot] com', 'source':'al poson', 'destination':'bariloche', 'secret':'secret2', 'comments':u'dying to take a piss'},
			{'_id':ObjectId(),'name':u'uri', 'direction':'north', 'leaving':datetime_from_string('2/12/2012'), 'arriving':datetime_from_string('3/12/2012'), 'email':'uri@gmail.co', 'munged_email': 'uri [at] gmail [dot] co', 'source':'bariloche', 'destination':'al poson', 'secret':'secret1', 'comments':u"can't wait to get going, who's in?\nlet's get started"},
			{'_id':ObjectId(),'name':u'מיכל', 'direction':'south', 'leaving':datetime_from_string('12/12/2012'), 'arriving':datetime_from_string('17/12/2012'), 'email':'yoavram@gmail.com', 'munged_email': 'yoavram [at] gmail [dot] com', 'source':'al poson', 'destination':'bariloche', 'secret':'secret2', 'comments':u'dying to take a piss'},
			{'_id':ObjectId(),'name':u'uri', 'direction':'north', 'leaving':datetime_from_string('2/12/2012'), 'arriving':datetime_from_string('3/12/2012'), 'email':'uri@gmail.co', 'munged_email': 'uri [at] gmail [dot] co', 'source':'bariloche', 'destination':'al poson', 'secret':'secret1', 'comments':u"can't wait to get going, who's in?\nlet's get started"},
			{'_id':ObjectId(),'name':u'מיכל', 'direction':'south', 'leaving':datetime_from_string('12/12/2012'), 'arriving':datetime_from_string('17/12/2012'), 'email':'yoavram@gmail.com', 'munged_email': 'yoavram [at] gmail [dot] com', 'source':'al poson', 'destination':'bariloche', 'secret':'secret2', 'comments':u'dying to take a piss'},
			{'_id':ObjectId(),'name':u'uri', 'direction':'north', 'leaving':datetime_from_string('2/12/2012'), 'arriving':datetime_from_string('3/12/2012'), 'email':'uri@gmail.co', 'munged_email': 'uri [at] gmail [dot] co', 'source':'bariloche', 'destination':'al poson', 'secret':'secret1', 'comments':u"can't wait to get going, who's in?\nlet's get started"},
			{'_id':ObjectId(),'name':u'מיכל', 'direction':'south', 'leaving':datetime_from_string('12/12/2012'), 'arriving':datetime_from_string('17/12/2012'), 'email':'yoavram@gmail.com', 'munged_email': 'yoavram [at] gmail [dot] com', 'source':'al poson', 'destination':'bariloche', 'secret':'secret2', 'comments':u'dying to take a piss'},
			{'_id':ObjectId(),'name':u'uri', 'direction':'north', 'leaving':datetime_from_string('2/12/2012'), 'arriving':datetime_from_string('3/12/2012'), 'email':'uri@gmail.co', 'munged_email': 'uri [at] gmail [dot] co', 'source':'bariloche', 'destination':'al poson', 'secret':'secret1', 'comments':u"can't wait to get going, who's in?\nlet's get started"},
			{'_id':ObjectId(),'name':u'מיכל', 'direction':'south', 'leaving':datetime_from_string('12/12/2012'), 'arriving':datetime_from_string('17/12/2012'), 'email':'yoavram@gmail.com', 'munged_email': 'yoavram [at] gmail [dot] com', 'source':'al poson', 'destination':'bariloche', 'secret':'secret2', 'comments':u'dying to take a piss'},
			{'_id':ObjectId(),'name':u'uri', 'direction':'north', 'leaving':datetime_from_string('2/12/2012'), 'arriving':datetime_from_string('3/12/2012'), 'email':'uri@gmail.co', 'munged_email': 'uri [at] gmail [dot] co', 'source':'bariloche', 'destination':'al poson', 'secret':'secret1', 'comments':u"can't wait to get going, who's in?\nlet's get started"},
			{'_id':ObjectId(),'name':u'מיכל', 'direction':'south', 'leaving':datetime_from_string('12/12/2012'), 'arriving':datetime_from_string('17/12/2012'), 'email':'yoavram@gmail.com', 'munged_email': 'yoavram [at] gmail [dot] com', 'source':'al poson', 'destination':'bariloche', 'secret':'secret2', 'comments':u'dying to take a piss'}
		]


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
			return self


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
