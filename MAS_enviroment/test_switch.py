#!/usr/bin/env python3
# encoding=utf-8

import matplotlib.pyplot as plt
import numpy as np

from MAS_Switch import GameEnv

env = GameEnv()
env.reset(block_level=2)

temp = env.render_env()

i = 0
r1 = 0
r2 = 0
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
        print(env.agent1.is_pickup(), env.agent2.is_pickup())
    if env.check_env_done():
        env.reset(block_level=np.random.randint(0, 3))
