import os, time, threading

import tornado.ioloop
import tornado.web
import tornado.httpserver
import redis

# include tornadio for socketio capabilities
from tornadio2 import SocketConnection, TornadioRouter, event

from dl.communicator import DottedLandscapeCommunicator
from dl.analytics import Analytics
from dl.animationstorage import AnimationStorage
from dl.animationplayer import AnimationPlayer

DL_COMMUNICATOR = DottedLandscapeCommunicator()
# we define the panel here
DL_COMMUNICATOR.define_panel(8, 8, 3)
WEB_CLIENTS = []
SOCKET_IO_CONNECTIONS = []
ANALYTICS = Analytics()
ANIMATION_STORAGE = AnimationStorage()
ANIMATION_PLAYER = AnimationPlayer(DL_COMMUNICATOR)


# Helper functions
def create_user_fingerprint(req):
    pass


# Template handlers
class LiveHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")
class DrawHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/draw.html")
class AnimateHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/animate.html")
class TextHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/text.html")
class MeemooHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/meemoo_connection.html")
class EmbedHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/embed.html")

class PanelPressedHandler(tornado.web.RequestHandler):
    def post(self):
        args = self.request.arguments
        x = int(args['x'][0])
        y = int(args['y'][0])
        c = args['c[]']

        print "panel_pressed", x, y, c
        user_data = create_user_fingerprint(self.request)
        ANALYTICS.live_drawed({'x': x, 'y': y, 'c': color}, user_data)

        packet = DL_COMMUNICATOR.encode_partial_frame(x, y, c)
        DL_COMMUNICATOR.send(packet)
        self.set_header("Content-Type", "application/json")
        self.write('ok')
        

class PanelUpdateHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        args = self.request.arguments
        print args
        i_want_update_now = args.has_key('sync')
        if i_want_update_now:
            if DL_COMMUNICATOR._cached_payload:
                self.on_panel_updated(DL_COMMUNICATOR._cached_payload)
                
        WEB_CLIENTS.append(self.async_callback(self.on_panel_updated))
        self.set_header("Content-Type", "application/json")
        print ">>>> got request for update on %s" % time.time()
        
    def on_panel_updated(self, data):
        if self.request.connection.stream.closed():
            print "STREAM CLOSED"
            return
        print "<<<< finishing async request"
        self.finish(tornado.escape.json_encode(data))
    

def notify_clients_on_panel_change(fd, events):
    _, data = DL_COMMUNICATOR.check_for_data()
    if data:
        global WEB_CLIENTS
        for w in WEB_CLIENTS:
            # print "notify client %s!" % w
            w(data)
        WEB_CLIENTS = []
        global SOCKET_IO_CONNECTIONS
        for i in SOCKET_IO_CONNECTIONS:
            # print "notify socketio! %s" % i
            i(data)


# TODO: move animation functionality and thread to another file?
class SaveAnimationHandler(tornado.web.RequestHandler):
    def post(self):
        args = self.request.arguments
        channels = int(args['channels'][0])
        name = args['title'][0]
        author = args['author'][0]
        
        # decode the frames from the sucky tornado variable handling
        counter = 0
        frames = []
        print
        print "ARGS:", args
        print
        while args.has_key('data[%s][data][]' % counter):
            fr = args['data[%s][data][]' % counter]
            print "FR", fr
            all_int_fr = []
            for f in fr:
                all_int_fr.append(int(f))
            print "save frame - adding frame %s of len %s" % (counter, len(all_int_fr))
            frames.append((all_int_fr, args['data[%s][duration]' % counter][0]))
            counter += 1
        
        frame_save_structure = {'channels': channels, 
                                'title': name, 'author': author,
                                'frames': frames}
        print "animation save: ", name, author
        global ANIMATION_STORAGE
        ANIMATION_STORAGE.save_animation_to_db(name, frame_save_structure)
        self.set_header("Content-Type", "application/json")
        json = tornado.escape.json_encode({'status': 'ok', 'name': name})
        self.write(json)


class PlayAnimationHandler(tornado.web.RequestHandler):
    def get(self):
        args = self.request.arguments
        name = args['title'][0]
        global ANIMATION_STORAGE
        a = ANIMATION_STORAGE.load_animation_from_db(name)
        if a:
            ANIMATION_PLAYER.play(a['frames'])


class GetAllAnimationsHandler(tornado.web.RequestHandler):
        def get(self):
            global ANIMATION_STORAGE
            a = ANIMATION_STORAGE.get_all_animations()
            json = tornado.escape.json_encode(a)
            self.write(json)


class SocketIOUpdaterConnection(SocketConnection):
    def on_message(self, msg):
        print "web_server: socket.io => got message! why? from who?", msg

    def send_panel_data(self, data):
        self.emit('dl_panel_data', data)

    @event
    def panel_press(self, x, y, c):
        packet = DL_COMMUNICATOR.encode_partial_frame(x, y, c)
        DL_COMMUNICATOR.send(packet)

    @event
    def text_message(self, message, c):
        print "MESSAGE COLOR:", c
        # user_data = create_user_fingerprint(self.request)
        # ANALYTICS.text_messaged({'msg': message, 'color': c}, user_data)
        ANIMATION_PLAYER.text(message=message, color=c)


    def on_open(self, msg):
        print "web_server: socketio opened", msg
        global SOCKET_IO_CONNECTIONS, ANALYTICS
        SOCKET_IO_CONNECTIONS.append(self.send_panel_data)
        # user_data = create_user_fingerprint(self.request)
        # ANALYTICS.user_connected(user_data)

    def on_close(self):
        print "web_server: socketio closed"
        global SOCKET_IO_CONNECTIONS
        SOCKET_IO_CONNECTIONS.remove(self.send_panel_data)


SocketIORouter = TornadioRouter(SocketIOUpdaterConnection)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    'debug': True,
    'socket_io_port': 9000,
}

application = tornado.web.Application([
    (r"/",                  LiveHandler),
    (r"/draw/",             DrawHandler),
    (r"/animate/",          AnimateHandler),
    (r"/text/",             TextHandler),
    (r"/meemoo/",           MeemooHandler),
    (r"/embed/",           EmbedHandler),

    (r"/a/press",               PanelPressedHandler),
    (r"/a/update",              PanelUpdateHandler),
    (r"/a/save-animation",      SaveAnimationHandler),
    (r"/a/play-animation",      PlayAnimationHandler),
    (r"/a/get-all-animations",  GetAllAnimationsHandler),
] + SocketIORouter.urls,
    **settings)

if __name__ == "__main__":
    import sys
    try:
        print "trying to connect via port 80"
        application.listen(80)
    except:
        print "... failed. Backing up to 8888"
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

    # Send one empty frame. This defines the panel so that other components
    # get frame information and can start running
    packet = DL_COMMUNICATOR.encode_partial_frame(0, 0, [0, 0, 0])
    DL_COMMUNICATOR.send(packet)

    ioloopy.start()
