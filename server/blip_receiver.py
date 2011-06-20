import socket, struct, sys

import threading
# magic, w, h, channels, max_val
s = None


class BlipReceiver(threading.Thread):
    ''' Receives messages from a Blip-protocol using source via UDP '''
    
    def __init__(self, *args, **kwargs):
        self.host = None # Symbolic name meaning all available interfaces
        self.port = 2323
        self.header_struct = struct.Struct('!IHHHH') 
        self.data_struct = None # constructed on first contact, when we know size
        self._observers = []
        self.keep_on_truckin = True
        super(BlipReceiver, self).__init__(*args, **kwargs)
    
    
    def add_observer(self, obs):
        print "adding observer %s" % len(self._observers)
        self._observers.append(obs)
        
            
    def listen_all(self):
        for res in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC,
                                      socket.SOCK_DGRAM, 0, socket.AI_PASSIVE):
            print "listening to", res
            af, socktype, proto, canonname, sa = res
            try:
                self.s = socket.socket(af, socktype, proto)
                print af, socktype, proto
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
        print "ready to receive data"
        while self.keep_on_truckin:
            try:
                data = self.s.recv(0xfff) # 4095 bytes
                if not data: break
                header_data = self.header_struct.unpack(data[:12])
                if not self.data_struct:
                    self.data_struct = struct.Struct('B' * header_data[1] * header_data[2] * header_data[3])
                payload_data = self.data_struct.unpack(data[12:])
                for o in self._observers:
                    o(header_data, payload_data)
                    
            except socket.timeout:
                if self.data_struct: # we already received data, so this is the end
                    break
        
        print "receiver done. closing connection"
        self.s.close()


if __name__ == '__main__':
    d = BlipReceiver()
    def listen(h, p): print h; print p
    d.add_observer(listen)
    d.run()