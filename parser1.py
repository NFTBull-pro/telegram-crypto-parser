# -*- coding: utf-8 -*-
from re import sub, findall, split as re_split
from requests import post
from codecs import getencoder
import cv2
from numpy import array as numpy_array, ones as numpy_ones, asarray as numpy_asarray, uint8 

# Библиотеки для считывания
from easyocr import Reader
from pytesseract import image_to_string as tesseract_read

from telegram import Bot
bot = Bot('1217886482:AAFVNmInNPsg7_6IbsAT-4fNbeTAUHfdKWk')


def parse_img(image_stream):

	file_bytes = numpy_asarray(bytearray(image_stream.read()), dtype=uint8)
	image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

	scale_percent = 325

	width = int(image.shape[1] * scale_percent / 100)
	height = int(image.shape[0] * scale_percent / 100)
	dim = (width, height)

	image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	bot.send_message(chat_id=781804238, text='parse_img - увеличили изображение и подготовили')

	reader = Reader(['en'], gpu=False)
	results = {}

	# Фиолетовый
	lower_magenta = numpy_array([140, 190, 190])
	upper_magenta = numpy_array([160, 255, 255])

	magenta_mask = cv2.inRange(hsv, lower_magenta, upper_magenta)
	magenta_mask = cv2.dilate(magenta_mask, None, iterations=9)

	magenta_image = cv2.bitwise_and(image, image, mask = magenta_mask)
	magenta_image = cv2.bitwise_not(magenta_image)

	# easyocr
	results['open1'] = reader.readtext(magenta_image, allowlist ='.0123456789', detail=0, low_text=0.4,text_threshold=0.88, batch_size=5)
	
	if not results['open1']:
		bot.send_message(chat_id=781804238, text='parse_img - не смогли спарсить фиолетовый')
		
	if results['open1']:
		if '.' not in results['open1'][0]:
			results['open1'][0] = results['open1'][0][:1]+'.'+results['open1'][0][1:]
		
		results['open1'] = findall(r"\d+\.\d+", results['open1'][0])

		bot.send_message(chat_id=781804238, text='parse_img - спарсили мадженту')
	else:
		results.pop('open1')

	# Синий

	lower_blue = numpy_array([100, 7, 220])
	upper_blue = numpy_array([120, 255, 255])

	# easyocr
	def get_open(results, _iterations):
		blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
		blue_mask = cv2.dilate(blue_mask, None, iterations=_iterations)
		
		blue_image = cv2.bitwise_and(image, image, mask = blue_mask)
		blue_image = cv2.bitwise_not(blue_image)

		results['open'] = reader.readtext(blue_image, allowlist ='.0123456789', detail=0, low_text=0.4,text_threshold=0.82, batch_size=5)
		if not results['open']:
			bot.send_message(chat_id=781804238, text='parse_img - не смогли спарсить синий')
			return None
		
		for i in range(len(results['open'])):
			if results['open'][i][-1] == '.':
				results['open'][i] = results['open'][i][:-1]
			if '.' not in results['open'][i]:
				results['open'][i] = results['open'][i][:1]+'.'+results['open'][i][1:]
				results['open'][i] = findall(r"\d+\.\d+", results['open'][i])[0]
	
	try:
		_iterations = 8
		get_open(results, _iterations)
		while True:
			temp = results['open']
			temp = [float(item) for item in temp if item]
			temp = [item for item in temp if item]
			temp = sorted(temp)
			dif = temp[-1] - temp[0]
			if dif > (temp[0]*3):
				_iterations += 1
				if _iterations > 11:
					raise  
				get_open(results, _iterations)
			else:
				break
	except Exception as e:
		bot.send_message(chat_id=781804238, text='parse_img - ошибка при парсинге синего:'+str(e))
		return None

	bot.send_message(chat_id=781804238, text='parse_img - спарсили синий')
	# Зеленый

	lower_green = numpy_array([40, 170, 170]) 
	upper_green = numpy_array([70, 255, 255]) 

	green_mask = cv2.inRange(hsv, lower_green, upper_green)
	green_mask = cv2.dilate(green_mask, None, iterations=9)
	green_image = cv2.bitwise_and(image, image, mask = green_mask)

	# easyocr green text
	results['target'] = reader.readtext(green_image, allowlist ='0123456789.', detail=0, low_text=0.4,text_threshold=0.88, batch_size=5)
	if not results['target']:
		bot.send_message(chat_id=781804238, text='parse_img - не смогли спарсить зеленый')
		return None

	for i in range(len(results['target'])):
		results['target'][i] = findall(r"\d+\.\d+", results['target'][i])[0]

	if not results['target']:
		return None
	
	bot.send_message(chat_id=781804238, text='parse_img - спарсили зеленый')

	# Красный
	lower_red = numpy_array([0,150,100])
	upper_red = numpy_array([10,255,255])

	red_mask = cv2.inRange(hsv, lower_red, upper_red)


	red_mask = cv2.dilate(red_mask, None, iterations=9)
	red_image = cv2.bitwise_and(image, image, mask = red_mask)
	red_image = cv2.bitwise_not(red_image)

	# easyocr red_text
	results['stop'] = reader.readtext(red_image, allowlist ='.0123456789', detail=0, low_text=0.3,text_threshold=0.90, batch_size=5)
	if not results['stop']:
		bot.send_message(chat_id=781804238, text='parse_img - не смогли спарсить красный')
		return  None

	if '.' not in results['stop'][0]:
		results['stop'][0] = results['stop'][0][:1]+'.'+results['stop'][0][1:]
	results['stop'][0] = findall(r"\d+\.\d+", results['stop'][0])[0]

	bot.send_message(chat_id=781804238, text='parse_img - спарсили красный')

	return results

blocked = ['Huobi', 'Kucoin']

def cutter(data, arr):
	for item in arr:
		data = data.replace(item, '')
	return data

# Imperial Trade Altcoins | Pirate's
def channel_1(text, channel_id, customId, logger, pred_message_list):
	if (text.find('Вход') != -1 or text.find('вход') != -1) and (text.find('Стоп') != -1 or text.find('Cтоп') != -1 or text.find('стоп') != -1) and text.find('Цели') != -1: 
		bot.send_message(chat_id=781804238, text='channel_1 спарсил данные, начинаем обрабатывать')
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		array_1 = []

		# Парсим текст получаем все прогнозы
		while True:
			try:
				index_1 = text.index('Цели')
				index_2 = text.find('\n\n',index_1)

				if index_2 != -1:
					first = text[:index_2]
					second = text[index_2:]

					array_1.append(first)
					text = second
				else:
					if (text.find('Вход') != -1 or text.find('вход') != -1) and (text.find('Стоп') != -1 or text.find('Cтоп') != -1 or text.find('стоп') != -1) and text.find('Цели') != -1:
						array_1.append(text)
					break
			except Exception as e:
				if (text.find('Вход') != -1 or text.find('вход') != -1) and (text.find('Стоп') != -1 or text.find('Cтоп') != -1 or text.find('стоп') != -1) and text.find('Цели') != -1:
					array_1.append(text)
				break

		# Парсим сообщения на данные
		for text in array_1:
			try:
				check = True
				
				for item in blocked:
					if item in text:
						check = False
						break

				if not check:
					continue

				index = 0
				symbol = ''
				for item in text[index:].split('\n'):
					if '/' in item:
						find_symbol = item.encode('ascii', errors='ignore').decode()
						symbol = sub(r'[^\w\s]+|[\d]+', r'', find_symbol).strip()#cutter(item.encode('ascii', errors='ignore').decode(), ['/', ' ', '(', ')'])
						if symbol:
							for key, item in pred_message_list.items():
								if find_symbol in item:
									if key != customId:
										customId = key
										break
							break
				
				index = text.find('Вход: ') 
				if index == -1:
					index = text.find('вход: ') 

				_open = cutter(text[index+6:].split('\n')[0].replace('..','.'), ['+','+-','$',' ']).encode('ascii', errors='ignore').decode()
				_open = [float(item) for item in _open.split('-') if item]
				
				index = text.find('⛔️')

				stop = cutter(text[index+8:].split('\n')[0], ['на ','+','-','$',' ']).encode('ascii', errors='ignore').decode()
				stop = stop.split('(')[0]

				index = text.find('Цели:')
				target = text[index+5:].split('\n')

				for i, _target in enumerate(target):
					target[i] = cutter(_target.split(") ", 1)[1].split('-')[0], ['+','-','$',' ']).encode('ascii', errors='ignore').decode()
			except Exception as e:
				logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})


			data = {}
			try:
				data["symbol"] = symbol
				data["open"] = _open
				data["stop"] = stop
				data["target"] = target
				data["customId"] = customId
				data["source"] = "telegram-channel-%d"%channel_id
				bot.send_message(chat_id=781804238, text='channel_1 обработал данные\n%s'%str(data))
				logger.info('Body data: \nsymbol: %s\nopen: %s\nstop: %s\ntarget: %s\ncustomId: %s\nsource: %s', 
								str(symbol), str(_open), str(stop), str(target), str(customId), data["source"], extra={'code_id': 'data'})
			except Exception as e:
				logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})

			# import json
			# if data:
			# 	data_tmp = []
			# 	with open('data.json') as json_file:
			# 		try:
			# 			data_tmp = json.load(json_file)
			# 		except:
			# 			pass
	
			# 		data_tmp += [data]

			# 	with open('data.json', 'w') as outfile:
			# 		json.dump(data_tmp, outfile)
			# Передаем на торгового бота
			if data:
				headers = {'Content-Type': 'application/json'}
				response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

				logger.info('Response from a trading bot: %s, %s', 
								str(response.status_code), str(response.text), extra={'code_id': 'info'})

# Этого канала больше нет
def channel_2(text, channel_id, customId, logger, pred_message_list):
	if text.find('Entering') != -1 and  text.find('target') != -1 and text.find('Stop-loss') != -1:
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		
		array_1 = text.split('📍')
		array_1 = [item for item in array_1 if item]

		for text in array_1:
			try:
				index = 0
				symbol = ''
				
				for item in text[index:].split('\n'):
					if item:
						symbol = sub(r'[^\w\s]+|[\d]+', r'',item.encode('ascii', errors='ignore').decode()).strip()
						break

				index = text.find('Entering')

				_open = text[index:].split('\n')[0]
				_open = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", _open)[:2]
				_open = [float(cutter(item, [' ', '-'])) for item in _open]
				_open.sort()

				index = text.find('⭕️')

				stop = text[index:].split('\n')[0]
				stop = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", stop)[0]
				stop = cutter(stop, [' ', '-'])

				target = []

				for target_id in range(10):
					target_text = 'target %d'%(target_id+1)

					index = text.find(target_text)

					if index == -1:
						break

					target_item = text[index:].split('\n')[0].replace(target_text, '')
					target_item = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item)[0]

					target_item = cutter(target_item, [' ', '-'])

					target.append(target_item)
			except Exception as e:
				logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})

			data = {}
			try:
				data["symbol"] = symbol
				data["open"] = _open
				data["stop"] = stop
				data["target"] = target
				data["customId"] = customId
				data["source"] = "telegram-channel-%d"%channel_id
				bot.send_message(chat_id=781804238, text='channel_2 обработал данные\n%s'%str(data))
				logger.info('Body data: \nsymbol: %s\nopen: %s\nstop: %s\ntarget: %s\ncustomId: %s\nsource: %s', 
								str(symbol), str(_open), str(stop), str(target), str(customId), data["source"], extra={'code_id': 'data'})
			except Exception as e:
				logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})

			# Передаем на торгового бота
			if data:
				headers = {'Content-Type': 'application/json'}
				#response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

				logger.info('Response from a trading bot: %s, %s', 
								str(response.status_code), str(response.text), extra={'code_id': 'info'})


#Vip Scapling Mega Crypto
def channel_3(text, channel_id, customId, logger, pred_message_list):
	if len(text.splitlines()) == 4 and (text.find('Stop') != -1 or text.find('Sl') != -1) and (text.find('Leverage') != -1 or text.find('leverage') != -1) and text.find('Targets:') != -1: 
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		try:
			text = text.splitlines()

			symbol = sub(r'[^\w\s]+|[\d]+', r'',text[0].split(' ')[0].encode('ascii', errors='ignore').decode()).strip()
			_open = [float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", text[0])[0])]

			leverage =int(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", text[2])[0])


			target = []
			target = text[1].replace('Targets: ', '').split('-')
			for i in range(len(target)):
				target[i] = float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target[i])[0])

			stop = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", text[3])[0]
		except Exception as e:
			logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})

		data = {}
		try:
			data["symbol"] = symbol
			data["open"] = _open
			data["stop"] = stop
			data["target"] = target
			data["leverage"] = leverage
			data["customId"] = customId
			data["source"] = "telegram-channel-%d"%channel_id
			bot.send_message(chat_id=781804238, text='channel_3 обработал данные\n%s'%str(data))
			logger.info('Body data: \nsymbol: %s\nopen: %s\nstop: %s\ntarget: %s\nleverage: %s\ncustomId: %s\nsource: %s', 
							str(symbol), str(_open), str(stop), str(target), str(leverage), str(customId), data["source"], extra={'code_id': 'data'})
		except Exception as e:
			logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})

		# Передаем на торгового бота
		if data:
			headers = {'Content-Type': 'application/json'}
			response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

			logger.info('Response from a trading bot: %s, %s', 
							str(response.status_code), str(response.text), extra={'code_id': 'info'})


def photo_channel(photo, text, channel_id, customId, logger, pred_message_list):

	try:
		reducePosition = findall(r"\d\/\d", text)
		for item in reducePosition:
			if item:
				reducePosition = item

		symbol = findall(r"( [A-Z]{1,}\/[A-Z]{1,} )|( [A-Z]{1,} \/ [A-Z]{1,} )", text)
		if symbol:
			symbol = findall(r"( [A-Z]{1,}\/[A-Z]{1,} )|( [A-Z]{1,} \/ [A-Z]{1,} )", text)[-1]
		else:
			return None

		for item in symbol:
			if item:
				symbol = cutter(item, [' ', '/'])
				break
	except Exception as e:
		logger.error('Error in first path (photo_channel): %s', str(e), extra={'code_id': 'error'})
		return None
	
	if reducePosition and symbol:
		bot.send_photo(chat_id=781804238, photo=photo)
		photo.seek(0)
		bot.send_message(chat_id=781804238, text='photo_channel спарсил данные, запускаем parse_img')
		try:
			data = parse_img(photo)
			bot.send_message(chat_id=781804238, text='отработал parse_img, идем дальше')

			for key, value in data.items():
				temp = value
				for i in range(len(temp)):
					if float(temp[i]):
						temp[i] = float(temp[i])

				data[key] = temp

			if 'open1' in data:
				data['open'] = data['open1'] + data['open']
				data.pop('open1')

			data['symbol'] = symbol
			data['reducePosition'] = reducePosition
			data["customId"] = customId
			data["source"] = "telegram-channel-%d"%channel_id
		except Exception as e:
			bot.send_message(chat_id=781804238, text='photo_channel ошибка блин\n%s'%str(e))
			logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})
			return None

		bot.send_message(chat_id=781804238, text='photo_channel спарсил данные\n%s'%str(data))
		try:
			logger.info('Body data: \nsymbol: %s\nopen: %s\nstop: %s\ntarget: %s\nreducePosition: %s\ncustomId: %s\nsource: %s', 
							str(data['symbol']), str(data['open']), str(data['stop']), str(data['target']), str(data['reducePosition']), str(customId), data["source"], extra={'code_id': 'data'})
		except:
			pass
		# Передаем на торгового бота
		if data:
			headers = {'Content-Type': 'application/json'}
			response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)
			bot.send_message(chat_id=781804238, text='photo_channel передал данные\n%s'%str(response.text))

			logger.info('Response from a trading bot: %s, %s', 
							str(response.status_code), str(response.text), extra={'code_id': 'info'})


# Crypto Cat
def channel_4(text, channel_id, customId, logger, pred_message_list):
	if text.find('TP') != -1 and text.find('update') == -1:
		#bot.send_message(chat_id=781804238, text='Crypto Cat спарсил данные, начинаем обрабатывать')
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		try:
			leverage, symbol, _open, stop = None, None, None, None
			
			try:
				results = findall(r"#[A-Z]{1,} \d{1,}X", text)
				
				for item in results:
					if item:
						symbol, leverage  = item.split(' ')[0].replace('#',''), int(item.split(' ')[1].replace('X', ''))	
			
			except:
				pass

			if not symbol:
				try:
					results = findall(r"\#[A-ZА-Я]{1,}", text)
					for item in results:
						if item:
							symbol = item.replace('#', '')
							break 
				except:
					pass

			if not symbol:
				return None

			try:
				results = findall(r"\d+\.\d+ - \d+\.\d+", text)
				if results:
					for item in results:
						if item:
							_open = item.split(' - ')
							_open = [float(_item) for _item in _open]
				else:
					index = text.find('Entry:') 
					if index != -1:
						_open = cutter(text[index+6:].split('\n')[0].replace('..','.'), ['+','+-','$',' ']).encode('ascii', errors='ignore').decode()
						_open = [float((findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", item)[0])) for item in _open.split('-') if item]
			except:
				pass
			
			target = []

			for target_id in range(20):
				try:
					target_text = 'TP %d: '%(target_id+1)

					index = text.find(target_text)

					if index == -1:
						target_text = 'TP%d: '%(target_id+1)
						index = text.find(target_text)
						if index == -1:
							break


					target_item = text[index:].split('\n')[0].replace(target_text, '')
					target_item = target_item.split('(')[0]
					target_item = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item)[0]

					target_item = cutter(target_item, [' ', '-'])

					target.append(target_item)
				except:
					break

			target = [float(item) for item in target]

			if not target:
				return None

			try:
				index = text.find('S/L:') 
				stop = float(cutter(text[index+4:].split('\n')[0].replace('..','.'), ['+','+-','$',' ']).encode('ascii', errors='ignore').decode())
			except:
				pass
		except Exception as e:
			logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})
			return None

		data = {}
		try:
			#data["time"] = time.timestamp()
			data["symbol"] = symbol
			if _open:
				data["open"] = _open
			if stop:
				data["stop"] = stop
			data["target"] = target
			if leverage:
				data["leverage"] = leverage
			data["customId"] = customId
			data["source"] = "telegram-channel-%d"%channel_id
			#bot.send_message(chat_id=781804238, text='channel_4 обработал данные\n%s'%str(data))
			try:
				logger.info('Body data: \nsymbol: %s\nopen: %s\nstop: %s\ntarget: %s\nleverage: %s\ncustomId: %s\nsource: %s', 
							str(symbol), str(_open), str(stop), str(target), str(leverage), str(customId), data["source"], extra={'code_id': 'data'})
			except:
				logger.info('Body data: \nsymbol: %s\ntarget: %s\ncustomId: %s\nsource: %s', 
							str(symbol), str(target), str(customId), data["source"], extra={'code_id': 'data'})
			
		except Exception as e:
			logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})
		
		# import json
		# if data:
		# 	data_tmp = []
		# 	with open('CryptoCat.json') as json_file:
		# 		try:
		# 			data_tmp = json.load(json_file)
		# 		except:
		# 			pass
		# 		print(len(data_tmp))
		# 		data_tmp += [data]

		# 	with open('CryptoCat.json', 'w') as outfile:
		# 		json.dump(data_tmp, outfile)

		# Передаем на торгового бота
		if data:
			headers = {'Content-Type': 'application/json'}
			response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

			logger.info('Response from a trading bot: %s, %s', 
							str(response.status_code), str(response.text), extra={'code_id': 'info'})


#CryptoBull 
def channel_5(text, channel_id, customId, logger, pred_message_list):
	if text.find('Цeли') != -1 and text.find('CryptoBull') != -1:
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		try:
			leverage, symbol,stop, _open, openVolume, target  = None, None, None, [], [], []
			results = findall(r"[A-ZА-Я]{1,}\/[A-ZА-Я]{1,}", text)
			for item in results:
				if item:
					symbol = item
					break 
			
			try:
				results = findall(r"(\d+% .. \d+\.\d*|\d+% .. \d+)", text)
				if results:
					for item in results:
						if item:
							temp = item.split('%')
							openVolume.append(int(temp[0]))
							_open.append(float(findall(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?", temp[1])[0][0]))
			except: 
				pass

			target_id = 1
			while True:
				target_text = '%d. '%(target_id)
				target_id += 1

				index = text.find(target_text)

				if index == -1:
					break

				target_item = text[index:].split('\n')[0].replace(target_text, '')
				target_item = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item)[0]

				target_item = cutter(target_item, [' ', '-'])
				target.append(float(target_item))

			results = findall(r"\d+x", text)
			leverage = float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", results[0])[0])
		except Exception as e:
			logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})
			return None

		data = {}
		try:
			# data["time"] = time.timestamp()
			data["symbol"] = symbol
			if _open:
				data["open"] = _open
			if openVolume:
				data["openVolume"] = openVolume
			data["target"] = target
			data["leverage"] = leverage
			data["customId"] = customId
			data["source"] = "telegram-channel-%d"%channel_id
			bot.send_message(chat_id=781804238, text='channel_5 обработал данные\n%s'%str(data))
		
			logger.info('Body data: \nsymbol: %s\nopen: %s\nstop: %s\ntarget: %s\nleverage: %s\ncustomId: %s\nsource: %s', 
							str(symbol), str(_open), str(stop), str(target), str(leverage), str(customId), data["source"], extra={'code_id': 'data'})
		except Exception as e:
			logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})
			return None

		# import json
		# if data:
		# 	data_tmp = []
		# 	with open('CryptoBull.json') as json_file:
		# 		try:
		# 			data_tmp = json.load(json_file)
		# 		except:
		# 			pass

		# 		data_tmp += [data]

		# 	with open('CryptoBull.json', 'w') as outfile:
		# 		json.dump(data_tmp, outfile)


		# Передаем на торгового бота
		if data:
			headers = {'Content-Type': 'application/json'}
			response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

			logger.info('Response from a trading bot: %s, %s', 
							str(response.status_code), str(response.text), extra={'code_id': 'info'})

# Маржерубы больше нет 1315722059
def channel_6(text, channel_id, customId, logger, pred_message_list, time):
	text = text.replace('\u200c', '')
	if text.find('Entry') != -1 or text.find('Targets') != -1 or text.find('Еntry') != -1 or text.find('Entrу'):
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		try:
			leverage, symbol, stop, _open, openVolume, target, targetVolume, stopVolume   = None, None, [], [], [], [], [], []
			results = findall(r"[A-ZА-Я]{1,}\/[A-ZА-Я]{1,}", text)
			for item in results:
				if item:
					symbol = item
					break 
			if not symbol:
				return None
			symbol = symbol.replace('/','')

			
			results = findall(r"\d+\.\d*X", text)
			try:
				leverage = float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", results[0])[0])
			except:
				leverage = None
			
			entry_targets = re_split(r'Entry|Еntry|Entrу', text)[1].split('\n\n')[0]
			target_id = 1
			while True:
				target_text = '%d) '%(target_id)
				target_id += 1

				index = entry_targets.find(target_text)

				if index == -1:
					break

				target_item = entry_targets[index:].split('\n')[0].replace(target_text, '')
				target_item = target_item.split('-')
				_open.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[0])[0]))
				openVolume.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[1])[0]))

			profit_targets = re_split(r'Take-Profit|Take-Рrofit|Tаke-Profit|Тake-Рrofit|Takе-Profit|Take-Рrоfit|Take-Prоfit|Тake-Prоfit|Takе-Рrofit|Тake-Profit', text)[1].split('\n\n')[0]

			target_id = 1
			while True:
				target_text = '%d) '%(target_id)
				target_id += 1

				index = profit_targets.find(target_text)

				if index == -1:
					break

				target_item = profit_targets[index:].split('\n')[0].replace(target_text, '')
				target_item = target_item.split('-')

				target.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[0])[0]))
				targetVolume.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[1])[0]))

			stop_targets = re_split(r'Stop|Stoр|Stоp|Stор', text)[1].split('\n\n')[0]
			target_id = 1
			while True:
				target_text = '%d) '%(target_id)
				target_id += 1

				index = stop_targets.find(target_text)

				if index == -1:
					break

				target_item = stop_targets[index:].split('\n')[0].replace(target_text, '')
				target_item = target_item.split('-')

				stop.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[0])[0]))
				stopVolume.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[1])[0]))

		except Exception as e:
			logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})
			return None

		data = {}
		try:
			data["time"] = time.timestamp()
			data["symbol"] = symbol
			data["open"] = _open
			data["openVolume"] = openVolume
			data["target"] = target
			data["targetVolume"] = targetVolume
			data["stop"] = stop
			data["stopVolume"] = stopVolume
			data["leverage"] = leverage
			data["customId"] = customId
			data["source"] = "telegram-channel-%d"%channel_id
			bot.send_message(chat_id=781804238, text='channel_6 обработал данные\n%s'%str(data))
			logger.info('Body data: \nsymbol: %s\nopen: %s\nopenVolume: %s\nstop: %s\nstopVolume: %s\ntarget: %s\ntargetVolume: %s\nleverage: %s\ncustomId: %s\nsource: %s', 
							str(symbol), str(_open),str(openVolume), str(stop),str(stopVolume), str(target),str(targetVolume), str(leverage), str(customId), data["source"], extra={'code_id': 'data'})
			
			# print('Body data: \nsymbol: %s\nopen: %s\nopenVolume: %s\nstop: %s\nstopVolume: %s\ntarget: %s\ntargetVolume: %s\nleverage: %s\ncustomId: %s\nsource: %s'%
			# 				(str(symbol), str(_open),str(openVolume), str(stop),str(stopVolume), str(target),str(targetVolume), str(leverage), str(customId), data["source"]))

		except Exception as e:
			logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})
			return None

		import json
		if data:
			data_tmp = []
			with open('margeruby.json') as json_file:
				try:
					data_tmp = json.load(json_file)
				except:
					pass

				data_tmp += [data]

			with open('margeruby.json', 'w') as outfile:
				json.dump(data_tmp, outfile)

		# Передаем на торгового бота
		# if data:
		# 	headers = {'Content-Type': 'application/json'}
		# 	response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

		# 	logger.info('Response from a trading bot: %s, %s', 
		# 					str(response.status_code), str(response.text), extra={'code_id': 'info'})


# @Artem_Trade (1271594974)
def channel_7(text, channel_id, customId, logger, pred_message_list):
	if text.find('Купил') != -1 or text.find('Цели') != -1:
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		try:
			symbol, leverage, target, targetVolume = None, None, [], []
			results = findall(r"\#[A-ZА-Я]{1,}", text)
			for item in results:
				if item:
					symbol = item.replace('#', '')
					break 

			results = findall(r"х\d+\.\d*", text)
			try:
				leverage = float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", results[0])[0])
			except:
				leverage = None

			target_id = 1
			while True:
				target_text = '%d цель:'%(target_id)
				target_id += 1

				index = text.find(target_text)

				if index == -1:
					break

				target_item = text[index:].split('\n')[0].replace(target_text, '')
				target_item = target_item.split('(')

				try:
					target.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[0])[0]))
					targetVolume.append(float(findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target_item[1])[0]))
				except:
					pass

			if not target:
				return None

		except Exception as e:
			logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})
			return None

		data = {}
		try:
			# data["time"] = time.timestamp()
			data["symbol"] = symbol
			data["target"] = target
			data["targetVolume"] = targetVolume
			if leverage:
				data["leverage"] = leverage
			data["customId"] = customId
			data["source"] = "telegram-channel-%d"%channel_id
			bot.send_message(chat_id=781804238, text='channel_7 обработал данные\n%s'%str(data))
			logger.info('Body data: \nsymbol: %s\ntarget: %s\ntargetVolume: %s\nleverage: %s\ncustomId: %s\nsource: %s', 
							str(symbol), str(target),str(targetVolume), str(leverage), str(customId), data["source"], extra={'code_id': 'data'})
			
			# print('Body data: \nsymbol: %s\nopen: %s\nopenVolume: %s\nstop: %s\nstopVolume: %s\ntarget: %s\ntargetVolume: %s\nleverage: %s\ncustomId: %s\nsource: %s'%
			# 				(str(symbol), str(_open),str(openVolume), str(stop),str(stopVolume), str(target),str(targetVolume), str(leverage), str(customId), data["source"]))

		except Exception as e:
			logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})
			return None

		# import json
		# if data:
		# 	data_tmp = []
		# 	with open('artem_trade.json') as json_file:
		# 		try:
		# 			data_tmp = json.load(json_file)
		# 		except:
		# 			pass

		# 		data_tmp += [data]

		# 	with open('artem_trade.json', 'w') as outfile:
		# 		json.dump(data_tmp, outfile)

		# Передаем на торгового бота
		if data:
			headers = {'Content-Type': 'application/json'}
			response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

			logger.info('Response from a trading bot: %s, %s', 
							str(response.status_code), str(response.text), extra={'code_id': 'info'})

# Лоран Смелых (1330518620)
def channel_8(text, channel_id, customId, logger, pred_message_list):
	text = text.encode().decode('utf-8', 'ignore')

	if text.find(u'LoranMarafon') != -1:
		logger.info('Message text: \n%s', text, extra={'code_id': 'message'})
		try:
			symbol, stop, target = None, None, []
			results = findall(r"\#[A-ZА-Я]{1,6}\b", text)
			for item in results:
				if item:
					symbol = item.replace('#', '')
					break 

			if not symbol:
				return None

			try:
				index = text.find('топ:')

				stop = text[index:].split('$')[0]
				stop = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", stop)[0]
				stop = float(cutter(stop, [' ']))
			except:
				pass

			index = text.find('профит')
			if index == -1:
				index = text.find('ель:')

			if index == -1:
				return None

			target = text[index:].split('$')[0]
			target = findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", target)[0]
			target = float(cutter(target, [' ']))
			target = [target]

			if not target:
				return None

		except Exception as e:
			logger.error('Error in find: %s', str(e), extra={'code_id': 'error'})
			return None

		data = {}
		try:
			# data["time"] = time.timestamp()
			data["symbol"] = symbol
			data["target"] = target
			if stop:
				data["stop"] = stop

			data["customId"] = customId
			data["source"] = "telegram-channel-%d"%channel_id

			logger.info('Body data: \nsymbol: %s\ntarget: %s\ncustomId: %s\nsource: %s', 
							str(symbol), str(target), str(customId), data["source"], extra={'code_id': 'data'})	
		except Exception as e:
			logger.error('Error in parsing to data: %s', str(e), extra={'code_id': 'error'})
			return None


		# import json
		# if data:
		# 	data_tmp = []
		# 	with open('artem_trade.json') as json_file:
		# 		try:
		# 			data_tmp = json.load(json_file)
		# 		except:
		# 			pass

		# 		data_tmp += [data]

		# 	with open('artem_trade.json', 'w') as outfile:
		# 		json.dump(data_tmp, outfile)

		# Передаем на торгового бота
		if data:
			headers = {'Content-Type': 'application/json'}
			response = post('https://xoinbot.goodrobot.io/signal', json=data, headers=headers)

			logger.info('Response from a trading bot: %s, %s', 
							str(response.status_code), str(response.text), extra={'code_id': 'info'})


		

# text = '''#LoranMarafon 👨🏻‍💻

# Зашел в #XRP в ЛОНГ по цене: 1.097$. Стоп: 1.059$ Тейк профит 1.239$

# Сделка хороша тем, что риск прибыль в ней более чем адекватные: 1/3.3'''

# text = '''#LoranMarafon
# #XRP

# Открыл очередной "сомнительный" лонг по XRP😂

# Зашел по 1.14$
# Стоп: 1.119$
# Цель: 1.229$

# ✖️✖️
# Вижу для себя некоторые моменты технического плана, побуждающие зайти в сделку. Стоп короткий, цель близко. Работаем.'''


# import logging
# logger = logging.getLogger('parser_logger')
# channel_8(text, 1, 1, logger, [])








