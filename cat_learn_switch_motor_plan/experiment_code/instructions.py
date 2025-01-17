from psychopy import visual, event
import os
import numpy as np


def draw_screen(win, im, advance_keys, regress_keys):

    im.draw()
    win.flip()

    k = event.waitKeys(keyList=advance_keys + regress_keys)

    if k[0] in advance_keys:
        kk = 1

    elif k[0] in regress_keys:
        kk = -1

    return kk


def give_instructions(win, cnd):

    instructions_dir = '../instructions/instructions_' + cnd + '/'

    im_list = []
    for f in os.listdir(instructions_dir):
        im_list.append(instructions_dir + f)

    im_list = np.sort(np.array(im_list))

    im = [
        visual.ImageStim(win,
                         image=x,
                         size=(2, 2),
                         units='norm',
                         pos=(0.0, 0.0)) for x in im_list
    ]

    # NOTE: Define the advance / regress key behaviour. `adk` and `rek` must
    # have exactly the same number of elements as `im`.
    adk = [['right']] * 8
    adk += [['v', 'b']] + [['right']] + [['v', 'b']] + [['right']]
    adk += [['right']] * 5
    adk += [['c', 'n']] + [['right']] + [['c', 'n']]
    adk += [['right']] * 4
    adk += [['v', 'b']] + [['right']]
    adk += [['c', 'n']] + [['right']]
    adk += [['c', 'n']] + [['right']]
    adk += [['v', 'b']] + [['right']]
    adk += [['c', 'n']] + [['right']]
    adk += [['v', 'b']] + [['right']]
    adk += [['right']] * 2

    rek = [['left']] * 8
    rek += [[None]] * 5
    rek += [['left']] * 4
    rek += [[None]] * 5
    rek += [['left']] * 2
    rek += [[None]] * 14

    i = 0
    while i != len(im):
        k = draw_screen(win, im[i], adk[i], rek[i])
        i = i + k
        if i < 0:
            i = 0

def give_debrief(win, cnd):

    instructions_dir = '../instructions/debrief/'

    im_list = []
    for f in os.listdir(instructions_dir):
        im_list.append(instructions_dir + f)

    im_list = np.sort(np.array(im_list))

    im = [
        visual.ImageStim(win,
                         image=x,
                         size=(2, 2),
                         units='norm',
                         pos=(0.0, 0.0)) for x in im_list
    ]

    # NOTE: Define the advance / regress key behaviour. `adk` and `rek` must
    # have exactly the same number of elements as `im`.
    adk = [['right']] * 4
    
    rek = [[None]]
    rek = [['left']] * 2
    rek += [[None]]

    i = 0
    while i != len(im):
        k = draw_screen(win, im[i], adk[i], rek[i])
        i = i + k
        if i < 0:
            i = 0
