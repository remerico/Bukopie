#!/usr/bin/python

import csv
from os import path
import bottle
from bottle import route, run, template

from player import Player


'''Read stations from CSV file'''
CSV_FILE =  path.join(path.dirname(__file__), 'stations.csv')
print(CSV_FILE)

def get_stations(f):
	try:
		csvfile = open(f, 'rb')
	except IOError, e:
		print str(e)
		sys.exit(1)

	stations = []
	for row in csv.reader(csvfile, skipinitialspace=True):
		if row[0].startswith('#'):
			continue
		name, url = map(lambda s: s.strip(), row)
		stations.append((name, url))
		
	return stations
	

stations = get_stations(CSV_FILE)
isplaying = -1

player = Player()


@route('/')
def index(playid=-1):
	global isplaying
	if playid == -1 : playid = isplaying
	return template('''
		%if playid != -1:
			<p>
				Now playing:  <b>{{stations[playid][0]}}</b>
				[<a href="/stop">stop</a>]
			</p>
			<p>Volume: 
			<a href="/volume/up">[x]</a>
			<a href="/volume/down">[-]</a>
			</p>
		%end
		
		<h5>Station List</h5>
		<ul>
		%id = 0
		%for row in stations:
			<li><a href="/play/{{id}}">{{row[0]}}</a></li>
			%id += 1
		%end
		</ul>
	''', stations=stations, playid=playid)

@route('/play/<playid:int>')
def play(playid=-1):
	global isplaying
	
	if playid != isplaying:
		bottle.TEMPLATES.clear()
		player.play(stations[playid][1])
		isplaying = playid
	
	return index(playid=playid)

@route('/stop')
def stop():
	global isplaying
	
	if isplaying != -1:
		player.close()
	
	return index(playid=-1)
	
@route('/volume/<action>')
def volume(action=''):
	if action == 'up':
		player.volumeUp()
	elif action == 'down':
		player.volumeDown()
		
	return index()	
	
run(host="0.0.0.0", port=8081, debug=True)
