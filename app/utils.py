
def try_int(data, default):
	try:
		value = int(data)
		return value
	except ValueError:
		return default
