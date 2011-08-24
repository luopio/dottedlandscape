import os, time
import tornado.ioloop
import tornado.web
import tornado.httpserver

from blip_receiver import DottedLandscapeCommunicator
    
DL_COMMUNICATOR = DottedLandscapeCommunicator()
WEB_CLIENTS = []


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        title = 'Frontpage'
        self.render("templates/index.html")
    


# no need for a cursor, since we're always just sending the current state. 
# what we need tho' is a way to not send the same data again (notifies filtered in dl_server?)
# options: create client ids based on joining time stamp + random string? <- fingerprint
#    and use that as id here?
#  option 2: make clients send their latest data set back (or some kind of hash/timestamp of
#   it (kind of cursor, but just to avoid redundancy))
class PanelPressedHandler(tornado.web.RequestHandler):
    def post(self):
        args = self.request.arguments
        x = int(args['x'][0])
        y = int(args['y'][0])
        print "pressed at", x, y, 
        print "color", args['c[]'][0]
        self.set_header("Content-Type", "application/json")
        self.write('ok')
        
     

# some update func()
        #global WAITERS
        #for w in WEB_CLIENTS:
        #    w()
        #WEB_CLIENTS = []

    
class PanelUpdateHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        WEB_CLIENTS.append(self.async_callback(self.on_panel_updated))
        self.set_header("Content-Type", "application/json")
        print ">>>> got async request for update"
        
    def on_panel_updated(self, data):
        if self.request.connection.stream.closed():
            return
        print "<<<< finishing async request"
        self.finish(tornado.escape.json_encode(data))
    

def notify_clients_on_panel_change(fd, events):
    data = DL_COMMUNICATOR.on_socket_receive(fd, events)
    if data:
        global WEB_CLIENTS
        for w in WEB_CLIENTS:
            print "notify client!"
            w(data)
        WEB_CLIENTS = []



settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    # 'debug': True,
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/a/press", PanelPressedHandler),    
    (r"/a/update", PanelUpdateHandler),    
    #(r"/js/(\w+)",  tornado.web.StaticFileHandler, dict(path='static/js')),
    #(r"/img/(\w+)", tornado.web.StaticFileHandler, dict(path='static/img')),
    #(r"/css/(\w+)", tornado.web.StaticFileHandler, dict(path='static/css')),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    
    # http_server = tornado.httpserver.HTTPServer(application)
    # http_server.listen(8888)
    # http_server.bind(8888)
    # http_server.start(2) # Forks multiple sub-processes
    
    ioloopy = tornado.ioloop.IOLoop.instance()
    DL_COMMUNICATOR.connect('127.0.0.1', 2323)
    ioloopy.add_handler(DL_COMMUNICATOR.receive_socket.fileno(), 
                        notify_clients_on_panel_change,
                        ioloopy.READ | ioloopy.ERROR)
    ioloopy.start()