import subprocess
import os
import psutil
import socket
import configparser
import logging

class Server:
	def __init__(self, path, name, host, port, process = 0):
		self.path = path
		self.name = name
		self.host = host
		self.port = port
		self.process = process
		self.stage = 0

class ServerControl:
	def __init__(self):
		print("Server starting")
		self.activeServer = 0

		# Подключаем конфиги
		config = configparser.ConfigParser()
		config.read("config.ini")

		# Подключаем логи
		logging.basicConfig(filename="serverLog.log", level=logging.INFO)
		self.log = logging.getLogger("root")
		self.log.exception('Server starting')

		# Создаем сервера
		# todo сюда нужно загружать информация из файла сейва
		self.servers = []
		server = Server('./start-server.sh', 'pzServer', '', 5600)
		server.push(server)

		self.host = ''
		self.port = int(config["Server"]["port"])

		self.stage = 0
		self.servPath = './start-server.sh'
		self.dir = '/home/arrakktura/Zomboid/Server/servertest.ini'
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
		self.sock = socket.socket()
		self.sock.bind((self.host, self.port))
		self.sock.listen(5)
		self.log.exception('Start listen command')

		while 1:
			self.conn, address = self.sock.accept()
			data = self.conn.recv(1024)
			data = data.decode('utf-8')
			self.log.exception('command(' + data + ')')
			message = 0

			# Выполняем запросов
			for server in range(self.servers):
				if (self.parserCommand(data)['server'] == server.name):

					# Обрабатываем команды
					if self.parserCommand(data)['command'] == 'restart':
						message = self.serverRestart()

					if self.parserCommand(data)['command'] == 'stop':
						message = self.serverStop(self.parserCommand(data)['server'])

					if self.parserCommand(data)['command'] == 'start':
						message = self.serverStart(self.parserCommand(data)['server'])

					if self.parserCommand(data)['command'] == 'getModName':
						messageName = self.getlistModName()
						messageId = self.getlistModId()
						message = messageName + '&' + messageId

					if self.parserCommand(data)['command'] == 'getStage':
						message = self.getStage(self.parserCommand(data)['server'])

					message = str(message)
					message = message.encode('utf-8')

			self.conn.send(message)

	# Поиск сервера
	def serverFind(self, name):
		for server in self.servers:
			if server.name == name:
				self.activeServer = server
		return 0 

	# Перезапуск сервера
	def serverRestart(self):
		self.serverStop()
		self.serverStart()
		return 1

	# Старт сервера
	def serverStart(self, serverName):
		self.serverFind(serverName)
		if self.activeServer == 0:
			return 0
		self.activeServer.process = subprocess.Popen(["bash", self.servPath])
		self.activeServer.stage = 1
		self.log.exception('Starting game server')
		return 1

	# Остановка сервера 
	def serverStop(self, serverName):
		self.serverFind(serverName)
		if self.activeServer == 0:
			return 0
		self.activeServer.process = psutil.Process(self.activeServer.process.pid)
		for proc in self.activeServer5.process.children(recursive=True):
			proc.kill()
		self.activeServer.process.kill()
		self.activeServer.stage = 0
		self.log.exception('Stop game server')
		return 1

	# Получение состояния сервера
	def getStage(self, serverName):
		self.serverFind(serverName)
		if self.activeServer == 0:
			return 0
		return self.activeServer.stage

	# Установить состояние сервера
	def setStage(self, stage):
		self.stage = stage
		return 0

	# Установить моды
	def setMode(self):
		return 'in progress...'

	# Получить список имен модов
	def getlistModName(self):
		with open(self.dir) as file:
			arr = ''
			for line in file.readlines():
				if (line[0:4] == 'Mods'):
					arr +=  line[5:]
			return arr

	# Получить список id модов
	def getlistModId(self):
		with open(self.dir) as file:
			arr = ''
			for line in file.readlines():
				if (line[0:13] == 'WorkshopItems'):
					arr +=  line[14:]
			return arr

serv = ServerControl()