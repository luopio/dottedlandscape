import threading, time
from text_writer import TextWriter

# TODO: global objects, ughh
TEXT_WRITER = None
# simple "lock" to ensure just one animation plays at a time
ANIMATION_LOCKED = False

class AnimationPlayer(object):

    def __init__(self, dlc):
        self.dlc = dlc
        global TEXT_WRITER
        TEXT_WRITER = TextWriter(dlc.panel_width, dlc.panel_height, dlc.channels)


    def play(self, frames):
        global ANIMATION_LOCKED
        if not ANIMATION_LOCKED:
            ANIMATION_LOCKED = True
            player_thread = PlayAnimationThread(self.dlc, frames)
            player_thread.start()


    def text(self, message, color):
        global ANIMATION_LOCKED
        if not ANIMATION_LOCKED:
            ANIMATION_LOCKED = True
            player_thread = PlayAnimationThread(self.dlc, None, message, color)
            player_thread.start()



class PlayAnimationThread(threading.Thread):

    def __init__(self, dlc, frames=None, message=None, color=None):
        self.frames = frames
        self.message = message
        self.color = color
        self.dlc = dlc
        super(PlayAnimationThread, self).__init__()


    def run(self):
        if self.frames:
            print "PlayAnimationThread: playing animation with %s frames." % len(self.frames)
            for frame in self.frames:
                p = self.dlc.encode_full_frame(frame[0])
                self.dlc.send(p)
                time.sleep(float(frame[1]))
        else:
            print "PlayAnimationThread: playing a message %s" % self.message
            for frame in TEXT_WRITER.get_all_frames(self.message, self.color):
                p = self.dlc.encode_full_frame(frame[0])
                self.dlc.send(p)
                time.sleep(float(frame[1]))

        global ANIMATION_LOCKED
        ANIMATION_LOCKED = False
        print "PlayAnimationThread: animation done."
