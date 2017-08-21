#!/usr/bin/env python3
# encoding=utf-8

import matplotlib.pyplot as plt
import numpy as np

from MAS_Fetch import GameEnv

env = GameEnv()
env.reset()

temp = env.render_env()

i = 0
show = False
t = 0
while True:
    if show:
        temp = env.render_env()
        plt.imshow(temp)
        plt.show(block=False)
        plt.pause(0.01)
        plt.clf()
        t += 1
        if not t % 10:
            show = False
    action1 = np.random.randint(8)
    action2 = np.random.randint(8)
    i += 1
    r1, r2 = env.move(action1, action2)
    if r1 or r2:
        show = True
        print(i, 'r1:', r1, 'r2:', r2)
