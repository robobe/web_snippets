import os
import cherrypy

PATH = os.path.abspath(os.path.dirname(__file__))

config = {
    'global' : {
        'server.socket_host' : '127.0.0.1',
        'server.socket_port' : 8080
    },
    '/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': PATH,
                'tools.staticdir.index': 'index.html',
            },
}

class App:

    @cherrypy.expose
    def index(self):
        return "hello"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def my_action(self):
        result = [
            {"id":1 , "name": "pos1"},
            {"id":2 , "name": "pos2"},
            {"id":3 , "name": "pos3"}
        ]
        
        {"operation": "request", "result": "success"}
        input_json = cherrypy.request.json
        value = input_json["my_key"]
        print (f"key: {value}")
        return result

if __name__ == '__main__':
    cherrypy.quickstart(App(), '/', config)