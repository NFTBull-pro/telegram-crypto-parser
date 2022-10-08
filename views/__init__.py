from flask import render_template, request, redirect, url_for, session, jsonify
from app import app
from helpers.database import *
from model import *
from datetime import datetime
from bson import ObjectId

@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'POST':
		if checkloginpassword():	
			return logs_page()
		else:
			return render_template('index.html')
	else:
		if "username" not in session:
			return render_template('index.html')
		else:
			return logs_page()

@app.route('/checkloginusername', methods=["POST"])
def checkUserlogin():
	return checkloginusername()

@app.route('/register', methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	elif request.method == "POST":
		registerUser()
		return redirect(url_for("index"))

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))


@app.route('/logs',methods=['GET','POST'])
def logs_page():
	if "username" not in session:
		return render_template('index.html')

	admin_user = db.admin_users.find_one({"username":session['username']})
	if not admin_user['status']:
		return render_template("notaccess.html")

	logs = ''

	try:
		f = open("parser.log", "r")
		logs = f.read()
	except:
		pass
	
	return render_template('logs.html',logs=logs, today=datetime.now().strftime("%H:%M") )	

@app.route('/signals/<signal_id>',methods=['GET'])
def get_signal(signal_id):
	signal_id = ObjectId(signal_id)
	signal = db.signals.find_one({'_id': signal_id})

	if not signal:
		return jsonify({'status': 400})
	
	data = {'status': 200}
	if 'json' in signal:
		data['json'] = signal['json']
	else:
		if 'error' in signal:
			data['error'] = signal['error']

	data['text'] = signal['text'].replace('\n','</br>')
	return jsonify(data)

@app.route('/signals',methods=['GET','POST'])
def signals_page():
	if "username" not in session:
		return render_template('index.html')

	admin_user = db.admin_users.find_one({"username":session['username']})
	if not admin_user['status']:
		return render_template("notaccess.html")
	
	signals = list(db.signals.find())
	for signal in signals:
		signal['timestamp'] = signal['datetime'].timestamp()
		signal['datetime'] = signal['datetime'].strftime('%H:%M %d.%m.%Y')
		if 'json' in signal:
			signal['channel'] = get_channel_text(signal['json']['source'].split('channel-')[1])
			signal['symbol'] = signal['json']['symbol'] if 'symbol' in signal['json'] else '-'
		else:
			signal['channel'] = get_channel_text(signal['source'])
			signal['symbol'] = '-'

	return render_template('signals.html',signals=signals, channels=get_channel_list(), today=datetime.now().strftime("%H:%M"))