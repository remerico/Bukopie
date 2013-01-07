from os import path
import json


class Config:

	def __init__(self):
		self.port = 5001
		self.stationfile = 'stations.csv'