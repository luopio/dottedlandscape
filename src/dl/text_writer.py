import alphabet

class TextWriter(object):

    def __init__(self, w, h, c=3):
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


    def get_all_frames(self, message, color=[255, 0, 0]):
        message = message.lower()
        if len(message) > 40: message = message[:37] + "..."
        message = " " + message + " "

        # build one big image that contains all the letters
        big_image = [0] * (self.panel_width + 1) * self.panel_height * self.channels * len(message)
        for i, l in enumerate(message):
            self.write(l, big_image, (self.panel_width + 1) * len(message), offset=(self.panel_width + 1) * i, color=color)

        # big image is ready, now return small frames from it, one per x-pixel
        offset = 0
        frame = [0] * self.panel_width * self.panel_height * self.channels
        for i in xrange(0, (self.panel_width + 1) * len(message) - self.panel_width):
            for yi in xrange(0, self.panel_height):
                for xi in xrange(0, self.panel_width):
                    pixel_index = (offset + xi) + yi * (self.panel_width + 1) * len(message)
                    frame_pixel_index = xi + yi * self.panel_width
                    for ci in xrange(0, self.channels):
                        frame[frame_pixel_index * self.channels + ci] = big_image[pixel_index * self.channels + ci]
            # frames.append((frame, 0.1))
            yield (frame, 0.15)
            offset += 1



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
    
                
