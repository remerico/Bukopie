import os
import tornado.ioloop
import tornado.web
import sockjs.tornado

import jsonrpc
import utils
from config import Config
from stations import Stations
from player import Player
from services import Services
import handlers as h


class Application(tornado.web.Application):
    def __init__(self):

        self.config = Config()
        self.playerEnabled = True
        self.player = Player(self.config)
        self.player.log.callback = self.handle_player_status;
        self.stations = Stations(self.config.get('stationfile'))
        self.services = Services()

        self.status = {
            'stations' : self.stations.list,
            'playing'  : False,
            'stream'   : '',
            'playid'   : -1,
            'player'   : self.player.log.get_status(),
            'volume'   : '25'
        }


        methods = {
            'getStatus' : h.GetStatusHandler,
            'play' : h.PlayHandler,
            'stop' : h.StopHandler,
            'setVol' : h.SetVolumeHandler,
            'pause' : h.PauseHandler
        }
        self.router = jsonrpc.JsonRpcRouter(self, methods, '/socket')


        handlers = [
            (r"/",            h.IndexHandler),
            (r"/favicon.ico", tornado.web.StaticFileHandler, {'path': 'favicon.ico'}),
        ] + self.router.urls 

        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path   = os.path.join(os.path.dirname(__file__), "static"),
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        self.listen(self.config.get('port'))


    def update_status(self, values):
        self.status = utils.merge_dict(self.status, values)
        self.router.notify('status', values)


    # Event handlers
    def handle_player_status(self, key, value):
        self.update_status({ 'player' : { key : value } })

        if key == 'stream':
            self.services.get_track_info(value, self.callback_track_info)

    def callback_track_info(self, trackinfo):
        self.update_status({ 'trackinfo' : trackinfo })
        


def run():
    print('Bukopie running')
    Application()
    tornado.ioloop.IOLoop.instance().start()



if __name__ == '__main__':
    run()