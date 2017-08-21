#!/usr/bin/env python3
# encoding=utf-8

import numpy as np
import scipy.misc


class AgentObj:
    def __init__(self, coordinates, type, name, direction=0, mark=0, hidden=0, pickup=0):
        self.x = coordinates[0]
        self.y = coordinates[1]
        #0: r, 1: g, 3: b
        self.type = type
        self.name = name
        self.hidden = hidden

        # 0: right, 1:top 2: left. 3: bottom
        self.direction = direction
        self.mark = mark
        # 0: without, 1: take
        self.pickup = pickup

    def is_pickup(self):
        return self.pickup

    def pick_up(self):
        self.pickup = 1

    def drop_down(self):
        self.pickup = 0

    def is_hidden(self):
        return self.hidden > 0

    def add_mark(self, agent_hidden):
        self.mark += 1
        if self.mark >= 2:
            self.mark = 0
            self.hidden = agent_hidden
        return self.mark

    def sub_hidden(self):
        self.hidden -= 1
        self.hidden = 0 if self.hidden <=0 else self.hidden
        return self.hidden

    def turn_left(self, **kwargs):
        self.direction = (self.direction + 1) % 4
        return self.direction

    def turn_right(self, **kwargs):
        self.direction = (self.direction - 1 + 4) % 4
        return self.direction

    def move_forward_delta(self):
        if self.direction == 0:
            delta_x, delta_y = 1, 0
        elif self.direction == 1:
            delta_x, delta_y = 0, -1
        elif self.direction == 2:
            delta_x, delta_y = -1, 0
        elif self.direction == 3:
            delta_x, delta_y = 0, 1
        else:
            assert self.direction in range(4), 'wrong direction'

        return delta_x, delta_y

    def move_left_delta(self):
        if self.direction == 0:
            delta_x, delta_y = 0, -1
        elif self.direction == 1:
            delta_x, delta_y = -1, 0
        elif self.direction == 2:
            delta_x, delta_y = 0, 1
        elif self.direction == 3:
            delta_x, delta_y = 1, 0
        else:
            assert self.direction in range(4), 'wrong direction'

        return delta_x, delta_y

    @staticmethod
    def legal_coordinates(coordinates, env):
        return env.size_x - 1 >= coordinates[0] >=0 and env.size_y - 1 >= coordinates[1] >= 0 \
               and coordinates not in env.block

    def move_forward(self, env):
        delta_x, delta_y = self.move_forward_delta()

        self.x = self.x + delta_x if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.x
        self.y = self.y + delta_y if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.y
        return self.x, self.y

    def move_backward(self, env):
        forward_delta_x, forward_delta_y = self.move_forward_delta()
        delta_x, delta_y = -forward_delta_x, -forward_delta_y

        self.x = self.x + delta_x if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.x
        self.y = self.y + delta_y if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.y
        return self.x, self.y

    def move_left(self, env):
        delta_x, delta_y = self.move_left_delta()

        self.x = self.x + delta_x if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.x
        self.y = self.y + delta_y if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.y
        return self.x, self.y

    def move_right(self, env):
        left_delta_x, left_delta_y = self.move_left_delta()
        delta_x, delta_y = -left_delta_x, -left_delta_y

        self.x = self.x + delta_x if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.x
        self.y = self.y + delta_y if self.legal_coordinates([self.x + delta_x, self.y + delta_y], env) else self.y
        return self.x, self.y

    def stay(self, **kwargs):
        pass

    def beam(self, env):#env_x_size, env_y_size):
        env_x_size = env.size_x
        env_y_size = env.size_y
        if self.direction == 0:
            beam_set = [(i + 1, self.y) for i in range(self.x, env_x_size - 1)]
        elif self.direction == 1:
            beam_set = [(self.x, i - 1) for i in range(self.y, 0, -1)]
        elif self.direction == 2:
            beam_set = [(i - 1, self.y) for i in range(self.x, 0, -1)]
        elif self.direction == 3:
            beam_set = [(self.x, i + 1) for i in range(self.y, env_y_size - 1)]
        else:
            assert self.direction in range(4), 'wrong direction'
        return beam_set


class PointObj:
    def __init__(self, coordinates, type, reward, hidden=0):
        # type: 1 is pick-up, 3 is drop
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.type = type
        self.reward = reward
        self.hidden = hidden

    def do(self, agent, env):
        reward = 0
        if self.type == 1:
            agent.pick_up()
            self.hidden = 1
            reward = self.reward
        elif agent.is_pickup():
            agent.drop_down()
            env.show_start()
            reward = self.reward
        return reward

    def is_hidden(self):
        return self.hidden > 0

    def show(self):
        self.hidden = 0


class GameEnv:
    def __init__(self, widht=34, hight=7):
        self.size_x = widht
        self.size_y = hight
        self.objects = []

        # 0: forward, 1: backward, 2: left, 3: right
        # 4: trun lelf, 5:turn right, 6: beam, 7: stay
        self.action_num = 8

        self.reset()

    def reset(self):
        self.agent1 = AgentObj(coordinates=(4, 2), type=2, name='agent1', direction=2)
        self.agent2 = AgentObj(coordinates=(4, 4), type=0, name='agent2', direction=2)
        self.agent1_actions = [self.agent1.move_forward, self.agent1.move_backward, self.agent1.move_left, self.agent1.move_right,
                               self.agent1.turn_left, self.agent1.turn_right, self.agent1.beam, self.agent1.stay]
        self.agent2_actions = [self.agent2.move_forward, self.agent2.move_backward, self.agent2.move_left, self.agent2.move_right,
                               self.agent2.turn_left, self.agent2.turn_right, self.agent2.beam, self.agent2.stay]
        self.agent1_beam_set = []
        self.agent2_beam_set = []

        block = []
        for x in range(7, 27):
            for y in range(0, 3):
                block.append([x, y])
                block.append([x, y + 4])

        self.block = tuple(block)

        self.start_point = PointObj(coordinates=(30, 3), type=1, reward=3)
        self.end_point = PointObj(coordinates=(3, 3), type=3, reward=5)

        self.point_list = [self.start_point, self.end_point]

    def move(self, agent1_action, agent2_action):
        assert agent1_action in range(8), 'agent1 take wrong action'
        assert agent2_action in range(8), 'agent2 take wrong action'

        agent1_old_x, agent1_old_y = self.agent1.x, self.agent1.y
        agent2_old_x, agent2_old_y = self.agent2.x, self.agent2.y

        self.agent1.sub_hidden()
        self.agent2.sub_hidden()

        agent1_action_return = self.agent1_actions[agent1_action](env=self)
        self.agent1_beam_set = [] if agent1_action != 6 else agent1_action_return

        agent2_action_return = self.agent2_actions[agent2_action](env=self)#_x_size=self.size_x, env_y_size=self.size_y)
        self.agent2_beam_set = [] if agent2_action != 6 else agent2_action_return

        if self.agent1.x == self.agent2.x and self.agent1.y == self.agent2.y:
            self.agent1.x, self.agent1.y = agent1_old_x, agent1_old_y
            self.agent2.x, self.agent2.y = agent2_old_x, agent2_old_y

        agent1_reward = 0
        agent2_reward = 0

        for point in self.point_list:
            if point.x == self.agent1.x and point.y == self.agent1.y and not point.is_hidden():
                agent1_reward = point.do(agent=self.agent1, env=self)
            elif point.x == self.agent2.x and point.y == self.agent2.y and not point.is_hidden():
                agent2_reward = point.do(agent=self.agent2, env=self)

        return agent1_reward, agent2_reward

    def show_start(self):
        self.start_point.show()

    def contribute_metrix(self):
        a = np.ones([self.size_y + 2, self.size_x + 2, 3])
        a[1:-1, 1:-1, :] = 0
        a[:, 0, 0] = 136 / 255
        a[:, 0, 1] = 138 / 255
        a[:, 0, 2] = 135 / 255

        a[:, self.size_x + 1, 0] = 136 / 255
        a[:, self.size_x + 1, 1] = 138 / 255
        a[:, self.size_x + 1, 2] = 135 / 255

        a[0, :, 0] = 136 / 255
        a[0, :, 1] = 138 / 255
        a[0, :, 2] = 135 / 255

        a[self.size_y + 1, :, 0] = 136 / 255
        a[self.size_y + 1, :, 1] = 138 / 255
        a[self.size_y + 1, :, 2] = 135 / 255

        for block in self.block:
            a[block[1] + 1, block[0] + 1, 0] = 0.53 #136 / 255
            a[block[1] + 1, block[0] + 1, 1] = 0.54 #138 / 255
            a[block[1] + 1, block[0] + 1, 2] = 0.53 #135 / 255

        for x, y in self.agent1_beam_set:
            a[y + 1, x + 1, 0] = 0.5
            a[y + 1, x + 1, 1] = 0.5
            a[y + 1, x + 1, 2] = 0.5
        for x, y in self.agent2_beam_set:
            a[y + 1, x + 1, 0] = 0.5
            a[y + 1, x + 1, 1] = 0.5
            a[y + 1, x + 1, 2] = 0.5

        a[self.end_point.y + 1, self.end_point.x + 1, 0] = 12 / 255
        a[self.end_point.y + 1, self.end_point.x + 1, 1] = 255 / 255
        a[self.end_point.y + 1, self.end_point.x + 1, 2] = 134 / 255

        if not self.start_point.is_hidden():
            a[self.start_point.y + 1, self.start_point.x + 1, 0] = 117 / 255
            a[self.start_point.y + 1, self.start_point.x + 1, 1] = 255 / 255
            a[self.start_point.y + 1, self.start_point.x + 1, 2] = 0

        for i in range(3):
            if not self.agent1.is_hidden():
                delta_x, delta_y = self.agent1.move_forward_delta()
                a[self.agent1.y + 1 + delta_y, self.agent1.x + 1 + delta_x, i] = 40 / 255
            if not self.agent2.is_hidden():
                delta_x, delta_y = self.agent2.move_forward_delta()
                a[self.agent2.y + 1 + delta_y, self.agent2.x + 1 + delta_x, i] = 40 / 255
            if self.agent1.is_pickup():
                a[self.agent1.y + 1, self.agent1.x + 1, i] = 1 if i == self.agent1.type else 0.5
            else:
                a[self.agent1.y + 1, self.agent1.x + 1, i] = 1 if i == self.agent1.type else 0
            if self.agent2.is_pickup():
                a[self.agent2.y + 1, self.agent2.x + 1, i] = 1 if i == self.agent2.type else 0.5
            else:
                a[self.agent2.y + 1, self.agent2.x + 1, i] = 1 if i == self.agent2.type else 0

        return a

    def render_env(self):
        a = self.contribute_metrix()

        b = scipy.misc.imresize(a[:, :, 0], [10 * self.size_y, 10 * self.size_x, 1], interp='nearest')
        c = scipy.misc.imresize(a[:, :, 1], [10 * self.size_y, 10 * self.size_x, 1], interp='nearest')
        d = scipy.misc.imresize(a[:, :, 2], [10 * self.size_y, 10 * self.size_x, 1], interp='nearest')

        a = np.stack([b, c, d], axis=2)
        return a

    def train_render(self):
        a = self.contribute_metrix()

        b = scipy.misc.imresize(a[:, :, 0], [84, 84, 1], interp='nearest')
        c = scipy.misc.imresize(a[:, :, 1], [84, 84, 1], interp='nearest')
        d = scipy.misc.imresize(a[:, :, 2], [84, 84, 1], interp='nearest')

        a = np.stack([b, c, d], axis=2)
        return a
