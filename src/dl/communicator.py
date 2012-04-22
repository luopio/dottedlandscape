import socket, struct, sys

import threading
# magic, w, h, channels, max_val
s = None

class DottedLandscapeCommunicator(object):
    ''' Understands the dl protocol, which is an extension to the Blinkenlights project's
        blip-protocol (i.e. this class can be used to talk with blip-protocol hosts as well).
    '''
    
    # original full frame from Blinkenlights project. Matches dl_MAGIC_FRAME_FULL
    blip_MAGIC_MCU_FRAME = 0x23542666
    # register for updates on panel changes, will receive full frames
    dl_MAGIC_NEW_CONNECTION = 0x11AEEE
    # register for new updates to only partial frames (dot by dot)
    dl_MAGIC_NEW_CONNECTION_PARTIAL = 0x11AEFF
    # partial frame with just changed dots
    dl_MAGIC_FRAME_PARTIAL = 0x114545
    # a full frame
    dl_MAGIC_FRAME_FULL = 0x23542666
    
    def __init__(self, panel_changed_callback=None):
        self.header_struct = struct.Struct('!IHHHH') 
        self.partial_frame_data_struct = struct.Struct('!IIHHH') # x, y, r, g, b 
        self.new_conn_data_struct = struct.Struct('!HHHHI') # ip.ip.ip.ip, port
        self.full_frame_data_struct = None # constructed on first contact, when we know size
        self.panel_changed_cb = panel_changed_callback
        self.panel_width, self.panel_height = 0, 0
        self._cached_payload = None


    def define_panel(self, width, height, channels):
        ''' called by the server to create the data struct '''
        print "DLCOMM >>> panel defined as %s x %s w/ %s channels" % (width, height, channels)
        self.full_frame_data_struct = struct.Struct('B' * width * height * channels)
        self.panel_width, self.panel_height, self.channels = width, height, channels
        if self.panel_changed_cb:
            self.panel_changed_cb(width, height, channels)
    
    
    def decode(self, data):
        try:
            header_data = self.header_struct.unpack(data[:12])
        except struct.error:
            print "DLCOMM >>> faulty header in decode len=%s" % len(data)
            return None, None
        
        # this is a blip package or dl full frame (identical for now)
        if header_data[0] == self.blip_MAGIC_MCU_FRAME or header_data[0] == self.dl_MAGIC_FRAME_FULL:
            # print "full frame decoded: ", header_data[1:3]
            if self.panel_width != header_data[2] or self.panel_height != header_data[1]:
                self.define_panel(header_data[2], header_data[1], header_data[3])
            payload_data = self.full_frame_data_struct.unpack(data[12:])
        
        elif header_data[0] == self.dl_MAGIC_FRAME_PARTIAL:
            # print "partial frame decoded: ", header_data[1:3]
            if self.panel_width != header_data[2] or self.panel_height != header_data[1]:
                self.define_panel(header_data[2], header_data[1], header_data[3])
            payload_data = self.partial_frame_data_struct.unpack(data[12:])
        
        elif header_data[0] == self.dl_MAGIC_NEW_CONNECTION:
            d = self.new_conn_data_struct.unpack(data[12:])
            payload_data = ('%s.%s.%s.%s' % d[:4], d[4]) 

        elif header_data[0] == self.dl_MAGIC_NEW_CONNECTION_PARTIAL:
            d = self.new_conn_data_struct.unpack(data[12:])
            payload_data = ('%s.%s.%s.%s' % d[:4], d[4])

        return header_data, payload_data
    
    
    def encode_handshake(self, ip, port):
        ip0, ip1, ip2, ip3 = [int(i) for i in ip.split('.')]
        data = self.header_struct.pack(self.dl_MAGIC_NEW_CONNECTION, 0, 0, 0, 0) + \
               self.new_conn_data_struct.pack(ip0, ip1, ip2, ip3, port)
        return data
    
    
    def encode_partial_update_handshake(self, ip, port):
        ip0, ip1, ip2, ip3 = [int(i) for i in ip.split('.')]
        data = self.header_struct.pack(self.dl_MAGIC_NEW_CONNECTION_PARTIAL, 0, 0, 0, 0) + \
               self.new_conn_data_struct.pack(ip0, ip1, ip2, ip3, port)
        return data


    def encode_full_frame(self, payload_data):
        data = self.header_struct.pack(self.dl_MAGIC_FRAME_FULL, self.panel_height, self.panel_width, self.channels, 255)
        data += self.full_frame_data_struct.pack(*payload_data)
        return data
    
    
    def encode_partial_frame(self, x, y, color):
        return self.header_struct.pack(self.dl_MAGIC_FRAME_PARTIAL, self.panel_height, self.panel_width, self.channels, 255) +\
               self.partial_frame_data_struct.pack(int(x), int(y), int(color[0]), int(color[1]), int(color[2])) 

    
    def send(self, packet):
        ''' send change notification to the server '''
        self.send_socket.sendto(packet, 0, (self.server_host, self.server_port))
        
    
    def check_for_data(self):
        try:
            data = self.receive_socket.recv(4096)
            headers, payload = self.decode(data)
            if not headers:
                return None
            
            if headers[0] in (self.blip_MAGIC_MCU_FRAME, self.dl_MAGIC_FRAME_FULL, self.dl_MAGIC_FRAME_PARTIAL):
                # print "DLCOMM >> valid frame found"
                self._cached_payload = payload
                return headers, payload
        except socket.error:
            pass # print "DLCOMM >> nothing to receive?"
        return None
        

    def connect(self, host, port, accept_partial_frames=False):
        print "DLCOMM >> connect to", host, ":", port
        self.server_host = host
        self.server_port = port
        receive_port = port + 1
        retries = 0
        connected = False
        # look for a good port
        while not connected:
            receive_port += 1
            self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                self.receive_socket.bind(("0.0.0.0", receive_port))
                connected = True
            except socket.error:
                retries += 1
                if retries > 100:
                    print "DLCOMM >> failed to initialize connection"
                    return None #failed        
        self.receive_socket.setblocking(0) # non-blocking
        
        # handshake!
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if accept_partial_frames:
            packet = self.encode_partial_update_handshake(host, receive_port)
            self.send_socket.sendto(packet, 0, (host, port))
        else:
            packet = self.encode_handshake(host, receive_port)
            self.send_socket.sendto(packet, 0, (host, port))
            

    
    def disconnect(self):
        self.send_socket.close()
        self.receive_socket.close()



class BlipReceiver(threading.Thread):
    ''' Receives, unpacks and delivers messages from a Blip-protocol using host via UDP.
    
        To receive the data in a listener, call add_observer(f).
        Function 'f' will then be called with two parameters:
        header_data -    tuple: (magic_number, anim_width, anim_height, amount_of_channels, max_value)
        video_data  -    tuple of values with length anim_width * anim_height * amount_of_channels
        every time a packet arrives. Blip receiver will run in it's own thread until you call stop(), 
        or it receives a quit command via the network. 
    '''
    
    def __init__(self, *args, **kwargs):
        self.host = None # Symbolic name meaning all available interfaces
        self.port = 2323
        self.header_struct = struct.Struct('!IHHHH') 
        self.data_struct = None # constructed on first contact, when we know size
        self._observers = []
        self.keep_on_truckin = True
        self._receive_amount = 0xfff # 4095 bytes default
        super(BlipReceiver, self).__init__(*args, **kwargs)
    
    
    def stop(self):
        self.keep_on_truckin = False
        self.join()
    
    
    def add_observer(self, obs):
        print "BlipReceiver: adding observer %s" % len(self._observers)
        self._observers.append(obs)
        
            
    def listen_all(self):
        for res in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC,
                                      socket.SOCK_DGRAM, 0, socket.AI_PASSIVE):
            print "BlipReceiver: listening to", res
            af, socktype, proto, canonname, sa = res
            try:
                self.s = socket.socket(af, socktype, proto)
            except socket.error, msg:
                self.s = None
                continue
            try:
                self.s.bind(sa)
            except socket.error, msg:
                self.s.close()
                self.s = None
                continue
            break
    
        if self.s is None:
            print 'could not open socket'
            sys.exit(1)

    
    def run(self):
        self.listen_all()
        self.s.settimeout(1.0)
        print "BlipReceiver: ready to receive data"
        while self.keep_on_truckin:
            try:
                data = self.s.recv(self._receive_amount) 
                if not data: break
                header_data = self.header_struct.unpack(data[:12])
                if not self.data_struct:
                    print "BlipReceiver: new data with w, h, c", header_data[1], header_data[2], header_data[3]
                    self.data_struct = struct.Struct('B' * header_data[1] * header_data[2] * header_data[3])
                    if (self.data_struct.size + self.header_struct.size) > self._receive_amount:
                        data += self.s.recv((self.data_struct.size + self.header_struct.size) - self._receive_amount)
                        self._receive_amount = self.data_struct.size + self.header_struct.size
                payload_data = self.data_struct.unpack(data[12:])
                for o in self._observers:
                    o(header_data, payload_data)
                    
            except socket.timeout:
                if self.data_struct: # we already received data, so this is the end
                    # get ready for the next flick
                    self.data_struct = None
                pass 
        
        print "BlipReceiver: I'm done. closing connection"
        self.s.close()


if __name__ == '__main__':
    d = BlipReceiver()
    def listen(h, p): print h; print p
    d.add_observer(listen)
    d.run()
