import sqlite3
import time

class DB(object):

    def __init__(self, file):
        self._file = file
        self._conn = sqlite3.connect(file)
        self.init_database(file)

    def to_unicode(self, str):
        return unicode(str, 'utf-8')

    def add_played_song(self, artist, title, station='', cover=''):

        # Do not allow empty fields
        if artist.strip() == '' or title.strip() == '': return

        p_artist, p_title = self.get_last_played_song()
        if p_artist == artist and p_title == title:
            return

        artist = self.to_unicode(artist)
        title = self.to_unicode(title)
        station = self.to_unicode(station)
        cover = self.to_unicode(cover)

        with self._conn as c:
            cur = c.cursor()

            cur.execute(u"""INSERT OR IGNORE INTO songs (artist, title, cover)
                            VALUES (?, ?, ?)""", (artist, title, cover))

            cur.execute(u"INSERT OR IGNORE INTO stations (name) VALUES (?)", (station,))

            cur.execute(u"SELECT id from songs WHERE artist = ? AND title = ?", (artist, title))
            song_id = cur.fetchone()[0]

            cur.execute(u"SELECT id from stations WHERE name = ?", (station,))
            station_id = cur.fetchone()[0]

            timestamp = int(time.time())

            cur.execute(u"""INSERT INTO song_history
                            (song_id, station_id, timestamp)
                            VALUES (?, ?, ?)""",
                            (song_id, station_id, timestamp))


    def add_played_station(self, name, url):

        name = self.to_unicode(name)
        url = self.to_unicode(url)

        with self._conn as c:
            cur = c.cursor()
            cur.execute(u"INSERT OR IGNORE INTO stations (name, url) VALUES (?, ?)",
                (name, url))

            cur.execute(u"SELECT id from stations WHERE name = ?", (name,))
            station_id = cur.fetchone()[0]

            timestamp = int(time.time())

            cur.execute(u"""INSERT INTO station_history 
                            (station_id, timestamp)
                            VALUES (?, ?)""",
                            (station_id, timestamp))

    def get_last_played_song(self):
        with self._conn as c:
            cur = c.cursor()
            cur.execute(u"""SELECT artist, title from view_song_history
                    ORDER BY timestamp DESC LIMIT 1""")

            res = cur.fetchone()

            if res: return res[0], res[1]
            else: return None, None


    def set_favorite_song(self, artist, title, favorite):
        
        artist = self.to_unicode(artist)
        title = self.to_unicode(title)

        with self._conn as c:
            c.execute(u"""UPDATE songs SET favorite = ?
                         WHERE artist = ? AND title  = ?""",
                           (1 if favorite else 0, artist, title)) 

    def get_listening_history(self, limit=100):
        with self._conn as c:
            cur = c.cursor()
            cur.execute(u"""SELECT artist, title, station, cover
                         FROM view_song_history
                         ORDER BY timestamp DESC
                         LIMIT ?""", (limit,) )

            return cur.fetchall()


    def is_favorite_song(self, artist, title):

        artist = self.to_unicode(artist)
        title = self.to_unicode(title)

        with self._conn as c:
            cur = c.cursor()
            cur.execute(u"""SELECT favorite FROM songs
                         WHERE artist = ? AND title  = ?""",
                            (artist, title))

            res = cur.fetchone()
            return res[0] == 1 if res else False


    def init_database(self, file):
        with self._conn as c:
            c.execute("""CREATE TABLE IF NOT EXISTS songs 
                        (id INTEGER PRIMARY KEY,
                         artist TEXT, 
                         title TEXT,
                         cover TEXT,
                         favorite INTEGER,
                         UNIQUE(artist, title))""")

            c.execute("""CREATE TABLE IF NOT EXISTS stations
                        (id INTEGER PRIMARY KEY,
                         name TEXT UNIQUE,
                         url TEXT,
                         favorite INTEGER)""")

            c.execute("""CREATE TABLE IF NOT EXISTS song_history
                        (id INTEGER PRIMARY KEY,
                         song_id INTEGER,
                         station_id INTEGER,
                         timestamp INTEGER,
                         FOREIGN KEY(song_id) REFERENCES songs(id),
                         FOREIGN KEY(station_id) REFERENCES stations(id))""")

            c.execute("""CREATE TABLE IF NOT EXISTS station_history
                        (id INTEGER PRIMARY KEY,
                         station_id INTEGER,
                         timestamp INTEGER,
                         FOREIGN KEY(station_id) REFERENCES stations(id))""")

            c.execute("""CREATE VIEW IF NOT EXISTS view_song_history AS
                            SELECT artist, title, cover, 
                                   songs.favorite AS "favorite", 
                                   stations.name AS "station", 
                                   timestamp
                            FROM song_history 
                            INNER JOIN songs 
                                ON song_history.song_id = songs.id 
                            INNER JOIN stations
                                ON song_history.station_id = stations.id""")

