import os
import csv
import json
from collections import namedtuple

StationData = namedtuple('StationData', ['id', 'name', 'url'])
DEFAULT_FILE = os.path.join(os.path.dirname(__file__), 'data', 'stations.csv')


class Stations:

	def __init__(self, file):

		if not os.path.exists(file):
			self.list = Stations.read(DEFAULT_FILE)
			Stations.write(file, self.list)
		else:
			self.list = Stations.read(file)

		self.file = file


	@staticmethod
	def read(file):

		stations = []

		try:
			cf = open(file, 'rb')
		except IOError, e:
			print(str(e))
			return stations
	
		i = 0;	
		for row in csv.reader(cf, skipinitialspace=True):
			if row[0].startswith('#'): continue
			name, url = map(lambda s: s.strip(), row)
			stations.append(StationData(i, name, url))
			i += 1

		cf.close()
		return stations


	@staticmethod
	def write(file, stations):

		try:
			cf = open(file, 'wb')

			writer = csv.writer(cf)
			for s in stations:
				writer.writerow([s.name, s.url])

			return True

		except:
			return False

		finally:
			cf.close()

		


	def get_id(self, id):
		return self.list[id];