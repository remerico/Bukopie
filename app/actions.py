import tornado.web

class ActionHandler(tornado.web.RequestHandler):
	def post(self):
		action = self.get_argument("action", None)

		if action:
			if action == 'play':
				print('play!')
			elif action == 'stop':
				print('stop!')
