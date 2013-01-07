# coding: utf-8
import os

from flask import Flask

from config import Config
from stations import get_stations

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

config = Config()
stations = get_stations(config.stationfile)

def run():
	print('Bukopie running')
	app.run(port=config.port)

import views