import time, sys
import gevent
from gevent import socket

from blip_receiver import DottedLandscapeCommunicator

# TODO: maybe separate to DottedLandscapePainter which would handle the 
# logic of drawing on the panel and fading out etc., animations, etc.

class DottedLandscapeServer(DottedLandscapeCommunicator):
    # panel_width = 8
    # panel_height = 8
    # channels = 3
    
    def __init__(self):
        self.host = None # Symbolic name meaning all available interfaces
        self.port = 2323
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket = None
        self.receivers = []
        self.__panel_data = None
        super(DottedLandscapeServer, self).__init__(self.prepare_panel)
        # self.define_panel(self.panel_width, self.panel_height, self.channels)

    
    def plot(self, x, y, color):
        p = (x % self.panel_width + y * self.panel_width) * 3
        
        
        #    self.__panel_data[p]     = max(0, min(self.__panel_data[p]     + color[0], 255))
        #    self.__panel_data[p + 1] = max(0, min(self.__panel_data[p + 1] + color[1], 255))
        #    self.__panel_data[p + 2] = max(0, min(self.__panel_data[p + 2] + color[2], 255))
        # otherwise, including with 0, 0, 0, we do absolute colors
        #else:
        self.__panel_data[p]     = color[0]
        self.__panel_data[p + 1] = color[1]
        self.__panel_data[p + 2] = color[2]
        self.__panel_changed = True
    
    
    def prepare_panel(self, w, h, c):
        # self.panel_width, self.panel_height, self.channels = w, h, c
        print "dl_server: prepare panel %sx%s:%s" % (w, h, c)
        self.__panel_data = [0 for i in xrange(self.panel_width * self.panel_height * self.channels)]

    
    def plot_all(self, color):
        i = 0
        while i < len(self.__panel_data):
            self.__panel_data[i]        = max(0, min(self.__panel_data[i]     + color[0], 255))
            self.__panel_data[i + 1]    = max(0, min(self.__panel_data[i + 1] + color[1], 255))
            c = max(0, min(self.__panel_data[i + 2] + color[2], 255))
            self.__panel_data[i + 2]    = c
            i += 3
        self.__panel_changed = True
    
    
    def plot_partial(self, data):
        x, y, r, g, b = data
        self.plot(x, y, (r, g, b))
        

    def plot_full(self, data):
        i = 0
        for v in data:
            # self.__panel_data[i] = max(0, min(self.__panel_data[i] + v, 255))
            # absolute coloring
            self.__panel_data[i] = v
            i += 1


    def listen_all(self):
        for res in socket.getaddrinfo(self.host, self.port, 
                                      socket.AF_UNSPEC, socket.SOCK_DGRAM, 
                                      0, socket.AI_PASSIVE):
            print "dl_server: listening to", res
            af, socktype, proto, canonname, sa = res
            try:
                self.receive_socket = socket.socket(af, socktype, proto)
            except socket.error, msg:
                self.receive_socket = None
                continue
            try:
                self.receive_socket.bind(sa)
            except socket.error, msg:
                self.receive_socket.close()
                self.receive_socket = None
                continue
            break
    
        if self.receive_socket is None:
            print 'dl_server: could not open socket'
            sys.exit(1)
    
    
    def add_new_receiver(self, payload_data):
        ip, port = payload_data[0], payload_data[1]
        if (ip, port) not in self.receivers:
            print "dl_server: new listener at (%s, %s)" % (ip, port)
            if self.__panel_data:
                packet = self.encode_full_frame(self.__panel_data)
                self.send_socket.sendto(packet, 0, (ip, port))
            self.receivers.append((ip, port))
    
    
    def notify_receivers(self):
        packet = self.encode_full_frame(self.__panel_data)
        for ip, port in self.receivers:
            print "notify receiver at", ip, port
            self.send_socket.sendto(packet, 0, (ip, port))
    
    
    def start(self):
        print "start"
        self.keep_on_doing_it = True
        self.listen_all()
        gevent.spawn(self.panel_fadeout)
        print "dl_server: entering main loop"
        while self.keep_on_doing_it:
            data = self.receive_socket.recv(0xfff)
            header, payload = self.decode(data)
            
            if header[0] == self.dl_MAGIC_NEW_CONNECTION:
                self.add_new_receiver(payload)
            
            elif header[0] == self.dl_MAGIC_FRAME_PARTIAL:
                if not self.__panel_data:
                    self.prepare_panel(header[2], header[1], header[3])
                self.plot_partial(payload)
                self.notify_receivers()
            
            elif header[0] == self.dl_MAGIC_FRAME_FULL or header[0] == self.blip_MAGIC_MCU_FRAME:
                if not self.__panel_data:
                    self.prepare_panel(header[2], header[1], header[3])
                self.plot_full(payload)
                self.notify_receivers()
            #print "header", header
            #print "payload", payload
            # self.panel_fadeout()
            gevent.sleep()
    
    
    def panel_fadeout(self):
        while self.keep_on_doing_it:
            i = 0
            if self.__panel_data:
                for v in self.__panel_data:
                    # self.__panel_data[i] *= 0.7
                    i += 1
            gevent.sleep(3)
    
    
    def get_panel_data(self):
        return self.__panel_data
    
          
    def quit(self):
        self.keep_on_doing_it = False
        
    
    def panel_data_to_ascii_graphics(self):
#        for i in xrange(self.panel_height * self.panel_width * 3):
#            print "|",
#            print   "%s:%s:%s" %    (str(self.__panel_data[i]).zfill(3), \
#                                    str(self.__panel_data[i]).zfill(3), \
#                                    str(self.__panel_data[i]).zfill(3)),
#            if i / 3. % self.panel_width == 0:
#                print "|"
        print self.__panel_data
    
    
    def send_test_packet(self, host, port):
        # plot a direct line through
        for i in xrange(0, self.panel_height):
            print "plot at", self.panel_width / 2, i
            self.plot(i, i, (255, 255, 0))
            
        self.panel_data_to_ascii_graphics()
        packet = self.encode_full_frame(self.__panel_data)
        self.send_socket.sendto(packet, 0, (host, port))


if __name__ == '__main__':
    dls = DottedLandscapeServer()
    dls.start()
    # dls.send_test_packet('127.0.0.1', 2324)
    