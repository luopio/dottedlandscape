import alphabet

class TextWriter(object):

    def __init__(self, w, h, c):
        self.panel_width = w
        self.panel_height = h
        self.channels = c
        self.alphabet_letter_width = 8 # restriction here..


    def write(self, letter, frame, frame_width, offset=0, color=[255, 0, 0]):
        if letter in alphabet.ALPHABET_BITS:
            bits = alphabet.ALPHABET_BITS[letter]
            for i, b in enumerate(bits):
                if b:
                    pixel_index = offset + i % self.alphabet_letter_width + i / self.alphabet_letter_width * frame_width
                    for ci in xrange(0, self.channels):
                        frame[pixel_index * self.channels + ci] = color[ci]


#            for i in xrange(offset, len(data_structure) / self.channels):
#                for ii, c in enumerate(color):
#                    data_structure[i * self.channels + ii] = bits[i] * int(c)
        # return frame


    def get_all_frames(self, message, color=[255, 0, 0]):
        # FIXME: hardcoded here. move into a generator to save mem?
        frames = []
        message = message.lower()
        if len(message) > 20: message = message[:17] + "..."
        message += " "

        # build one big image that contains all the letters
        big_image = [0] *self.panel_width * self.panel_height * self.channels * len(message)
        for i, l in enumerate(message):
            self.write(l, big_image, self.panel_width * len(message), offset=self.panel_width * i, color=color)


#        for i in xrange(0, len(big_image), 3):
#            if big_image[i]: print "*",
#            else: print ".",
#            if i % 8 == 0:
#                print


        # big image is ready, now return small frames from it, one per x-pixel
        offset = 0
        print "size of big image", len(big_image)
        for i in xrange(0, self.panel_width * (len(message) - 1)):
            frame = [0] * self.panel_width * self.panel_height * self.channels
            print "frame with offset", offset
            for yi in xrange(0, self.panel_height):
                for xi in xrange(0, self.panel_width):
                    pixel_index = (offset + xi) + yi * self.panel_width * len(message)
                    frame_pixel_index = xi + yi * self.panel_width
                    print "pi", pixel_index, "fpi", frame_pixel_index
                    for ci in xrange(0, self.channels):
                        frame[frame_pixel_index * self.channels + ci] = big_image[pixel_index * self.channels + ci]
            frames.append((frame, 0.1))
            offset += 1
        # create one frame for each letter in the message
#        for l in message:
#            data_buffer = self.write(l, [0 for i in xrange(8*8*3)], color=color)
#            frames.append((data_buffer, 0.9)) # frame duration constant...
        return frames    



if __name__=='__main__':
    import dl_server
    import gevent
    
    t = TextWriter()
    dls = dl_server.DottedLandscapeServer()
    dls.define_panel(8,8,3)
    gevent.spawn(dls.start)
    # dls.start()
    gevent.sleep()
    
    print "dls started"
    do_not_quit = True
    
    while do_not_quit:
        l = raw_input('write letter > ')
        t.write(l, dls.get_panel_data())
        dls.notify_receivers()
        gevent.sleep()
        
    dls.quit()
    
                