import time
import redis

class Analytics(object):

    redis_prefix            = 'dl_analytics:'
    animation_played_prefix = 'animation_played:'
    text_messaged_prefix    = 'text_messaged:'
    user_connected_prefix   = 'user_connected'
    user_text_messaged_prefix       = 'user_text_messaged:'
    user_played_animation_prefix    = 'user_played_animation:'

    def __init__(self):
        self.conn = redis.Redis()


    def animation_played(self, animation_data, user_fingerprint):
        animation_data['t'] = time.time()
        self.increment(self.redis_prefix+self.animation_played_prefix+animation_data['name'])
        self.add(self.redis_prefix+self.user_played_animation_prefix+user_fingerprint, animation_data)


    def user_connected(self, user_data):
        user_data['t'] = time.time()
        self.add(self.redis_prefix+self.user_connected_prefix, user_data)


    def text_messaged(self, msg_data, user_fingerprint):
        msg_data['t'] = time.time()
        self.add(self.redis_prefix+self.user_text_messaged_prefix+user_fingerprint, msg_data)


    def generate_report(self):
        pass


    def increment(self, key, amount=1):
        ''' Key happened once or more times. '''
        pass


    def add(self, key, value):
        ''' Occurence of key with value happened. '''
        pass