from os import path
import json


class Config:

	def __init__(self):
		self.port = 8081
		self.stationfile = 'data/stations.csv'