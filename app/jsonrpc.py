import tornado.web
import sockjs.tornado
import simplejson as json

import utils

def enum(**enums): return type('Enum', (), enums)

Recipient = enum(Sender = 1,    # Send to sender
                 All = 2,       # Send to all connections
                 Others = 3)    # Send to all connections except sender


class JsonRpcRouter(sockjs.tornado.SockJSRouter):
    def __init__(self,
                 application,
                 methods={},
                 prefix='',
                 user_settings=dict(),
                 io_loop=None):
        super(JsonRpcRouter, self).__init__(JsonRpcConnection, prefix, user_settings, io_loop)
        self._application = application
        self._methods = methods
        self._connections = set()

    def create_session(self, session_id, register=True):
        """ Inject some convenient references to connection objects """
        s = super(JsonRpcRouter, self).create_session(session_id, register)
        s.conn.application = self._application
        s.conn.methods = self._methods
        s.conn.server = self
        return s

    def add_methods(self, methods):
        self._methods.update(methods)

    def notify(self, method, params, clients=None):
        if not clients: clients = self._connections

        if len(clients) > 0:
            msg = json.dumps({ 'method' : method, 'params' : params })
            print(msg)
            self.broadcast(clients, msg)

    @property
    def connections(self):
        return self._connections




class JsonRpcConnection(sockjs.tornado.SockJSConnection):

    def on_open(self, request):
        self.server.connections.add(self) 
        print(str(len(self.server.connections)) + ' users')

    def on_close(self):
        self.server.connections.remove(self)
        print(str(len(self.server.connections)) + ' users')

    def on_message(self, message):
        print('RECV : ' + message)

        data   = json.loads(message)
        method = data.get('method');
        params = data.get('params');
        id     = data.get('id');

        # self.methods is injected from JsonRpcRouter.create_session
        handler_class = self.methods.get(method)

        # Instance of JsonRpcHandler
        if handler_class:
            handler = handler_class(self, id)
            handler.on_execute(params)

    def notify(self, method, params, recipient=Recipient.All):
        if recipient == Recipient.Sender:
            clients = set([self])
        elif recipient == Recipient.All:
            clients = self.server.connections
        elif recipient == Recipient.Others:
            clients = self.other_connections
        
        self.server.notify(method, params, clients)

    def respond(self, result, error, id):
        msg = json.dumps({ 'result' : result, 'error'  : error, 'id' : id })
        self.send(msg)

    @property
    def other_connections(self):
        """ Returns a set of other connections except this instance """
        others = set()
        for c in self.server.connections:
            if c != self: others.add(c)
        #print('serving to ' + str(len(others)))
        return others


class JsonRpcHandler(object):

    def __init__(self, connection, id):
        # Instance of JsonRpcConnection
        self.connection = connection

        # Instance of tornado.web.Application
        self.application = connection.application

        # Arbitrary number received from client
        self.id = id

    def on_execute(self, params):
        pass

    def respond(self, result, error=None):
        self.connection.respond(result, error, self.id)

    def notify(self, method, params, recipient=Recipient.All):
        self.connection.notify(method, params, recipient)
