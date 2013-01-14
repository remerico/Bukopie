import tornado.web
import sockjs.tornado
import simplejson as json

import utils
from config import Config
from stations import Stations
from player import Player
from services import Services

# Global effing variables
config = Config()
playerEnabled = True
player = Player(config)
stations = Stations(config.stationfile)
services = Services()

status = {
	'stations' : stations.list,
	'playing'  : False,
	'stream'   : '',
	'playid'   : -1,
	'player'   : player.log.get_status()
}

class PlayerConnection(sockjs.tornado.SockJSConnection):
	connections = set()

	def __init__(self, session):
		player.log.callback = self.handle_player_status;
		super(PlayerConnection, self).__init__(session)

	def on_open(self, request):
		self.connections.add(self) 
		print(str(len(self.connections)) + ' users')

	def on_close(self):
		self.connections.remove(self)
		print(str(len(self.connections)) + ' users')

	def on_message(self, message):
		print('RECV : ' + message)

		data   = json.loads(message)

		method = data['method'];
		params = data['params'];
		id     = data['id'];

		if method == 'getStatus':
			self.respond(status, None, id)
		
		elif method == 'play':
			play_id = utils.try_int(params[0], -1)

			if play_id >= 0 and play_id != status['playid']:
				if playerEnabled: player.play(stations.get_id(play_id).url)

				self.update_status({ 
					'playing' : True,
					'playid'  : play_id,
					'stream'  : stations.list[play_id].name if play_id >= 0 else '',
					'player'  : player.log.get_status(),
					'trackinfo' : {}
				})

			self.respond(1, None, id)

		elif method == 'stop':
			if playerEnabled: player.close()

			self.update_status({ 
				'playing' : False, 
				'playid'  : -1,
				'stream'  : '',
				'player'  : player.log.get_status(),
				'trackinfo' : {}
			})

			self.respond(1, None, id)

		elif method == 'setVol':
			percent = utils.try_int(params[0], -1)

			if percent >= 0:
				percent = max(0, min(100, percent))
				if playerEnabled: player.setVolume(percent)

			self.respond(1, None, id)

		elif method == 'pause':
			if playerEnabled: player.pause()
			self.respond(1, None, id)

		
	def respond(self, result, error, id):
		msg = json.dumps({ 'result' : result, 'error'  : error, 'id' : id })
		self.send(msg)

	def notify(self, method, params):
		msg = json.dumps({ 'method' : method, 'params' : params })
		self.broadcast(self.connections, msg);

	def update_status(self, values):
		global status
		status = utils.merge_dict(status, values)
		self.notify('status', values)

	# Event handlers
	def handle_player_status(self, key, value):
		self.update_status({ 'player' : { key : value } })

		if key == 'stream':
			services.get_track_info(value, self.handle_track_info)

	def handle_track_info(self, trackinfo):
		self.update_status({ 'trackinfo' : trackinfo })


class MainHandler(tornado.web.RequestHandler):
	def get(self):	
		self.render("index.html", config=self.application.config)
