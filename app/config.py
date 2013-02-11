import os
import simplejson as json


if os.geteuid() == 0:       # User is root
    CONFIG_DIR = '/etc/bukopie'
else:
    CONFIG_DIR = os.path.join(os.getenv('HOME', '~'), '.bukopie')   


CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')


class Config:

    default_config = {
        'port' : 8081,
        'stationfile' : os.path.join(CONFIG_DIR, 'stations.csv'),
        'databasefile' : os.path.join(CONFIG_DIR, 'database.db'),
        'cache-kb' : 160,
        'cache-min' : 50,
        'volume' : 25
    }

    def __init__(self):

        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        if not os.path.exists(CONFIG_FILE):
            self._keys = Config.default_config()
            self.save()
        else:
            self._keys = Config.read(CONFIG_FILE)


    def get(self, key, default=None):
        if default == None: default = Config.default_config[key]
        return self._keys[key] if key in self._keys else default

    def set(self, key, value, save=False):
        self._keys[key] = value
        if save: self.save()

    def save(self):
        Config.write(CONFIG_FILE, self._keys)


    @staticmethod
    def read(file):

        try:
            cf = open(file, 'rb')
            return json.load(cf)
        except:
            return Config.default_config
        finally:
            cf.close()

            
    @staticmethod
    def write(file, keys):
        
        try:
            cf = open(file, 'wb')
            json.dump(keys, cf, indent=4)
            return True
        except:
            return False
        finally:
            cf.close()
