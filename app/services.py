# Last.FM Web services

from tornado import httpclient
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import re
import urllib
import simplejson as json
import md5

lastfm_host = 'ws.audioscrobbler.com'
lastfm_sub = '/2.0/'

lastfm_headers = {
    'Accept-Charset' : 'utf-8',
    'Content-type' : 'application/x-www-form-urlencoded',
    'User-Agent' : 'Bukopie/0.1'
} 

class Services(object):

    def __init__(self):
        self.key = 'c170b328716d00ae3dc47eaa0644a677'
        self.secret = 'f920bc65cc7db8b3482bc3b3e73ada79'
        self.session = ''

    def get_track_info(self, track, callback):
        """ Get some info about the specified track """

        artist, title = self._parseTrack(track)

        if artist and title:
            url = 'http://ws.audioscrobbler.com/2.0/?' + \
                urllib.urlencode({
                    'format'  : 'json',
                    'method'  : 'track.getInfo',
                    'api_key' : self.key,
                    'artist'  : artist,
                    'track'   : title
                    })

            def call(response): self._handleTrackinfo(response, callback)

            print('!! sending data to Last.FM...')
            AsyncHTTPClient().fetch(url, call)

        else:
            callback({ 'cover' : '' })


    def _parseTrack(self, track):
        """ Takes a track name and try to parse it as artist and title """

        split = track.split(' - ')
        if len(split) < 2: return '', ''

        artist = split[0]
        title = re.sub("\s*\([^)]*\)", '', split[len(split) - 1]).strip()

        print('Artist: ' + artist + '    Track: ' + title)

        return artist, title


    def _handleTrackinfo(self, response, callback):
        """ Event handler for self.get_track_info """

        info = { 'cover' : '' }

        if not response.error:
            data = json.loads(response.body)

            if 'error' not in data:
                # Why is it so deeply nested like this, I do not know
                if 'track' in data and 'album' in data['track'] and 'image' in data['track']['album']:
                    covers = data['track']['album']['image']
                    l = len(covers)
                    if l > 0: info['cover'] = covers[l - 1]['#text']

        print(info)

        if callback: callback(info)


    def login(self, username, password, callback):
        """ Login to a Last.FM account, returns mobile session """

        body = urllib.urlencode({
            'format'   : 'json',
            'method'   : 'auth.getMobileSession',
            'username' : username,
            'password' : password,
            'api_key'  : self.key,
            'api_sig'  : self._get_signature(username, password)
            })

        def call(response): self._handle_session_response(response, callback)

        AsyncHTTPClient().fetch(
            HTTPRequest('https://' + lastfm_host + lastfm_sub, 
                method='POST', headers=lastfm_headers, body=body), call)

    def _get_signature(self, username, password):
        sig = 'api_key' + self.key + 'methodauth.getMobileSessionpassword' + password + 'username' + username + self.secret
        return md5.new(sig).hexdigest()

    def _handle_session_response(self, response, callback):

        pass


class _Request(object):

    def __init__(self, service, method, params={}, callback=None, auth=False):
        self.service = service
        self.callback = callback
        
        self.params = {
            'format' : 'json',
            'method' : method,
            'api_key' : service.key,
        }

        for k in params:
            self.params[k] = params[k]

        if auth:
            self.params['sk'] = service.session
        

    def send(self):

        body = urllib.urlencode(self.params)

        AsyncHTTPClient().fetch(
            HTTPRequest('https://' + lastfm_host + lastfm_sub, 
                method='POST', headers=lastfm_headers, body=body), self._handle_response)


    def _handle_response(self, response):
        pass


class SessionRequest(_Request):

    def __init__(self, callback):
        # super(SessionRequest, self).__init__
        pass

    def _handle_response(self, response):
        pass
