import json

def handle_action(message):

	message = json.loads(message)

	if 'action' in message and 'param' in message:

		action = message['action']
		param  = message['param']

		if   action == 'play':
			print('play!')
		
		elif action == 'stop':
			print('stop!')
			
		elif action == 'volumeUp':
			print('vol up!')

		elif action == 'volumeDown':
			print('vol down!')
