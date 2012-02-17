import alphabet

# how to draw?
# option 1: draw first letter in middle, second in start, moving first (playwwords)
#            => fade out after time
# option 2: make letters move all the time

class TextWriter(object):
    
    channels = 3
    
    def update(self):
        pass
    
    def write(self, letter, data_structure, offset=0, active_channel_index=0):
        if letter in alphabet.ALPHABET_BITS:
            bits = alphabet.ALPHABET_BITS[letter]
            for i in xrange(offset, len(data_structure) / self.channels):
                data_structure[i * self.channels + active_channel_index] = bits[i] * 255
        return data_structure
                
    def get_all_frames(self, message, active_channel_index=0):
        # FIXME: hardcoded here. move into a generator to save mem?
        frames = []
        message = message.lower()
        for l in message:
            data_buffer = self.write(l, [0 for i in xrange(8*8*3)], active_channel_index=active_channel_index)
            frames.append((data_buffer, 0.9)) # frame duration constant...
        return frames    
                
if __name__=='__main__':
    # this is not the way to go IRL
    # - panel only now notifies on change, changes are accepted only
    #   via network (nice, clean model)
    # too many gevent.sleeps/spawns everywhere... ok for testing..
    # bigger question: how to do animations? other processes affecting panel state?
    # maybe build a generic cmdline command sender for simple communicator testing
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
    
                