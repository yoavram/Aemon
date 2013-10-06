import os
from flask import Flask, request, render_template, redirect, Response, url_for, session
from flask.ext.pymongo import PyMongo, ObjectId, InvalidId
import simplejson
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime, timedelta
import colorbrewer

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
ADMIN_PW = os.environ.get('ADMIN_PW', '$5$rounds=84608$P0jO/99FFwBqiE36$8s6D.dBAPt4iUcC0DBkKcDSpAxlZTMOhVsuQEhYYjF3')
GIFT = True
COLORS = colorbrewer.YlGnBu
def RGB2HEX(rgb):
	 return '#' + ''.join(['{0:02x}'.format(x) for x in rgb])
for k,v in COLORS.items():
	v = [RGB2HEX(x) for x in v]
	COLORS[k] = v

app = Flask(__name__)
app.config.from_object(__name__)  
app.secret_key = SECRET # TODO check if I can remove this


if app.debug:
	print " * Running in debug mode"
	from mockdb import groups, questions, answers, users
else:
	app.config['MONGO_DBNAME'] = db_name_from_uri(app.config['MONGO_URI'])
	mongo = PyMongo(app)
	if mongo:
		print " * Connection to database established"
		groups = mongo.db.groups
		questions = mongo.db.questions
		answers = mongo.db.answers
		users = mongo.db.users

app.permanent_session_lifetime = timedelta(days=3)
app.config['num_groups'] = groups.count()
app.config['num_questions'] = questions.count()
app.jinja_env.filters['format_date'] = string_from_datetime
app.jinja_env.filters['format_date_short'] = short_string_from_datetime

@app.route('/')
def root():
	# TODO Check session id
    return render_template("index.html")

@app.route('/start/<string:user_id>')
def start(user_id):
	session['user_id'] = user_id
	session['progress'] = 0
	return redirect(url_for("start_questionare"))

@app.route('/answer/<int:grp>/<int:que>/<int:ans>')
def answer(grp,que,ans):
	data = {"user_id":session["user_id"], "group":grp,"question":que,"answer":ans}
	success = answers.insert(data)
	session['progress'] += 1
	return jsonify(result=success)

@app.route('/questionare')
def start_questionare():	
	group_num = 1
	if 'group' in session:
		group = groups.find_one({'name':session['group']})
		if group:
			group_num = group['order']
	return redirect(url_for("cont_questionare", group_num=group_num))

@app.route('/questionare/<int:group_num>')
def cont_questionare(group_num):
	if 'user_id' not in session: # TODO does this work?
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
	data = request.form.copy()
	uid = users.insert(data)	
	return jsonify(result=uid)

@app.route('/email', methods=['POST'])
def email():
	u = users.find_one({'_id':ObjectId(session['user_id'])})
	if u:
		u['email'] = request.form['email']
		return jsonify(result=True,email=request.form['email'])
	else:
		return jsonify(result=False)

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
	if request.is_xhr or 'json' in request.args:
		return jsonify(result=groups.find())
	else:
		return render_template("groups.html")

@app.route('/admin/questions')
@app.route('/admin/questions/')
@app.route('/admin/questions/<string:group>')
def view_questions(group=''):
	if request.is_xhr or 'json' in request.args:
		if group:
			qs = questions.find({'group':group})	
		else:
			qs = questions.find()
		return jsonify(result=qs)
	else:
		return render_template("questions.html",group=group)

@app.route('/admin/users')
def view_users():
	if request.is_xhr:
		return abort(404)
	if 'json' in request.args:
		return jsonify(result=users.find())
	return render_template("users.html", users=users.find())

@app.route('/admin/answers')
def view_answers():
	if request.is_xhr:
		return abort(404)
	if 'json' in request.args:
		return jsonify(result=answers.find())
	return render_template("answers.html", answers=answers.find())


@app.route('/admin/question/save', methods=['POST'])
def save_question():
	if request.method == 'POST':
		_id = request.form.get('_id')		
		try:
			q = questions.find_one({'_id':ObjectId(_id)})
			for k in q.keys():
				if k in request.form:
					try:
						v = request.form[k]
						v = int(v)
					except ValueError:
						pass
					q[k] = v
			success = questions.update(q) #TODO check this returns bool
		except InvalidId: # New question
			q = {}
			for k,v in request.form.items():
					q[k] = v
			success = questions.insert(q) #TODO check this returns bool
		reorder_questions()
		return jsonify(result=success)

@app.route('/admin/group/save', methods=['POST'])
def save_group():
	if request.method == 'POST':
		_id = request.form.get('_id')		
		try:
			g = groups.find_one({'_id':ObjectId(_id)})
			for k in g.keys():
				if k in request.form:
					g[k] = request.form[k]
			success = groups.update(g) #TODO check this returns bool
		except InvalidId: # New question
			g = {}
			for k,v in request.form.items():
					g[k] = v
			success = groups.insert(g) #TODO check this returns bool
		reorder_groups()
		return jsonify(result=success)

		
@app.route('/admin/question/remove/<string:question_id>')
def remove_question(question_id):
	success = questions.remove({'_id':ObjectId(question_id)})
	reorder_questions()
	return jsonify(result=success)

@app.route('/admin/group/remove/<string:group_id>')
def remove_group(group_id):
	success = groups.remove({'_id':ObjectId(group_id)})
	reorder_groups()
	return jsonify(result=success)
	
def reorder_questions():
	for g in groups.find():
		cursor = questions.find({'group':g['name']})
		reorder_cursor(cursor,questions)

def reorder_groups():
	cursor = groups.find()
	reorder_cursor(cursor,groups)

def reorder_cursor(cursor, collection):
	cursor.sort('order') # TODO mockdb doesn't accept params to sort
	for i,x in enumerate(cursor):
		x['order'] = i + 1
		collection.update(x)


if __name__ == '__main__':	
	port = int(os.environ.get('PORT', 5005))
	app.run(host='0.0.0.0', port=port, debug=app.debug)	
	print "Finished"
