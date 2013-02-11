import utils

class Status:

    def __init__(self, application):
        self.handler = application.handler
        self.player = application.player
        self.stations = application.stations
        self.services = application.services

        self.status = {
            'stations' : self.stations.list,
            'playing'  : False,
            'stream'   : '',
            'playid'   : -1,
            'player'   : self.player.log.get_status(),
            'volume'   : '25'
        }

        self.player.log.callback = self.handle_player_status;



    def update_status(self, values):
        self.status = utils.merge_dict(self.status, values)
        self.handler.router.notify('status', values)


    # Event handlers
    def handle_player_status(self, key, value):
        self.update_status({ 'player' : { key : value } })

        if key == 'stream':
            self.services.get_track_info(value, self.callback_track_info)

    def callback_track_info(self, trackinfo):
        self.update_status({ 'trackinfo' : trackinfo })


    def __getitem__(self, index):
        return self.status[index]