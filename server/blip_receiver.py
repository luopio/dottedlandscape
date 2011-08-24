import socket, struct, sys

import threading
# magic, w, h, channels, max_val
s = None

class DottedLandscapeCommunicator(object):
    ''' Understands the dl protocol, which is an extension to the Blinkenlights project's
        blip-protocol (i.e. this class can be used to talk with blip-protocol hosts as well '''
    
    blip_MAGIC_MCU_FRAME = 0x23542666
    dl_MAGIC_NEW_CONNECTION = 0x11AEEE
    dl_MAGIC_FRAME_PARTIAL = 0x114545 # partial frame with just changed dots
    dl_MAGIC_FRAME_FULL = 0x119898 # full frame received
    
    def __init__(self):
        self.header_struct = struct.Struct('!IHHHH') 
        self.partial_frame_data_struct = struct.Struct('!IIIHHH') # x, y, r, g, b 
        self.new_conn_data_struct = struct.Struct('!HHHHI') # ip.ip.ip.ip, port
        self.blip_data_struct = None # constructed on first contact, when we know size
    
    
    def define_panel(self, width, height, channels):
        ''' called by the server to create the data struct '''
        self.data_struct = struct.Struct('B' * width * height * channels)
    
    
    def decode(self, data):
        try:
            header_data = self.header_struct.unpack(data[:12])
        except struct.error:
            print "dl_server: faulty header in decode len=%s" % len(data)
            return None, None
        
        # this is a blip package or dl full frame (identical for now)
        if header_data[0] == self.blip_MAGIC_MCU_FRAME or header_data[0] == self.dl_MAGIC_FRAME_FULL:
            if not self.blip_data_struct:
                self.blip_data_struct = struct.Struct('B' * header_data[1] * header_data[2] * header_data[3])
                self.panel_height, self.panel_width = header_data[1], header_data[2] # reversed..
            payload_data = self.blip_data_struct.unpack(data[12:])
        
        elif header_data[0] == self.dl_MAGIC_FRAME_PARTIAL:
            if not self.panel_width:
                self.panel_height, self.panel_width = header_data[1], header_data[2] # reversed..                
            payload_data = self.partial_frame_data_struct.unpack(data[12:])
        
        elif header_data[0] == self.dl_MAGIC_NEW_CONNECTION:
            d = self.new_conn_data_struct.unpack(data[12:])
            payload_data = ('%s.%s.%s.%s' % d[:4], d[4]) 
            
        return header_data, payload_data
    
    
    def encode(self, header_data, payload_data):
        data = self.header_struct.pack(*header_data)
        data += self.data_struct.pack(*payload_data)
        return data
    
    
    def encode_add_receiver(self, ip, port):
        ip0, ip1, ip2, ip3 = [int(i) for i in ip.split('.')]
        data = self.header_struct.pack(self.dl_MAGIC_NEW_CONNECTION, 0, 0, 0, 0) + \
               self.new_conn_data_struct.pack(ip0, ip1, ip2, ip3, port)
        return data
    
    
    def encode_full_frame(self, data):
        # always 3 channels, max value 255
        return self.encode((self.dl_MAGIC_FRAME_FULL, self.panel_height, self.panel_width, 3, 255),
                           data)
    
    
    def encode_partial_frame(self, x, y, r, g, b):
        return self.encode((self.dl_MAGIC_FRAME_FULL, self.panel_height, self.panel_width, 3, 255),
                           (x, y, r, g, b))

    
    def send(self, packet):
        ''' send change notification to the server '''
        self.send_socket.send(packet)
        
    
    def on_socket_receive(self, fd, events):
        try:
            data = self.receive_socket.recv(4096)
            headers, payload = self.decode(data)
            if not headers:
                return None
            
            if headers[0] in (self.blip_MAGIC_MCU_FRAME, self.dl_MAGIC_FRAME_FULL, self.dl_MAGIC_FRAME_PARTIAL):
                print "DLCOMM >> valid frame found"
                return payload
        except socket.error:
            print "DLCOMM >> nothing to receive?"
        

    def connect(self, host, port):
        print "DLCOMM >> connect to", host, ":", port
        self.host = host
        self.port = port
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket.bind((self.host, self.port))
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket.bind((self.host, self.port + 1))
        self.receive_socket.setblocking(0) # non-blocking
        
    
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