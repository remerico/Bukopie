import sqlite3
import time

class DB(object):

    def __init__(self, file):
        self._file = file
        self._conn = sqlite3.connect(file)
        self.init_database(file)


    def update_played_song(self, artist, title):
        with self._conn as c:
            cur = c.cursor()
            cur.execute("""UPDATE played_songs
                           SET    play_count  = play_count + 1,
                                  last_played = ?
                           WHERE  artist = ?
                           AND    title  = ?""", 
                           (int(time.time()), artist, title))


            # Update failed, insert new entry instead
            if cur.rowcount == 0:
                print("SQL : INSERT song -> " + artist + "  " + title)
                c.execute("""INSERT INTO played_songs
                                (artist, title, play_count, last_played, favorite)
                               VALUES (?, ?, ?, ?, ?)""",
                               (artist, title, 1, int(time.time()), 0))


    def set_favorite_song(self, artist, title, favorite):
        with self._conn as c:
            c.execute("""UPDATE played_songs SET favorite = ?
                         WHERE artist = ? AND title  = ?""",
                           (1 if favorite else 0, artist, title)) 


    def is_favorite_song(self, artist, title):
        with self._conn as c:
            c.execute("""SELECT favorite FROM played_songs
                         WHERE artist = ? AND title  = ?""",
                            (artist, title))

            res = c.fetchone()

            if res:
                return res[0] == 1
            else:
                return False


    def init_database(self, file):
        with self._conn as c:
            c.execute("""CREATE TABLE IF NOT EXISTS played_songs 
                        (id INTEGER PRIMARY KEY,
                         artist TEXT, 
                         title TEXT,
                         play_count INTEGER, 
                         last_played INTEGER, 
                         favorite INTEGER)""")

            c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS played_songs_idx 
                         ON played_songs(artist, title)""")