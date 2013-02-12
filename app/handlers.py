import tornado.web
import sockjs.tornado
import simplejson as json

import utils
from jsonrpc import JsonRpcHandler, Recipient, JsonRpcRouter


class Handler(object):
    def __init__(self, application):
        self.application = application
        self.methods = {
            'getStatus' : GetStatusHandler,
            'play'      : PlayHandler,
            'stop'      : StopHandler,
            'setVol'    : SetVolumeHandler,
            'pause'     : PauseHandler,
            'getHistory': GetHistoryHandler,
        }
        self.router = JsonRpcRouter(application, self.methods, '/socket')

        self.urls = [
            (r"/",            IndexHandler),
            (r"/favicon.ico", tornado.web.StaticFileHandler, {'path': 'favicon.ico'}),
        ] + self.router.urls 


class GetStatusHandler(JsonRpcHandler):
    def on_execute(self, params):
        self.respond(self.application.status.status)


class PlayHandler(JsonRpcHandler):
    def on_execute(self, params):

        play_id = utils.try_int(params[0], -1)

        if play_id >= 0 and play_id != self.application.status['playid']:
            self.application.player.play(self.application.stations.get_id(play_id).url)

            self.application.status.update({ 
                'playing' : True,
                'playid'  : play_id,
                'stream'  : self.application.stations.list[play_id].name if play_id >= 0 else '',
                'player'  : self.application.player.log.get_status(),
                'trackinfo' : {}
            })

        self.respond(1)


class StopHandler(JsonRpcHandler):
    def on_execute(self, params):
        self.application.player.close()

        self.application.status.update({ 
            'playing' : False, 
            'playid'  : -1,
            'stream'  : '',
            'player'  : self.application.player.log.get_status(),
            'trackinfo' : {}
        })

        self.respond(1)


class SetVolumeHandler(JsonRpcHandler):
    def on_execute(self, params):
        percent = utils.try_int(params[0], -1)

        if percent >= 0:
            percent = max(0, min(100, percent))
            self.application.player.setVolume(percent)

        self.application.status['volume'] = str(percent)
        self.respond(1)
        self.notify('status', { 'volume' : str(percent)}, Recipient.Others)


class PauseHandler(JsonRpcHandler):
    def on_execute(self, params):
        self.application.player.pause()
        self.respond(1)


class GetHistoryHandler(JsonRpcHandler):
    def on_execute(self, params):
        data = self.application.db.get_listening_history()
        res = []
        for i in data:
            res.append({ 'artist' : i[0], 'title' : i[1] })

        self.respond(res)
        

class IndexHandler(tornado.web.RequestHandler):

    def get(self):  
        self.render("index.html", config=self.application.config)
