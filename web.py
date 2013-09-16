import os
from flask import Flask, request, render_template, redirect, Response, url_for
from flask.ext.pymongo import PyMongo, ObjectId
import simplejson

DATE_FORMAT = "%d/%m/%Y"
SHORT_DATE_FORMAT = "%d/%m/%y"

class MongoDocumentEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, ObjectId):
            return str(o)
        return simplejson.JSONEncoder(self, o)

def jsonify(*args, **kwargs):
    return Response(simplejson.dumps(dict(*args, **kwargs), cls=MongoDocumentEncoder), mimetype='application/json')


def db_name_from_uri(full_uri):
	ind = full_uri[::-1].find('/')
	return full_uri[-ind:]


def datetime_from_string(string):
	return datetime.strptime(string, DATE_FORMAT)


def string_from_datetime(datetime_obj):
	return datetime_obj.strftime(DATE_FORMAT)


def short_string_from_datetime(datetime_obj):
	return datetime_obj.strftime(SHORT_DATE_FORMAT)

# add environment variables using 'heroku config:add VARIABLE_NAME=variable_name'
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
MONGO_URI = os.environ.get('MONGOLAB_URI')
GOOGLE_ANALYTICS = os.environ.get('GOOGLE_ANALYTICS', '')

app = Flask(__name__)
app.config.from_object(__name__)  

if app.debug:
	print " * Running in debug mode"
	import mockdb
	groups = mockdb.groups
	questions = mockdb.questions
else:
	app.config['MONGO_DBNAME'] = db_name_from_uri(app.config['MONGO_URI'])
	mongo = PyMongo(app)
	if mongo:
		print " * Connection to database established"
		groups = mongo.db.groups
		questions = mongo.db.questions

app.jinja_env.filters['format_date'] = string_from_datetime
app.jinja_env.filters['format_date_short'] = short_string_from_datetime


@app.route('/')
def root():
    return render_template("index.html")

@app.route('/start/<string:session>')
def start(session):
	print "Starting questionare for session", session
	grps = 

@app.route('/personal')
def personal():
    return render_template("personal.html")

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=app.debug)	
	print "Finished"
