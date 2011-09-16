import os, time, threading
import tornado.ioloop
import tornado.web
import tornado.httpserver
import redis

from blip_receiver import DottedLandscapeCommunicator
    
DL_COMMUNICATOR = DottedLandscapeCommunicator()
# define the panel here
DL_COMMUNICATOR.define_panel(8, 8, 3)
WEB_CLIENTS = []


class LiveHandler(tornado.web.RequestHandler):
    def get(self):
        anims = get_all_animations()
        self.render("templates/index.html", saved_animations=anims)

class AnimateHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/animate.html")

class TextHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/text.html")
    

class PanelPressedHandler(tornado.web.RequestHandler):
    def post(self):
        args = self.request.arguments
        x = int(args['x'][0])
        y = int(args['y'][0])
        c = args['c[]']
        #print "pressed at", x, y, 
        #print "color", args['c[]'][0]
        print "panel_pressed", x, y, c
        packet = DL_COMMUNICATOR.encode_partial_frame(x, y, c)
        DL_COMMUNICATOR.send(packet)
        self.set_header("Content-Type", "application/json")
        self.write('ok')
        
     
class PanelUpdateHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        WEB_CLIENTS.append(self.async_callback(self.on_panel_updated))
        self.set_header("Content-Type", "application/json")
        print ">>>> got async request for update on %s" % time.time()
        
    def on_panel_updated(self, data):
        if self.request.connection.stream.closed():
            return
        print "<<<< finishing async request"
        self.finish(tornado.escape.json_encode(data))
    

def notify_clients_on_panel_change(fd, events):
    data = DL_COMMUNICATOR.check_for_data()
    if data:
        global WEB_CLIENTS
        for w in WEB_CLIENTS:
            print "notify client %s!" % w
            w(data)
        WEB_CLIENTS = []


class SaveAnimationHandler(tornado.web.RequestHandler):
    def post(self):
        args = self.request.arguments
        speed = int(args['speed'][0])
        channels = int(args['channels'][0])
        name = args['title'][0]
        author = args['author'][0]
        
        # decode the frames from the sucky tornado variable handling
        counter = 0
        frames = []
        while args.has_key('data[%s][]' % counter):
            fr = args['data[%s][]' % counter]
            all_int_fr = []
            for f in fr:
                all_int_fr.append(int(f))
            print "save frame - adding frame %s of len %s" % (counter, len(all_int_fr))
            frames.append(all_int_fr)
            counter += 1
        
        frame_save_structure = {'speed': speed, 'channels': channels, 
                                'title': name, 'author': author,
                                'frames': frames}
        print "animation save: ", speed, channels, name, author
        save_animation_to_db(name, frame_save_structure)
        self.set_header("Content-Type", "application/json")
        self.write('saved as %s' % name)


class PlayAnimationHandler(tornado.web.RequestHandler):
    def get(self):
        args = self.request.arguments
        name = args['title'][0]
        a = load_animation_from_db(name)
        if a:
            pt = PlayAnimationThread()
            pt.speed = a['speed']
            pt.frames = a['frames']
            pt.start()
            

class PlayAnimationThread(threading.Thread):
    frames = []
    speed = 0
    def run(self):
        for frame in self.frames:
            print "PLAY FRAME THREAD WITH LEN %s " % len(frame)
            p = DL_COMMUNICATOR.encode_full_frame(frame)
            DL_COMMUNICATOR.send(p)
            time.sleep(self.speed / 1000.)


def save_animation_to_db(key, val):
    prefix = 'dl_'
    json = tornado.escape.json_encode(val)
    r = redis.Redis()
    r.set(prefix+key, json)


def load_animation_from_db(key):
    prefix = 'dl_'
    r = redis.Redis()
    return tornado.escape.json_decode(r.get(prefix+key))
    

def get_all_animations():
    r = redis.Redis()    
    prefix = 'dl_'
    anims = []
    for k in r.keys(prefix+'*'):
        j = tornado.escape.json_decode(r.get(k))
        anims.append((j['title'], j['author'], j['frames'][0]))
    return anims

    
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    'debug': True,
}

application = tornado.web.Application([
    (r"/", LiveHandler),
    (r"/animate/", AnimateHandler),
    (r"/text/", TextHandler),
    (r"/a/press", PanelPressedHandler),
    (r"/a/update", PanelUpdateHandler),
    (r"/a/save-animation", SaveAnimationHandler),    
    (r"/a/play-animation", PlayAnimationHandler),    
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