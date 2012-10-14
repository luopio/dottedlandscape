import random
import time
from dl.communicator import DottedLandscapeCommunicator
from dl.text_writer import TextWriter

# singleton for message writing
TEXT_WRITER = None

def message(tbl_width, tbl_height, vars):
    global TEXT_WRITER
    if not TEXT_WRITER:
        TEXT_WRITER = TextWriter(tbl_width, tbl_height)
        msgs = ['Cartes Flux 2012', 'DottedLandscape.net', 'Reclaim your public space']
        msg = random.choice(msgs)
        vars['frames'] = TEXT_WRITER.get_all_frames(msg, vars['color'])
        vars['current_index'] = 0
        vars['frame_duration'] = 0.05
        print "play message", msg

    try:
        vars['cur_frame'] = vars['frames'].next()[0]
    except StopIteration:
        del(TEXT_WRITER)
        TEXT_WRITER = None
        return vars['cur_frame'], False, vars

    return vars['cur_frame'], True, vars



def knight_rider(tbl_width, tbl_height, vars):
    if not vars.has_key('offset'):
        vars['offset'] = int(random.random() * tbl_width)
        vars['speed'] = 1
        vars['frame_duration'] = 0.10
        vars['total_frames'] = int(30 + 60 * random.random())
        vars['inverted'] = True if random.random() > 0.5 else False

    if vars['inverted']:
        frame = vars['color'] * tbl_width * tbl_height
        c = (0, 0, 0)
    else:
        frame = [0] * tbl_width * tbl_height * 3
        c = vars['color']

    for i in xrange(0, tbl_height):
        frame[(i * tbl_width + vars['offset']) * 3]     = c[0]
        frame[(i * tbl_width + vars['offset']) * 3 + 1] = c[1]
        frame[(i * tbl_width + vars['offset']) * 3 + 2] = c[2]


    vars['offset'] += vars['speed']
    if vars['offset'] > tbl_width - 1:
        vars['speed'] = -1
        vars['offset'] = tbl_width - 1
        # change colors on bounce
        vars['color'] = get_random_color()
    elif vars['offset'] < 0:
        vars['speed'] = 1
        vars['offset'] = 0
        # change colors on bounce
        vars['color'] = get_random_color()

    if vars['frame_counter'] > vars['total_frames']:
        return frame, False, vars

    return frame, True, vars


def random_colors(tbl_width, tbl_height, vars):
    if not vars.has_key('total_frames'):
        vars['total_frames'] = int(30 + 20 * random.random())
        vars['prev_frame'] = [0] * tbl_width * tbl_height * 3 
        vars['frame_duration'] = 0.10

    if vars['color']:
        # for i in xrange(0, tbl_width * tbl_height):
        #     frame += (vars['color'] if random.random() < 0.4 else [0, 0, 0]) # TODO: channels hardcoded here
        pass
    else:
        # for i in xrange(0, tbl_width * tbl_height * 3): # TODO: channels hardcoded here
        #     frame.append( 0 if random.random() < 0.8 else 255 )
        for i in xrange(0, int(random.random() * 3)):
            random_index = int(random.random() * (tbl_width * tbl_height - 1) * 3)
            vars['prev_frame'][random_index] = 0 if random.random() < 0.3 else 255     
            vars['prev_frame'][random_index + 1] = 0 if random.random() < 0.3 else 255     
            vars['prev_frame'][random_index + 2] = 0 if random.random() < 0.3 else 255     

    if vars['frame_counter'] > vars['total_frames']:
        return vars['prev_frame'], False, vars

    return vars['prev_frame'], True, vars


def game_of_life(tbl_width, tbl_height, vars):
    if not vars.has_key('table'):
        print "shuffle table"
        tbl = [0] * dlc.panel_width * dlc.panel_height
        for i, e in enumerate(tbl):
            if random.random() < 0.34: tbl[i] = 1
        vars['table'] = tbl
        vars['frame_duration'] = 0.3

    new_tbl = [0] * tbl_width * tbl_height
    alive = False
    for i, e in enumerate(vars['table']):
        nn = _gof_number_of_neighbours(i, vars['table'], tbl_width, tbl_height)
        new_tbl[i] = e
        if e == 1:
            if nn > 3 or nn < 2:
                new_tbl[i] = 0
        else:
            if nn == 3:
                new_tbl[i] = 1
                alive = True
    frame = []
    for i in new_tbl:
        frame.append(vars['color'][0] * i)
        frame.append(vars['color'][1] * i)
        frame.append(vars['color'][2] * i)
    vars['table'] = new_tbl

    if vars['frame_counter'] > 50:
        alive = False

    return frame, alive, vars


def _gof_number_of_neighbours(i, tbl, tbl_width, tbl_height):
    x = i % tbl_width
    y = i / tbl_width
    nn = 0
    if y > 0:
        if tbl[x + (y - 1) * tbl_width]:
            nn += 1
        if x > 0:
            if tbl[x - 1 + (y - 1) * tbl_width]:
                nn += 1
        if tbl_width > (x + 1):
            if tbl[x + 1 + (y - 1) * tbl_width]:
                nn += 1
    if x > 0:
        if tbl[x - 1 + y * tbl_width]:
            nn += 1
    if tbl_width > (x + 1):
        if tbl[x + 1 + y * tbl_width]:
            nn += 1
    if tbl_height > (y + 1):
        if tbl[x + (y + 1) * tbl_width]:
            nn += 1
        if x > 0:
            if tbl[x - 1 + (y + 1) * tbl_width]:
                nn += 1
        if tbl_width > (x + 1):
            if tbl[x + 1 + (y + 1) * tbl_width]:
                nn += 1
    return nn


def get_random_color():
    color = [0, 0, 0]
    if random.random() > 0.5:
        color[0] = 255
    if random.random() > 0.5:
        color[1] = 255
    if random.random() > 0.5:
        color[2] = 255
    if sum(color) == 0:
        color[1] = 255
    elif sum(color) == 255 * 3:
        color[0] = 0
    return color


def select_random_visualization():
    visualization = random.choice([knight_rider, random_colors, game_of_life,
                                   random_colors, game_of_life, game_of_life,
                                   message, message])
    print "picked random viz:", visualization.__name__
    vars = {'frame_duration': 0.35, 'frame_counter': 0}
    vars['color'] = get_random_color()
    if visualization == random_colors: #  and sum(vars['color']) > 255:
        vars['color'] = None

    return visualization, vars


if __name__ == '__main__':

    dlc = DottedLandscapeCommunicator()
    dlc.connect('127.0.0.1', 2323)
    last_packet_received = 0
    done = False
    idle_time = 15
    last_frame = None
    now = time.time()
    vars = {'frame_duration': 0.5, 'frame_counter': 0} # will be updated by the visualization algorithms
    visualization, vars = select_random_visualization()

    while not done:
        # get any incoming data from the DL server
        headers, payload = dlc.check_for_data()

        # panel is up, but there is nothing happening
        if not payload and dlc.panel_width:

            now = time.time()

            if now - last_packet_received > idle_time:
                frame, alive, vars = visualization(dlc.panel_width, dlc.panel_height, vars)
                last_frame = frame
                dlc.send(dlc.encode_full_frame(frame))
                vars['frame_counter'] += 1

                # new random visualization
                if not alive:
                    visualization, vars = select_random_visualization()

        # it seems the panel is playing something
        elif payload:
            s = sum(payload)
            if last_frame:
                ss = sum(last_frame)
            else:
                ss = -1
            # quick checksum to see if the frame changed or was blank
            if s == ss or s == 0:
                pass
            else:
                last_packet_received = time.time()

        time.sleep(vars['frame_duration'])

    dlc.disconnect()

