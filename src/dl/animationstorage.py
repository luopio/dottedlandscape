import tornado, redis, json

class AnimationStorage(object):
    prefix = 'dl_2_'

    def __init__(self):
        self.r = redis.Redis()


    def save_animation_to_db(self, key, val):
        json = tornado.escape.json_encode(val)
        self.r.set(self.prefix+key, json)


    def load_animation_from_db(self, key):
        return tornado.escape.json_decode(self.r.get(self.prefix+key))


    def get_all_animations(self):
        anims = []
        # TODO: should not use keys.. more so because of this quick hax
        for k in self.r.keys(self.prefix+'*').split(self.prefix):
            if not k: continue
            j = json.loads(self.r.get(self.prefix+k))
            # j = tornado.escape.json_decode(self.r.get(k))
            anims.append((j['title'], j['author'], j['frames'][0]))
        return anims

