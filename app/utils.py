from copy import deepcopy

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
