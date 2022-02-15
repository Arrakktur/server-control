import subprocess
import os
import psutil
import socket
import configparser
import logging

class Server:
	def __init__(self, path, name, host, port):
		self.path = path
		self.name = name
		self.host = host
		self.port = port

class ServerControl:
	def __init__(self):
		print("LOG: Server starting")
		config = configparser.ConfigParser()
		config.read("config.ini")

		logging.basicConfig(filename="serverLog.log", level=logging.INFO)
		self.log = logging.getLogger("root")
		self.log.exception('Server starting')

		self.host = ''
		self.port = int(config["Server"]["port"])

		self.stage = 0
		self.servPath = './start-server.sh'
		self.dir = '/home/arrakktura/Zomboid/Server/servertest.ini'
		self.socketListen()

	def __del__(self):
		pass

	def parserCommand(command):
		arr = []
		if command.find('command') > 0:
			pass
		if command.find('server') > 0:
			pass

	#Слушаем команды
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

			if data == 'restart':
				message = self.serverRestart()

			if data == 'stop':
				message = self.serverStop()

			if data == 'start':
				message = self.serverStart()

			if data == 'getModName':
				messageName = self.getlistModName()
				messageId = self.getlistModId()
				message = messageName + '&' + messageId

			if data == 'getStage':
				message = self.getStage()

			message = str(message)
			message = message.encode('utf-8')
			self.conn.send(message)

	def serverRestart(self):
		self.serverStop()
		self.serverStart()
		return 1

	def serverStart(self):
		self.process = subprocess.Popen(["bash", self.servPath])
		self.stage = 1
		self.log.exception('Starting game server')
		return 1

	def serverStop(self):
		self.process = psutil.Process(self.process.pid)
		for proc in self.process.children(recursive=True):
			proc.kill()
		self.process.kill()
		self.stage = 0
		self.log.exception('Stop game server')
		return 1

	def getStage(self):
		return self.stage

	def setStage(self, stage):
		self.stage = stage
		return 0

	def setMode(self):
		return 'in progress...'

	def getlistModName(self):
		with open(self.dir) as file:
			arr = ''
			for line in file.readlines():
				if (line[0:4] == 'Mods'):
					arr +=  line[5:]
			return arr

	def getlistModId(self):
		with open(self.dir) as file:
			arr = ''
			for line in file.readlines():
				if (line[0:13] == 'WorkshopItems'):
					arr +=  line[14:]
			return arr

serv = ServerControl()