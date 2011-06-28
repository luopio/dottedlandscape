import os
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        title = 'Frontpage'
        self.render("templates/index.html")

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    'debug': True,
}

application = tornado.web.Application([
    (r"/", MainHandler),
    #(r"/js/(\w+)",  tornado.web.StaticFileHandler, dict(path='static/js')),
    #(r"/img/(\w+)", tornado.web.StaticFileHandler, dict(path='static/img')),
    #(r"/css/(\w+)", tornado.web.StaticFileHandler, dict(path='static/css')),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()