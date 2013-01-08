import tornado.web
import json

class MainHandler(tornado.web.RequestHandler):
	def get(self):	
		self.render("index.html", config=self.application.config)


class NowPlayingHandler(tornado.web.RequestHandler):
	def get(self):
		if self.application.isplaying:
			self.render('nowplaying.html', config=self.application.config)
			pass
		else:
			self.redirect('/');


class GetStatusHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		pass


class GetPlayingHandler(tornado.web.RequestHandler):
	def get(self):
		playing = {}
		if self.application.playid >= 0:
			playing['stream'] = self.application.stations.list[self.application.playid][0]
			playing['playing'] = True
		else:
			playing['stream'] = ''
			playing['playing'] = False
		self.write(json.dumps(playing))


class StationsHandler(tornado.web.RequestHandler):
	def get(self):

		list = []
		i = 0
		for s in self.application.stations.list:
			list.append({ 'id' : i, 'name' : s[0] })
			i += 1

		list[self.application.playid]['playing'] = True

		self.write(json.dumps(list))


class ActionHandler(tornado.web.RequestHandler):
	def post(self):
		action = self.get_argument("action", None)

		if action:
			if action == 'play':
				id = self.get_argument("id", None)
				if id and int(id) != self.application.playid:
					print('play! ' + str(id))
					self.application.isplaying = True;
					self.application.playid = int(id);

			elif action == 'stop':
				print('stop!')
				self.application.isplaying = False;
				self.application.playid = -1;
