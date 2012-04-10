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
        # send a all values as integers
        liblo.send(self.__target, "/dl/frame", *full_frame)
            

if __name__ == '__main__':
    # foo = 'a'
    # while foo != 'q':
    #     foo = raw_input('> ')
    #     sc.write([int(foo) for i in xrange(0, 8)])
    # sc.close()
    
    
    osc = OscRouter()
    dlc = DottedLandscapeCommunicator()
    dlc.connect('127.0.0.1', 2323)
    
    done = False 
    while not done:
        # get any incoming data from the DL server
        data = dlc.check_for_data()
        if data:     # new frame received!
            print "Osc got a frame!", len(data)
            osc.send(data)
            
        else:
            time.sleep(0.05)
                
    
    dlc.disconnect()
