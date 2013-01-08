import tornado.web

class MainHandler(tornado.web.RequestHandler):
	def get(self):	
		self.render("index.html", config=self.application.config)


class NowPlayingHandler(tornado.web.RequestHandler):
	def get(self):
		self.write(self.application.stations.json_list())


class StatusHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		pass

class StationsHandler(tornado.web.RequestHandler):
	def get(self):
		self.write(self.application.stations.json_list())

class ActionHandler(tornado.web.RequestHandler):
	def post(self):
		action = self.get_argument("action", None)

		if action:
			if action == 'play':
				print('play!')
			elif action == 'stop':
				print('stop!')
