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
from handlers import Handler
from status import Status
from db import DB


class Application(tornado.web.Application):
    def __init__(self):

        self.config = Config()
        self.player = Player(self.config)
        self.stations = Stations(self.config.get('stationfile'))
        self.db = DB(self.config.get('databasefile'))
        self.handler = Handler(self)
        self.services = Services()
        self.status = Status(self)

        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path   = os.path.join(os.path.dirname(__file__), "static"),
        )

        tornado.web.Application.__init__(self, self.handler.urls, **settings)
        self.listen(self.config.get('port'))
        


def run():
    print('Bukopie running')
    Application()
    tornado.ioloop.IOLoop.instance().start()



if __name__ == '__main__':
    run()