# coding: utf-8
import os

import tornado.ioloop
import tornado.web

from config import Config
from stations import Stations
from actions import ActionHandler


config = Config()
stations = Stations(config.stationfile)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/action", ActionHandler),
            (r"/get/status", StatusHandler),
            (r"/get/stations", StationsHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
	def get(self):	
		self.render("index.html", config=config)


class StatusHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		pass

class StationsHandler(tornado.web.RequestHandler):
	def get(self):
		self.write(stations.json_list())


def run():
	print('Bukopie running')
	app = Application()
	app.listen(config.port)
	tornado.ioloop.IOLoop.instance().start()