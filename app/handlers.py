import tornado.web
import json

from player import Player

playerEnabled = False
player = Player()

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
	def get(self):
		self.finish("{chenez : 1}")


class GetPlayingHandler(tornado.web.RequestHandler):
	def get(self):
		playing = {}
		playing['id'] = self.application.playid
		playing['stream'] = self.application.stations.list[self.application.playid][0] if self.application.playid >= 0 else ''
		self.write(json.dumps(playing))


class StationsHandler(tornado.web.RequestHandler):
	def get(self):

		list = []
		i = 0
		for s in self.application.stations.list:
			list.append({ 'id' : i, 'name' : s[0] })
			i += 1

		if self.application.playid >= 0:
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
					if playerEnabled: player.play(self.application.stations.list[int(id)][1])
					self.application.isplaying = True;
					self.application.playid = int(id);

			elif action == 'stop':
				print('stop!')
				self.application.isplaying = False;
				self.application.playid = -1;
				if playerEnabled: player.close()

			elif action == 'volumeUp':
				print('vol up')
				if playerEnabled: player.volumeUp()

			elif action == 'volumeDown':
				print('vol down')
				if playerEnabled: player.volumeDown()
