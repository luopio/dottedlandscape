import tornado, redis, time

class AnimationStorage(object):
    prefix = 'dl_2_'
    directory_key = 'dl_animation_directory'

    def __init__(self):
        self.r = redis.Redis()


    def save_animation_to_db(self, key, val):
        json = tornado.escape.json_encode(val)
        key = self.prefix+key
        self.r.set(key, json)
        self.r.sadd(self.directory_key, key)


    def load_animation_from_db(self, key):
        print "loading", key
        val = self.r.get(self.prefix+key)
        val = tornado.escape.json_decode(val)
        if not val.has_key('play_count'):
            val['play_count'] = 0
            val['time'] = time.time()
            print "outdated animation value for", key, "updating"
            self.save_animation_to_db(key, val)
        else:
            val['play_count'] += 1
            self.save_animation_to_db(key, val)

        return val


    def get_all_animations(self):
        anims = []
        # TODO: should not use keys.. more so because of this quick hax
        for k in self.r.smembers(self.directory_key):
            j = tornado.escape.json_decode(self.r.get(k))
            middle_frame = j['frames'][len(j['frames']) / 2]
            anims.append({'title': j['title'],
                          'author': j['author'],
                          'time': j['time'],
                          'play_count': j['play_count'],
                          'frame': middle_frame})
        return anims

