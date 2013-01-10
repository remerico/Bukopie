import tornado.web
import tornado.ioloop
import json
import utils

playerEnabled = True

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
		player = self.application.player

		status = player.log.get_status()
		arg_ts = utils.try_int(self.get_argument('timestamp', 0), 0)

		if arg_ts != status['timestamp']:
			self.finish(json.dumps(status))
		else:
			player.log.add_callback(self.new_update)

	def new_update(self, message):
		if self.request.connection.stream.closed(): 
			return
		self.finish(json.dumps(message))

	def on_connection_close(self):
		player = self.application.player
		player.log.remove_callback(self.new_update)


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
		player = self.application.player
		action = self.get_argument("action", None)

		if action:
			if action == 'play':
				id = utils.try_int(self.get_argument("id", None), -1)
				if id != self.application.playid:
					if playerEnabled: 
						player.play(self.application.stations.list[id][1])
					self.application.isplaying = True;
					self.application.playid = id;

			elif action == 'stop':
				self.application.isplaying = False;
				self.application.playid = -1;
				if playerEnabled: player.close()

			elif action == 'setVol':
				percent = self.get_argument("percent", None)
				if percent:
					percent = max(0, min(100, utils.try_int(percent, 0)))
					if playerEnabled: player.setVolume(percent)

			elif action == 'pause':
				if playerEnabled: player.pause()

