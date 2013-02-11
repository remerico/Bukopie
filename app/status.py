import tornado.ioloop
import utils

class Status:

    def __init__(self, application):
        self.handler = application.handler
        self.player = application.player
        self.stations = application.stations
        self.services = application.services
        self.db = application.db
        self.ioloop = tornado.ioloop.IOLoop.instance()

        self.status = {
            'stations' : self.stations.list,
            'playing'  : False,
            'stream'   : '',
            'playid'   : -1,
            'player'   : self.player.log.get_status(),
            'volume'   : '25'
        }

        self.player.log.callback = self.handle_player_status;


    def update(self, values):
        self.status = utils.merge_dict(self.status, values)
        self.handler.router.notify('status', values)


    # Event handlers
    def handle_player_status(self, key, value):

        def callback():
            self.update({ 'player' : { key : value } })

            if key == 'stream':
                self.services.get_track_info(value, self.handle_track_info)

                artist, title = utils.parse_track(value)
                self.db.update_played_song(artist, title)

        self.ioloop.add_callback(callback)

    def handle_track_info(self, trackinfo):
        self.update({ 'trackinfo' : trackinfo })


    def __getitem__(self, index):
        return self.status[index]

    def __setitem__(self, index, value):
        self.status[index] = value