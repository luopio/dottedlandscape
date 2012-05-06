import tornado, redis

class AnimationStorage(object):
    prefix = 'dl_2_'
    directory_key = 'dl_animation_directory'

    def __init__(self):
        self.r = redis.Redis()


    def save_animation_to_db(self, key, val):
        json = tornado.escape.json_encode(val)
        key = self.prefix+key, json
        self.r.set(key)
        self.r.sadd(self.directory_key, key)


    def load_animation_from_db(self, key):
        return tornado.escape.json_decode(self.r.get(self.prefix+key))


    def get_all_animations(self):
        anims = []
        # TODO: should not use keys.. more so because of this quick hax
        for k in self.r.smembers(self.directory_key):
            j = tornado.escape.json_decode(self.r.get(k))
            middle_frame = j['frames'][len(j['frames']) / 2]
            anims.append((j['title'], j['author'], middle_frame))
        return anims

