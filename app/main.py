import os
import tornado.ioloop
import tornado.web
import sockjs.tornado

from config import Config
import handlers as h


class Application(tornado.web.Application):
    def __init__(self):

		self.config = Config()

		handlers = [
			(r"/",            h.MainHandler),
			(r"/favicon.ico", tornado.web.StaticFileHandler, {'path': 'favicon.ico'}),
		] + sockjs.tornado.SockJSRouter(h.PlayerConnection, '/socket').urls 

		settings = dict(
			template_path = os.path.join(os.path.dirname(__file__), "templates"),
			static_path   = os.path.join(os.path.dirname(__file__), "static"),
		)

		tornado.web.Application.__init__(self, handlers, **settings)
		self.listen(self.config.get('port'))
		

def run():
	print('Bukopie running')
	Application()
	tornado.ioloop.IOLoop.instance().start()



if __name__ == '__main__':
    run()