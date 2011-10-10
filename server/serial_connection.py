#!/bin/python
import serial, struct



class SerialConnection(object):
    ser = None
    channels = 1 # TODO: move to general settings
    
    def __init__(self):
        # arduino is little endian
        # self.full_frame_struct = struct.Struct('<' + 'B' * 8 * self.channels) # one byte per row, per channel 
        self.full_frame_struct = struct.Struct('<' + 'B') 
    
    def connect(self):
        self.ser = serial.Serial('/dev/ttyUSB1', 4800)
        
        # self.ser.setTimeout(0.8)
        # line = self.ser.read(58)
        # print "msg >", line
    

    def write(self, data):
        self.ser.write(self.full_frame_struct.pack(data))
        #self.ser.write(data)
        print "return:", self.ser.read()
        
    
    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            
            

if __name__ == '__main__':
    sc = SerialConnection()
    sc.connect()
    print "sending serial data"
    foo = 'a'
    while foo != 'q':
        foo = raw_input('> ')
        # sc.write([int(foo) for i in xrange(0, 8)])
        sc.write(int(foo))
    sc.close()
    