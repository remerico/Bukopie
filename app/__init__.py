# coding: utf-8
import os

from flask import Flask
from websocket import handle_websocket
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from config import Config

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

config = Config()


def run():
	http_server = WSGIServer(('',config.port), handler, handler_class=WebSocketHandler)
	http_server.serve_forever()

def handler(environ, start_response):  
	path = environ["PATH_INFO"]
	if path == "/websocket":  
		handle_websocket(environ["wsgi.websocket"])   
	else:  
		return app(environ, start_response)  


import views