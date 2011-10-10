#!/bin/python
import serial, struct, time

from blip_receiver import DottedLandscapeCommunicator

class SerialConnection(object):
    ser = None
    
    def __init__(self):
        # Arduino is little endian
        self.full_frame_struct = struct.Struct('<B' + 'B' * 8 * 3) # one byte per row, per channel 
    
    def connect(self):
        self.ser = serial.Serial('/dev/ttyUSB1', 19200)
        
        # self.ser.setTimeout(0.8)
        # line = self.ser.read(58)
        # print "msg >", line
    

    def write(self, data):
        self.ser.write(self.full_frame_struct.pack(255, *data))
        
    
    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            
            

if __name__ == '__main__':
    # foo = 'a'
    # while foo != 'q':
    #     foo = raw_input('> ')
    #     sc.write([int(foo) for i in xrange(0, 8)])
    # sc.close()
    
    
    sc = SerialConnection()
    sc.connect()
    dlc = DottedLandscapeCommunicator()
    dlc.connect('127.0.0.1', 2323)
    

    done = False 
    while done == False:
        # get any incoming data from the DL server
        data = dlc.check_for_data()
        if data:     # new frame received!
            print "frame!", len(data)
            
            # data format r, g, b, r, g, b, r, g, b, r, g, b, r, g, b, etc.. 
            i = 0
            frame = []
            while i < 8 * 8 * 3:
                red_value = 0
                green_value = 0
                blue_value = 0
                for u in xrange(0, 8):
                    if data[i]:
                        red_value += 1 << u
                    i += 1
                    if data[i]:
                        green_value += 1 << u
                    i += 1
                    if data[i]:
                        blue_value += 1 << u
                    i += 1
                    
                print bin(red_value)
                frame.append( red_value )
                frame.append( green_value )
                frame.append( blue_value )
                # x = (i / 3 % 8)
                # y = (i / 3 / 8)
            print "sent %s of data" % len(frame)
            sc.write(frame)
        else:
            time.sleep(0.5)
                
    
    dlc.disconnect()
