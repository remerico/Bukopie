import subprocess
import thread
import os
import threading
import logging
import time
import re

'''
    Slave mode options
        get_property path   : URL
        volume 1            : Increase volume
        volume 0            : Decrease volume
        volume <percent> 1  : Set percent
        mute                : Mute/Unmute
        quit                : Quit
        get_time_pos        : Time in seconds
        get_audio_bitrate   : Bitrate

    Status messages
        Name   : Chillout Dreams - DIGITALLY IMPORTED - relax to the sounds of dream and ibiza style chillout
        Genre  : Electronic Chillout Dream
        Website: http://www.di.fm/chilloutdreams
        Public : yes
        Bitrate: 96kbit/s
        Starting playback...
        ICY Info: StreamTitle='Baby Mammoth - Lost Bearings';StreamUrl='';
 '''


class PlayerLog:

    def __init__(self, player):

        # Thread locks. These are needed because 
        # MPlayer status updates runs on another thread
        self.status_lock = threading.Lock()

        self.callback = None
        self.player = player

        self.reset_status();

    def write(self, message):
        message = message.strip()

        if len(message) > 0:
            print(message)
            self.parse_line(message)


    def parse_line(self, line):
        """ Some pretty lame regex routines :D """

        r = re.search('Name\s*:\s*(.+)', line)
        if r: self.update_status('station', r.group(1))

        if not r:
            r = re.search('Bitrate\s*:\s*(.+)', line)
            if r: self.update_status('bitrate', r.group(1))

        if not r:
            r = re.search('Website\s*:\s*(.+)', line)
            if r: self.update_status('url', r.group(1))

        if not r:
            r = re.search("ICY Info: StreamTitle=\'(.*?)\';", line)
            if r:
                self.update_status('stream', r.group(1));

        if not r:
            r = re.search("Volume:\s*([0-9]*)", line)
            if r:
                self.update_status('volume', r.group(1));

        if not r:
            if line.startswith('Starting playback...'):
                self.update_status('connection', 'connected');
            elif line.startswith('Resolving') or line.startswith('Connecting'):
                self.update_status('connection', 'connecting');


    def update_status(self, key, value):
        self.status_lock.acquire()
        if (self.status[key] != value):
            self.status[key] = value
            if self.callback != None:
                self.callback(key, value)
        self.status_lock.release()

    def reset_status(self):
        self.status = {
            'stream'     : '',
            'station'    : '',
            'bitrate'    : '',
            'url'        : '',
            'connection' : '',
            'volume'     : self.player.volume,
        }

    def get_status(self):
        self.status_lock.acquire()
        result = self.status.copy()
        self.status_lock.release()
        return result



class Player(object):
    """ Media player class. Playing is handled by mplayer """
    process = None
    
    def __init__(self, config):
        self.volume = 25  # default
        self.config = config
        self.log = PlayerLog(self)

    def __del__(self):
        self.close()

    def updateStatus(self):
        try:
            user_input = self.process.stdout.readline()
            while(user_input != ''):
                self.log.write(user_input)
                user_input = self.process.stdout.readline()

        except:
            logging.error('ERROR!! update status failed!', exc_info=True)

    def is_playing(self):
        return bool(self.process)

    def play(self, stream_url):
        """ use mplayer to play a stream """
        print("Ready to play " + stream_url)
        self.close()

        opts = ["mplayer", "-quiet", 
            "-slave",
            "-cache", str(self.config.cache),
            "-cache-min", str(self.config.cachemin),
            "-volume", str(self.volume)]

        if stream_url.split("?")[0][-3:] in ['m3u', 'pls']:
            opts.extend(["-playlist", stream_url])
        else:
            opts.extend([stream_url])

        self.process = subprocess.Popen(opts, shell=False,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
        thread.start_new_thread(self.updateStatus, ())

    def sendCommand(self, command):
        """ send keystroke command to mplayer """
        if(self.process is not None):
            try:
                self.process.stdin.write(command + '\n')
            except:
                pass

    def mute(self):
        """ mute mplayer """
        self.sendCommand("mute")

    def pause(self):
        """ pause streaming (if possible) """
        self.sendCommand("pause")

    def close(self):
        """ exit pyradio (and kill mplayer instance) """
        self.sendCommand("quit")
        if self.process is not None:
            os.kill(self.process.pid, 15)
            self.process.wait()
        self.process = None
        self.log.reset_status()

    def setVolume(self, percent):
        self.sendCommand("volume " + str(percent) + " 1")
        self.volume = percent
