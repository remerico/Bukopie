import csv
import json
from os import path

class Stations:

	def __init__(self, file):
		self.file = path.join(path.dirname(__file__), file)
		self.list = Stations.read(self.file)

	@staticmethod
	def read(file):

		stations = []

		try:
			csvfile = open(file, 'rb')
		except IOError, e:
			print str(e)
			return stations
		
		for row in csv.reader(csvfile, skipinitialspace=True):
			if row[0].startswith('#'): continue
			name, url = map(lambda s: s.strip(), row)
			stations.append((name, url))

		csvfile.close()
		return stations