# coding: utf-8
import json

def handle_websocket(ws):
	while True:
		message = ws.receive()
		if message is None:
			print('ERROR: no message received')
			break
		else:
			print('received: ' + message)
			message = json.loads(message)

			if 'action' in message and 'param' in message:
				pass
			else:
				print('ERROR: invalid message')

			r  = "I have received this message from you : %s" % message
			ws.send(json.dumps({'output': r}))


def handle_action(action, param):

	if   action == 'play':
		pass
	elif action == 'stop':
		pass
	elif action == 'volumeUp':
		pass
	elif action == 'volumeDown':
		pass