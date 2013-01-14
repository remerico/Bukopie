import tornado.httpclient
import re
import urllib
import simplejson as json

lastfm_key = 'c170b328716d00ae3dc47eaa0644a677'

class Services(object):

	def get_track_info(self, track, callback):

		artist, title = self._parseTrack(track)

		if artist and title:
			url = 'http://ws.audioscrobbler.com/2.0/?' + \
				urllib.urlencode({
					'format'  : 'json',
					'method'  : 'track.getInfo',
	                'api_key' : lastfm_key,
	                'artist'  : artist,
	                'track'   : title
					})

			def call(response): self._handleTrackinfo(response, callback)

			print('!! sending data to Last.FM...')
			tornado.httpclient.AsyncHTTPClient().fetch(url, call)

		else:
			callback({ 'cover' : '' })


	def _parseTrack(self, track):

		split = track.split(' - ')
		if len(split) < 2: return '', ''

		artist = split[0]
		title = re.sub("\s*\([^)]*\)", '', split[len(split) - 1]).strip()

		print('Artist: ' + artist + '    Track: ' + title)

		return artist, title


	def _handleTrackinfo(self, response, callback):

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


