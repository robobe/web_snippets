import argparse
import random
import os
import time
import datetime
import threading
import signal
import sys
import cherrypy
import json
import urllib.parse as urlparse
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage


class ChatWebSocketHandler(WebSocket):
    def received_message(self, m):
        msg=m.data.decode("utf-8")
        try:
            jo=json.loads(msg)
        except(ValueError, KeyError, TypeError):
            cherrypy.log("Not Json")
        cmd=jo["c"]
        if (cmd=="update"):
            cherrypy.engine.publish('websocket-broadcast','{"cmd_result": 1}')

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))


class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        urlP = urlparse.urlparse(cherrypy.request.base)
        fo = open('index.html')
        content = fo.read()
        fo.close()
        return content

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

pollStatus = True

def getStatus():
	return [random.randint(0, 1),\
			random.randint(0, 1),\
			random.randint(0, 1),\
			random.randint(0, 1),\
			random.randint(0, 1),\
			random.randint(0, 1),\
			random.randint(0, 1),\
			random.randint(0, 1)]

def status2JSON(status):
	return '{"status":['+(', '.join(str(x) for x in status))+']}'

def stpoll():
    global pollStatus
    while pollStatus:
        currentStatus = getStatus()
        status = status2JSON(currentStatus)
        cherrypy.engine.publish('websocket-broadcast', '%s ' %status)
        time.sleep(2)
    cherrypy.log("exitting therad")

if __name__ == '__main__':
    import logging
    from ws4py import configure_logger
    thread = threading.Thread(target = stpoll)
    thread.daemon = True
    thread.start()
    cherrypy.config.update({'server.socket_host': "0.0.0.0",
                            'server.socket_port': 9009,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    pwd=os.getcwd()
    cherrypy.quickstart(Root("0.0.0.0", 9000, False), '', config={
        '/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': ''
        },
        '/ws': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': ChatWebSocketHandler
        },
        '/js': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': 'js'
        }})
