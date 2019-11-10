"""IPC helper

Class for simple Inter Process Communication through the use of fifo filesystem pipes.
"""
import os
class fifocom:
	def __init__(self, path):
		self.path = path
		try:
			os.mkfifo(self.path)
		except:
			pass
		
	def __del__(self):
		try:
			os.unlink(self.path)
		except:
			pass
		
	def recv(self):
		pipe = open(self.path, "r")
		s = pipe.read()
		pipe.close()
		return s
	
	def send(self, s):
		pipe = open(self.path, "w")
		pipe.write(s)
		pipe.close()
