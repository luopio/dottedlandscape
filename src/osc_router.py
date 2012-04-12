#!/bin/python
import time
import liblo

from dl.communicator import DottedLandscapeCommunicator

class OscRouter(object):
    ser = None
    
    def __init__(self, target_port=10000):
        # send all messages to port 1234 on the local machine
        try:
            self.__target = liblo.Address(target_port)
        except liblo.AddressError, err:
            print str(err)
            sys.exit()
                 
    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None
    
    
    def send(self, full_frame):
        liblo.send(self.__target, "/dl/frame", *full_frame)
    
    
    def send_partial(self, x, y, r, g, b):
        liblo.send(self.__target, "/dl/plot", x, y, r, g, b)
        

if __name__ == '__main__':
    # foo = 'a'
    # while foo != 'q':
    #     foo = raw_input('> ')
    #     sc.write([int(foo) for i in xrange(0, 8)])
    # sc.close()
    
    
    osc = OscRouter()
    dlc = DottedLandscapeCommunicator()
    dlc.connect('127.0.0.1', 2323, accept_partial_frames=True)
    
    done = False 
    while not done:
        
        # get any incoming data from the DL server
        data = dlc.check_for_data()
        if not data:
            continue
        headers, payload = data 
        
        if headers[0] == dlc.dl_MAGIC_FRAME_PARTIAL:
            print "Osc got a partial frame!", len(payload)
            osc.send_partial(*payload)
        
        elif headers[0] == dlc.dl_MAGIC_FRAME_FULL:
            print "Osc got a full frame!", len(payload)
            osc.send(payload)
            
        else:
            time.sleep(0.05)
                
    dlc.disconnect()
