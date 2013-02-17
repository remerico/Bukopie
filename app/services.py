# Last.FM Web services
import pylast
import config


class Services(object):

    def __init__(self):
        self.key = 'c170b328716d00ae3dc47eaa0644a677'
        self.secret = 'f920bc65cc7db8b3482bc3b3e73ada79'

        self.network = pylast.LastFMNetwork(api_key = self.key, api_secret = self.secret)
        self.network.enable_caching(file_path=config.CONFIG_DIR+'/lastfmcache')

    def get_cover(self, artist, title):
        """ Get some info about the specified track """

        try:
            cover = self.network.get_album(artist, title).get_cover_image() or ''
        except:
            cover = ''

        print('Cover: ' + cover)

        return cover