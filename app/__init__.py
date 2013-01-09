# coding: utf-8
import os

import tornado.ioloop
import tornado.web

from config import Config
from stations import Stations
from player import Player
import handlers as h


class Application(tornado.web.Application):
    def __init__(self):

		self.config = Config()
		self.player = Player(self.config)
		self.stations = Stations(self.config.stationfile)
		self.isplaying = False;
		self.playid = -1;

		handlers = [
			(r"/", h.MainHandler),
			(r"/nowplaying", h.NowPlayingHandler),
			(r"/action", h.ActionHandler),
			(r"/get/status", h.GetStatusHandler),
			(r"/get/playing", h.GetPlayingHandler),
			(r"/get/stations", h.StationsHandler),
			(r"/favicon.ico", tornado.web.StaticFileHandler, {'path': 'favicon.ico'}),
		]
		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static")
		)

		tornado.web.Application.__init__(self, handlers, **settings)
		

def run():
	print('Bukopie running')
	app = Application()
	app.listen(app.config.port)
	tornado.ioloop.IOLoop.instance().start()