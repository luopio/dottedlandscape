import sys
import gevent
from gevent import socket

from dl.communicator import DottedLandscapeCommunicator

# TODO: maybe separate to DottedLandscapePainter which would handle the 
# logic of drawing on the panel and fading out etc., animations, etc.

class DottedLandscapeServer(DottedLandscapeCommunicator):

    def __init__(self, additive_coloring=False, fade_out=False):
        self.host = None # Symbolic name meaning all available interfaces
        self.port = 2323
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket = None
        self.receivers = []
        # receivers that only wish to hear plot-by-plot updates, not whole frames
        self.partial_receivers = None
        self.additive_coloring = additive_coloring
        self.fade_out = fade_out
        self.__fade_out_counters = None
        self.__panel_data = None
        super(DottedLandscapeServer, self).__init__(self.prepare_panel)
        # self.define_panel(self.panel_width, self.panel_height, self.channels)

    
    def plot(self, x, y, color):
        p = (x % self.panel_width + y * self.panel_width) * 3
        if self.additive_coloring:
            self.__panel_data[p]     = max(0, min(self.__panel_data[p]     + color[0], 255))
            self.__panel_data[p + 1] = max(0, min(self.__panel_data[p + 1] + color[1], 255))
            self.__panel_data[p + 2] = max(0, min(self.__panel_data[p + 2] + color[2], 255))
        # otherwise, including with 0, 0, 0, we do absolute colors
        else:
            self.__panel_data[p]     = color[0]
            self.__panel_data[p + 1] = color[1]
            self.__panel_data[p + 2] = color[2]
        self.__panel_changed = True
    
    
    def prepare_panel(self, w, h, c):
        print "dl_server: prepare panel %sx%s:%s" % (w, h, c)
        self.__panel_data = [0 for _ in xrange(self.panel_width * self.panel_height * self.channels)]
        self.__fade_out_counters = [0 for _ in xrange(self.panel_width * self.panel_height)]


    def plot_partial(self, data):
        x, y, r, g, b = data
        self.__fade_out_counters[x + y * self.panel_width] = 40
        # also increase all the others.. make the whole picture live longer
        self.__fade_out_counters = map(lambda x: (x > 100 and x + 5) or (x > 0 and x + 25) or 0, self.__fade_out_counters)
        self.plot(x, y, (r, g, b))
        

    def plot_full(self, data):
        i = 0
        while i < len(data):
            # absolute coloring
            # if data[i] + data[i + 1] + data[i + 2] > 0:
            self.__panel_data[i] = data[i]
            self.__panel_data[i + 1] = data[i + 1]
            self.__panel_data[i + 2] = data[i + 2]
            if data[i] + data[i + 1] + data[i + 2] > 0:
                self.__fade_out_counters[int(i / 3)] = 30
            i += 3
        self.__panel_changed = True
    

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
    
    
    def add_new_receiver(self, payload_data, accept_partial_frames=False):
        ip, port = payload_data[0], payload_data[1]
        if (ip, port, accept_partial_frames) not in self.receivers:
            print "dl_server: new listener at (%s, %s). Accepts partial frames? %s" % (ip, port, accept_partial_frames)
            self.receivers.append((ip, port, accept_partial_frames))
        if self.__panel_data:
            packet = self.encode_full_frame(self.__panel_data)
            self.send_socket.sendto(packet, 0, (ip, port))

    
    def notify_receivers(self, is_partial_frame=False):
        packet = self.encode_full_frame(self.__panel_data)
        for ip, port, accepts_partial_frames in self.receivers:
            # partial frame listeners get the change in more compact form
            if not( is_partial_frame and accepts_partial_frames ):
                self.send_socket.sendto(packet, 0, (ip, port))
    
    
    def notify_partial_receivers(self, data):
        ''' Some receivers are only interested in x,y and color - not full frame data.
            This notifies all of those. Full frame updates are not sent via this way. '''
        x, y, r, g, b = data
        packet = self.encode_partial_frame(x, y, (r, g, b))
        for ip, port, accepts_partial_frames in self.receivers:
            if accepts_partial_frames:
                print "notify partial receiver at", ip, port
                self.send_socket.sendto(packet, 0, (ip, port))


    def start(self):
        print "start"
        self.keep_on_doing_it = True
        self.listen_all()
        
        # start the fade out routine
        if self.fade_out:
            print "dl_server: activating fadeout"
            gevent.spawn(self.panel_fadeout)
        
        print "dl_server: entering main loop"
        while self.keep_on_doing_it:
            data = self.receive_socket.recv(0xfff)
            header, payload = self.decode(data)
            
            if header[0] == self.dl_MAGIC_NEW_CONNECTION:
                self.add_new_receiver(payload)
            
            elif header[0] == self.dl_MAGIC_NEW_CONNECTION_PARTIAL:
                self.add_new_receiver(payload, accept_partial_frames=True)

            elif header[0] == self.dl_MAGIC_FRAME_PARTIAL:
                if not self.__panel_data:
                    self.prepare_panel(header[2], header[1], header[3])
                self.plot_partial(payload)
                self.notify_receivers(is_partial_frame=True)
                self.notify_partial_receivers(payload)
            
            elif header[0] == self.dl_MAGIC_FRAME_FULL or header[0] == self.blip_MAGIC_MCU_FRAME:
                if not self.__panel_data:
                    self.prepare_panel(header[2], header[1], header[3])
                self.plot_full(payload)
                self.notify_receivers()
            
            gevent.sleep()
    
    
    def panel_fadeout(self):
        ''' Runs on its own and fades out the panel. '''
        while self.keep_on_doing_it:
            i = 0
            at_least_one_has_gone_dark = False
            if self.__fade_out_counters and sum(self.__fade_out_counters):

                for i, v in enumerate(self.__fade_out_counters):
                    if self.__fade_out_counters[i] > 0:
                        self.__fade_out_counters[i] -= 1

                        if self.__fade_out_counters[i] <= 0:
                            self.__fade_out_counters[i] = 0
                            self.__panel_data[i * 3 + 0] = 0
                            self.__panel_data[i * 3 + 1] = 0
                            self.__panel_data[i * 3 + 2] = 0
                            at_least_one_has_gone_dark = True

                if at_least_one_has_gone_dark:
                    self.notify_receivers()

            gevent.sleep(0.1)
    
    
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
    dls = DottedLandscapeServer(fade_out=True, additive_coloring=False)
    dls.start()
    # dls.send_test_packet('127.0.0.1', 2324)
    