#!/bin/python
import serial, struct, time

from dl.communicator import DottedLandscapeCommunicator

class SerialConnection(object):
    ''' The SerialConnection class sends data through the serial port to the
        Arduino. The size of the panel is restricted here because we pack each
        row in a channel into one byte (8 bits, on/off). This sets the column
        amount to 8. Changing this should not be too hard if the electronics
        accept different forms in the future. '''

    ser = None
    
    def __init__(self, rows, channels):
        # Arduino is little endian
        self.full_frame_struct = struct.Struct('<B' + 'B' * rows * channels) # one byte per row, per channel


    def connect(self):
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 115200)
        except:
            self.ser = serial.Serial('/dev/ttyACM1', 115200)


    def write(self, data, checksum):
        self.ser.write(self.full_frame_struct.pack(checksum, *data))
        
    
    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            
            

if __name__ == '__main__':

    dlc = DottedLandscapeCommunicator()
    dlc.connect('127.0.0.1', 2323)

    print "waiting for panel size information.."
    while dlc.panel_height == None:
        dlc.check_for_data()
        time.sleep(0.1)

    print "received panel data (%s x %s x %s)" % (dlc.panel_width, dlc.panel_height, dlc.channels)
    sc = SerialConnection(dlc.panel_height, dlc.channels)
    sc.connect()

    done = False
    while not done:
        # get any incoming data from the DL server
        _, data = dlc.check_for_data()
        if data:     # new frame received!
            print "serial connection received a frame of length %s!" % len(data)
            
            # data format r, g, b, r, g, b, r, g, b, r, g, b, r, g, b, etc.. 
            i = 0
            frame = []
            for y in xrange(0, 8):
                red_value = 0
                green_value = 0
                blue_value = 0
                for x in xrange(0, 8):
                    i = ((7 - x) * 8 + (y)) * 3
                    if data[i]:
                        red_value += 1 << x
                    if data[i + 1]:
                        green_value += 1 << x
                    if data[i + 2]:
                        blue_value += 1 << x
                    
                # print bin(red_value)
                frame.append( red_value )
                frame.append( green_value )
                frame.append( blue_value )
                # x = (i / 3 % 8)
                # y = (i / 3 / 8)
            print "sent %s of data" % len(frame)
            checksum = 13
            sc.write(frame, checksum)
        else:
            # time.sleep(0.5)
            pass
                
    
    dlc.disconnect()
