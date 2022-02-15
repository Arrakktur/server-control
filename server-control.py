import subprocess
import os
import psutil
import socket
import configparser
import logging

class Server:
	def __init__(self, path, pathConfig, name, host, port, process = 0):
		self.path = path # Путь до файла запуска сервера
		self.pathConfig = pathConfig # Путь до файла настроек сервера
		self.name = name # Имя сервера 
		self.host = host # Хост сервера
		self.port = port # Порт сервера
		self.process = process # Процесс сервера 
		self.stage = 0 # Состояние сервера

class ServerControl:
	def __init__(self):
		print("Server starting")

		# Id активного сервера (костыль, но так надо)
		self.activeServer = -1

		# Подключаем конфиги
		config = configparser.ConfigParser()
		config.read("config.ini")

		# Подключаем логи
		logging.basicConfig(filename="serverLog.log", level=logging.INFO)
		self.log = logging.getLogger("root")
		self.log.exception('Server starting')

		# Создаем сервера
		# todo это объединить со следующим блоком, сюда нужно загружать информацию из файла сейва
		self.servers = [] # Список серверов
		server = Server('./start-server.sh', '/home/arrakktura/Zomboid/Server/servertest.ini', 'pzServer', '', 5600, 0)
		self.servers.append(server)

		# Добавляем параметры для серверов из конфиг файла
		for i in range(len(self.servers)):
			path = str(config[self.servers[i].name]["path"])
			pathConfig = str(config[self.servers[i].name]["pathConfig"])
			name = str(config[self.servers[i].name]["name"])
			host = str(config[self.servers[i].name]["host"])
			port = int(config[self.servers[i].name]["port"])
			process = int(config[self.servers[i].name]["process"])
			stage = int(config[self.servers[i].name]["stage"])

		self.socketListen()

	def __del__(self):
		pass

	# Парсим строку из запроса
	def parserCommand(command):
		arr = {'command': '', 'server': ''}
		place = command.find('&')
		com = command.find('command')
		server = command.find('server')
		if com >= 0:
			arr['command'] = command[8:place]
		if server >= 0:
			arr['server'] = command[server+7:]
		return arr

	# Слушаем команды
	def socketListen(self):
		#Открываем сокет
		self.sock = socket.socket()
		self.sock.bind((self.host, self.port))
		self.sock.listen(5)
		self.log.exception('Start listen command')

		while 1:
			# Слушаем запросы
			self.conn, address = self.sock.accept()
			data = self.conn.recv(1024)
			data = data.decode('utf-8')
			self.log.exception('command(' + data + ')')
			message = 0

			# Смотрим на какой сервер пришел запрос
			self.serverFind(self.parserCommand(data)['server'])

			if self.activeServer != -1 and self.activeServer != '':
				
				self.activeServer = -1

				# Обрабатываем запросы
				if self.parserCommand(data)['command'] == 'restart':
					message = self.serverRestart(self.parserCommand(data)['server'])

				if self.parserCommand(data)['command'] == 'stop':
					message = self.serverStop(self.parserCommand(data)['server'])

				if self.parserCommand(data)['command'] == 'start':
					message = self.serverStart(self.parserCommand(data)['server'])

				if self.parserCommand(data)['command'] == 'getModName':
					messageName = self.getlistModName(self.parserCommand(data)['server'])
					messageId = self.getlistModId(self.parserCommand(data)['server'])
					message = messageName + '&' + messageId

				if self.parserCommand(data)['command'] == 'getStage':
					message = self.getStage(self.parserCommand(data)['server'])

				if self.parserCommand(data)['command'] == 'getParams':
					pass

				if self.parserCommand(data)['command'] == 'getLog':
					pass

				if self.parserCommand(data)['command'] == 'createServer':
					pass

				if self.parserCommand(data)['command'] == 'deleteServer':
					pass

				if self.parserCommand(data)['command'] == 'setModName':
					pass

			# Отправляем ответ
			message = str(message)
			message = message.encode('utf-8')

			self.conn.send(message)

	# Поиск сервера
	def serverFind(self, name):
		for server in range(len(self.servers)):
			if self.servers[server].name == name:
				self.activeServer = server
		return 0 

	# Перезапуск сервера
	def serverRestart(self, serverName):
		self.serverStop(serverName)
		return self.serverStart(serverName)

	# Старт сервера
	def serverStart(self, serverName):
		self.serverFind(serverName)
		if self.activeServer == -1:
			return 0
		self.servers[self.activeServer].process = subprocess.Popen(["bash", self.servPath])
		self.servers[self.activeServer].activeServer.stage = 1
		self.activeServer = -1
		self.log.exception('Starting game server')
		return 1

	# Остановка сервера 
	def serverStop(self, serverName):
		self.serverFind(serverName)
		if self.activeServer == 0:
			return 0
		self.servers[self.activeServer].process = psutil.Process(self.activeServer.process.pid)
		for proc in self.servers[self.activeServer].process.children(recursive=True):
			proc.kill()
		self.servers[self.activeServer].process.kill()
		self.servers[self.activeServer].stage = 0
		self.log.exception('Stop game server')
		return 1

	# Получение состояния сервера
	def getStage(self, serverName):
		self.serverFind(serverName)
		if self.activeServer == 0:
			return 0
		self.activeServer = -1
		return self.servers[self.activeServer].stage

	# Установить состояние сервера
	def setStage(self, serverName, stage):
		self.serverFind(serverName)
		self.servers[self.activeServer].stage = stage
		self.activeServer = -1
		return 0

	# Установить моды
	def setMode(self):
		return 1

	# Получить список имен модов
	def getlistModName(self, serverName):
		self.serverFind(serverName)
		with open(self.servers[self.activeServer].pathConfig) as file:
			arr = ''
			for line in file.readlines():
				if (line[0:4] == 'Mods'):
					arr +=  line[5:]
			self.activeServer = -1
			return arr

	# Получить список id модов
	def getlistModId(self, serverName):
		self.serverFind(serverName)
		with open(self.servers[self.activeServer].pathConfig) as file:
			arr = ''
			for line in file.readlines():
				if (line[0:13] == 'WorkshopItems'):
					arr +=  line[14:]
				self.activeServer = -1
			return arr

serv = ServerControl()