from app import app
from flask import request, session

from helpers.database import *
from helpers.hashpass import *

from bson import json_util
import json

def checkloginpassword():
	username = request.form['username']
	check = db.admin_users.find_one({"username": username})
	password = request.form['password']
	hashpassword = getHashed(password)
	if hashpassword == check["password"]:
		session['username'] = username
		return True
	else:
		return False

def registerUser():
	fields = [k for k in request.form]                                      
	values = [request.form[k] for k in request.form]
	data = dict(zip(fields, values))
	user_data = json.loads(json_util.dumps(data))
	user_data["password"] = getHashed(user_data["password"])
	user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
	user_data['status'] = False
	db.admin_users.insert(user_data)

def checkloginusername():
	username = request.form["username"]
	check = db.admin_users.find_one({"username": username})
	if check is None:
		return "No User"
	else:
		return "User exists"

def get_channel_list():
	return list({
				1289429673 : 'Тестовый (Макса)',
				1413326076 : 'Imperial Trade Altcoins| Pirate`s',
				1345495618 : 'Vip Scalping Mega Crypto',
				1283542460 : 'VIP Channel Mega Crypto',
				1476143943 : 'Mr Mozart | Pirates',
				1407454871 : 'Crypto Cat',
				1285877251 : 'CryptoBull Pirates',
				1315722059 : 'Маржерубы  Крипты | Pirates',
				1271594974 : 'Artem_Trade',
				1330518620 : 'Лоран Смелых',
				1551513891 :' Герман на блокчейн'
			}.values())


def get_channel_text(channel_id):
	try:
		return {
			1289429673 : 'Тестовый (Макса)',
			1413326076 : 'Imperial Trade Altcoins| Pirate`s',
			1345495618 : 'Vip Scalping Mega Crypto',
			1283542460 : 'VIP Channel Mega Crypto',
			1476143943 : 'Mr Mozart | Pirates',
			1407454871 : 'Crypto Cat',
			1285877251 : 'CryptoBull Pirates',
			1315722059 : 'Маржерубы  Крипты | Pirates',
			1271594974 : 'Artem_Trade',
			1330518620 : 'Лоран Смелых',
			1551513891 :' Герман на блокчейн'
		}[int(channel_id)]
	except:
		return '-'