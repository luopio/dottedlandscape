import random
import time
from dl.communicator import DottedLandscapeCommunicator

def game_of_life(tbl, tbl_width, tbl_height):
    new_tbl = [0] * tbl_width * tbl_height
    alive = False
    for i, e in enumerate(tbl):
        nn = number_of_neighbours(i, tbl, tbl_width, tbl_height)
        new_tbl[i] = e
        if e == 1:
            if nn > 3 or nn < 2:
                new_tbl[i] = 0
        else:
            if nn == 3:
                new_tbl[i] = 1
                alive = True
    return alive, new_tbl


def number_of_neighbours(i, tbl, tbl_width, tbl_height):
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


def shuffle_table(dlc):
    print "shuffle"
    tbl = [0] * dlc.panel_width * dlc.panel_height
    for i, e in enumerate(tbl):
        if random.random() < 0.3: tbl[i] = 1
    return tbl


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

if __name__ == '__main__':
    dlc = DottedLandscapeCommunicator()
    dlc.connect('127.0.0.1', 2323)
    last_packet_received = 0
    done = False
    tbl = None
    color = [0, 255, 0]
    idle_time = 3
    last_frame = None
    amount_of_frames_since_refresh = 0
    while not done:

        # get any incoming data from the DL server
        data = dlc.check_for_data()
        if not data:
            now = time.time()
            if now - last_packet_received > idle_time:
                if tbl:
                    print "game of life!"
                    alive, tbl = game_of_life(tbl, dlc.panel_width, dlc.panel_height)
                    frame = []
                    for i in tbl:
                        frame.append(color[0] * i)
                        frame.append(color[1] * i)
                        frame.append(color[2] * i)
                    last_frame = frame
                    dlc.send(dlc.encode_full_frame(frame))
                    amount_of_frames_since_refresh += 1
                    if not alive or amount_of_frames_since_refresh > 50:
                        tbl = shuffle_table(dlc)
                        color = get_random_color()
                        amount_of_frames_since_refresh = 0
        else:
            headers, payload = data
            s = sum(payload)
            if last_frame:
                ss = sum(last_frame)
            else:
                ss = -1
            # quick checksum to see if the frame changed or was blank
            if s == ss or s == 0:
                print "it was ours!"
            else:
                print "activity!"
                print "lastframe", last_frame
                print "payload: ", payload
                print
                tbl = None # refresh next time

                last_packet_received = time.time()
            if not tbl:
                tbl = shuffle_table(dlc)
                color = get_random_color()
                amount_of_frames_since_refresh = 0

        time.sleep(0.3)

    dlc.disconnect()

