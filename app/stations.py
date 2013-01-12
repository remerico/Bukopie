import csv
import json
from collections import namedtuple
from os import path

StationData = namedtuple('StationData', ['id', 'name', 'url'])

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
	
		i = 0;	
		for row in csv.reader(csvfile, skipinitialspace=True):
			if row[0].startswith('#'): continue
			name, url = map(lambda s: s.strip(), row)
			stations.append(StationData(i, name, url))
			i += 1

		csvfile.close()
		return stations

	def get_id(self, id):
		return self.list[id];