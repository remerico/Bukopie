from copy import deepcopy
import re

def try_int(data, default):
	try:
		value = int(data)
		return value
	except ValueError:
		return default

def merge_dict(a, b):
    '''recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then merge_dict is called
    on both values and the result stored in the returned dictionary.'''
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
                result[k] = merge_dict(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

def parse_track(track):
    """ Takes a track name and try to parse it as artist and title """

    split = track.split(' - ')
    if len(split) < 2: return '', ''

    artist = split[0]
    title = re.sub("\s*\([^)]*\)", '', split[len(split) - 1]).strip()

    return artist, title