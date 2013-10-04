import os
from flask import Flask, request, render_template, redirect, Response, url_for, session
from flask.ext.pymongo import PyMongo, ObjectId, InvalidId
import simplejson
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime, timedelta
from uuid import uuid4 as uuid

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
SECRET = os.environ.get('SECRET', 'A0ZXHH!jmN]LWX/,?Rr98j/3yX R~T')
ADMIN_PW = os.environ.get('ADMIN_PW', '$5$rounds=87555$a5NNYH4VQvtM6XAX$lVAxzku5ovvu82HZA2nkBcdAfEGkRHzHDkuw2MXsvJ1')
COLORS = ['','#D7191C', '#FDAE61', '#FFFFBF', '#ABD9E9', '#2C7BB6'] # 1 count (not 0 count)

app = Flask(__name__)
app.config.from_object(__name__)  
app.secret_key = SECRET # TODO check if I can remove this


if app.debug:
	print " * Running in debug mode"
	from mockdb import groups, questions, answers
else:
	app.config['MONGO_DBNAME'] = db_name_from_uri(app.config['MONGO_URI'])
	mongo = PyMongo(app)
	if mongo:
		print " * Connection to database established"
		groups = mongo.db.groups
		questions = mongo.db.questions
		answers = mongo.db.answers

app.permanent_session_lifetime = timedelta(days=3)
app.config['num_groups'] = groups.count()
app.config['num_questions'] = questions.count()
app.jinja_env.filters['format_date'] = string_from_datetime
app.jinja_env.filters['format_date_short'] = short_string_from_datetime

@app.route('/')
def root():
	# TODO Check session id
    return render_template("index.html")

@app.route('/start/<string:session_id>')
def start(session_id):
	print "Starting questionare for session", session_id
	session['session_id'] = session_id
	session['progress'] = 0
	return redirect(url_for("start_questionare"))

@app.route('/answer/<int:que>/<int:ans>')
def answer(que,ans):
	data = {"session_id":session["session_id"], "question":que,"answer":ans}
	success = answers.insert(data)
	session['progress'] += 1
	return jsonify(result=success)

@app.route('/questionare')
def start_questionare():	
	if 'group' in session:
		group = groups.find_one({'name':session['group']})
		group_num = group['order']
	else:	
		group_num = 1
	return redirect(url_for("cont_questionare", group_num=group_num))

@app.route('/questionare/<int:group_num>')
def cont_questionare(group_num):
	if 'session_id' not in session:
		return redirect(url_for("root"))
	if group_num > groups.count():
		return redirect(url_for("finish"))
	group = groups.find_one({'order':group_num})
	qs = questions.find({'group':group['name']})
	return render_template("questionare.html", group=group, questions=qs)

@app.route('/finish')
def finish():
	return render_template("finish.html")

@app.route('/personal', methods=['POST'])
def personal():
    return str(uuid())

@app.route('/admin', methods=['GET','POST'])
def admin():
	# POST
	if request.method == 'POST':
		pw = request.form['password']		
		if not pwd_context.verify(pw, ADMIN_PW):
			return render_template("login.html", failed=True)
		session['admin'] = True	
	# GET 
	elif not session.get('admin', False): 
			return render_template("login.html", failed=False)		
	return redirect(url_for('view_groups'))

@app.route('/logout')
def logout():
	session['admin'] = False
	return redirect('/')

@app.route('/admin/groups')
def view_groups():
	if not session.get('admin', False):
		redirect('/admin')
	if request.is_xhr:
		return jsonify(result=groups.find())
	else:
		return render_template("groups.html")

@app.route('/admin/questions')
@app.route('/admin/questions/')
@app.route('/admin/questions/<string:group>')
def view_questions(group=''):
	if not session.get('admin', False):
		redirect('/admin')
	if request.is_xhr:
		if group:
			qs = questions.find({'group':group})	
		else:
			qs = questions.find()
		return jsonify(result=qs)
	else:
		return render_template("questions.html",group=group)

@app.route('/admin/answers')
def view_answers():
	if not session.get('admin', False):
		redirect('/admin')
	#if request.is_xhr:
	return jsonify(result=answers.find())

@app.route('/admin/question/save', methods=['POST'])
def save_question():
	if not session.get('admin', False):
		redirect('/admin')
	if request.method == 'POST':
		_id = request.form.get('_id')		
		try:
			q = questions.find_one({'_id':ObjectId(_id)})
			for k in q.keys():
				if k in request.form:
					q[k] = request.form[k]
			success = questions.update(q) #TODO check this returns bool
		except InvalidId: # New question
			q = {}
			for k,v in request.form.items():
					q[k] = v
			success = questions.insert(q) #TODO check this returns bool
		return jsonify(result=success)

@app.route('/admin/group/save', methods=['POST'])
def save_group():
	if not session.get('admin', False):
		redirect('/admin')
	if request.method == 'POST':
		_id = request.form.get('_id')		
		try:
			g = groups.find_one({'_id':ObjectId(_id)})
			for k in q.keys():
				if k in request.form:
					g[k] = request.form[k]
			success = groups.update(q) #TODO check this returns bool
		except InvalidId: # New question
			g = {}
			for k,v in request.form.items():
					g[k] = v
			success = groups.insert(g) #TODO check this returns bool
		return jsonify(result=success)

		
@app.route('/admin/question/remove/<string:question_id>')
def remove_question(question_id):
	if not session.get('admin', False):
		redirect('/admin')	
	success = questions.remove({'_id':ObjectId(question_id)})
	return jsonify(result=success)

@app.route('/admin/group/remove/<string:group_id>')
def remove_group(group_id):
	if not session.get('admin', False):
		redirect('/admin')	
	success = groups.remove({'_id':ObjectId(group_id)})
	return jsonify(result=success)
	


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5005))
	app.run(host='0.0.0.0', port=port, debug=app.debug)	
	print "Finished"
