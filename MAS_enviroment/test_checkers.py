#!/usr/bin/env python3
# encoding=utf-8

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

from MAS_Checkers import GameEnv

env = GameEnv()
env.reset()

temp = env.render_env()

i = 0
while True:
    temp = env.render_env()
    print('temp', temp[0,0,:])
    plt.imshow(temp)
    plt.show(block=False)
    plt.pause(0.1)
    plt.clf()
    action1 = np.random.randint(8)
    action2 = np.random.randint(8)
    if env.is_done():
        env.reset()
    r1, r2 = env.move(action1, action2)
    print(r1, r2)
