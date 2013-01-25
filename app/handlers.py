import tornado.web
import sockjs.tornado
import simplejson as json

import utils
from jsonrpc import JsonRpcHandler


class GetStatusHandler(JsonRpcHandler):
    # 'getStatus'

    def on_execute(self, params):
        self.respond(self.application.status)


class PlayHandler(JsonRpcHandler):
    # 'play'

    def on_execute(self, params):

        play_id = utils.try_int(params[0], -1)

        if play_id >= 0 and play_id != self.application.status['playid']:
            if self.application.playerEnabled:
                self.application.player.play(self.application.stations.get_id(play_id).url)

            self.application.update_status({ 
                'playing' : True,
                'playid'  : play_id,
                'stream'  : self.application.stations.list[play_id].name if play_id >= 0 else '',
                'player'  : self.application.player.log.get_status(),
                'trackinfo' : {}
            })

        self.respond(1)


class StopHandler(JsonRpcHandler):
    # 'stop'

    def on_execute(self, params):
        if self.application.playerEnabled:
            self.application.player.close()

        self.application.update_status({ 
            'playing' : False, 
            'playid'  : -1,
            'stream'  : '',
            'player'  : self.application.player.log.get_status(),
            'trackinfo' : {}
        })

        self.respond(1)


class SetVolumeHandler(JsonRpcHandler):
    # 'setVol'

    def on_execute(self, params):

        percent = utils.try_int(params[0], -1)

        if percent >= 0:
            percent = max(0, min(100, percent))
            if self.application.playerEnabled:
                self.application.player.setVolume(percent)

        self.respond(1)


class PauseHandler(JsonRpcHandler):
    # 'pause'

    def on_execute(self, params):
        if self.application.playerEnabled:
            self.application.player.pause()

        self.respond(1)





class IndexHandler(tornado.web.RequestHandler):

    def get(self):  
        self.render("index.html", config=self.application.config)
