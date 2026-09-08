import time
from audioop import reverse

import pygame
import random
import math

from numpy.ma.core import nomask
import numpy as np

WIDTH, HEIGHT = 1000, 600
FPS = 10
RES = (WIDTH, HEIGHT)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = [0, 255, 0]
GREY = (136, 136, 136)
VEL = 5
ant_size = 5
MAP = np.zeros((int(WIDTH / VEL), int(HEIGHT / VEL)), dtype=bool)
ants = []

Mouse = pygame.mouse

# TODO antler kendi kuyruguna takılmalı mı?
# Index out of bounds gidiyo
# rastgele hız olunca kuyruklar yavaş kalıyo


def av(v1, v2):
    result = []
    if isinstance(v2, int):
        for i in range(len(v1)):
            result.append(v1[i] + v2)
    else:
        for i in range(len(v1)):
            result.append(v1[i] + v2[i])
    return result


def am(v1, s):
    result = []
    for i in range(len(v1)):
        result.append(v1[i] * s)

    return result


def update_color(col, update_vec):
    new_color = av(col, update_vec)
    for c in range(len(new_color)):
        if new_color[c] < 0:
            new_color[c] = 0
        elif new_color[c] > 255:
            new_color[c] = 255

    return new_color


def getIndex(pos):
    ind_x = int(pos[0] / VEL)
    ind_y = int(pos[1] / VEL)
    x_limit = WIDTH/VEL
    y_limit = HEIGHT/VEL
    if ind_x >= x_limit:
        ind_x = int(x_limit-1)
    elif ind_x < 0:
        ind_x = 0
    if ind_y >= y_limit:
        ind_y = int(y_limit-1)
    elif ind_y < 0:
        ind_y = 0

    return [ind_x, ind_y]



def check_pos(index):
    return MAP[index[0], index[1]]


def update_on_map(old, new):
    MAP[old[0], old[1]] = 0
    MAP[new[0], new[1]] = 1


class Ant:

    def __init__(self):
        self.body = []
        head = self.createBody(ant_size, [random.randint(0, int((WIDTH/VEL)-1))*VEL,
                                          random.randint(0, int((HEIGHT/VEL)-1))*VEL])
        print(int(head.x), int(head.y))
        self.body.append(head)
        self.vel = VEL

        # remove comment if you want tail
        """for i in range(3):
            tail = self.createBody(ant_size, [0, 0])
            self.body.append(tail)"""

    def createBody(self, size, coords):
        map_position = getIndex(coords)
        MAP[map_position[0], map_position[1]] = 1
        return pygame.Rect(coords[0], coords[1], size, size)


    def check_move(self, move):

        ind = getIndex(move)
        # position is occupied if it returns True
        return check_pos(ind)


    def move(self, move_vector=[0, 0]):
        head = self.body[0]
        coords = [head.x, head.y]

        move = [coords[0] + move_vector[0] * self.vel,
                    coords[1] + move_vector[1] * self.vel]

        """if random.choice([True, False, False]):
            x_entropy = random.randint(-2, 2)
            y_entropy = random.randint(-2, 2)
            move[0] += x_entropy
            move[1] += y_entropy"""


        if move_vector != [0, 0] and not (self.check_move(move)):
            length = len(self.body)

            previous = coords
            head.x = move[0]
            head.y = move[1]

            
            for i in range(1, length):
                # the coords of the tail of the ant = coords of the head
                # so it looks more natural
                
                current = self.body[i]
                temp = [current.x, current.y]

                current.x = previous[0]
                current.y = previous[1]
                previous = [temp[0], temp[1]]

            ind_old = getIndex(previous)
            ind_new = getIndex([move[0], move[1]])

            update_on_map(ind_old, ind_new)
        # time.sleep(0.1) bunu elleme kardeş


class Simulation:

    def __init__(self, resolution, agents):
        self.resolution = resolution
        self.agents = agents
        # resolution is a tuple that contains the width and height of the program
        # We divide by velocity to divide the map in equal blocks
        self.map = np.zeros((resolution[0] / VEL, resolution[1] / VEL))



def follow_mouse(ants, reverse):
    coeff = 1
    if reverse:
        coeff = -1
    for ant in ants:
        head = ant.body[0]
        ant_coords = [head.x, head.y]
        distance_to_mouse = distance_vector(ant_coords, Mouse.get_pos())
        move = normalize(distance_to_mouse)
        move = am(move, coeff)
        ant.move(move)



def distance_vector(v1, v2):
    return [v2[0] - v1[0], v2[1] - v1[1]]


def normalize(v):

    x = v[0]
    y = v[1]

    vector_length = math.sqrt(x**2 + y**2)
    if vector_length == 0: return [0, 0]
    norm_x = x / vector_length
    norm_y = y / vector_length

    # return [round(norm_x), round(norm_y)]
    return [norm_x, norm_y]


def draw_window(WIN, ants, color, background):
    WIN.fill(background)
    for ant in ants:
        for part in ant.body:
            pygame.draw.rect(WIN, (color[0], color[1], color[2]), part)

    pygame.display.update()


def main():
    clock = pygame.time.Clock()
    run = True

    COLOR = GREEN
    BACKGROUND = BLACK

    v_change = [0.5, 0.8, 1]
    v2 = [0, 0.2, 0]
    v3 = [0, 0, 0.3]

    v = [0, 0, 0]

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ants?")

    for i in range(20):
        ant = Ant()
        ants.append(ant)

    pause = False
    reverse = False
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:
                    pause = not pause
                elif event.key == pygame.K_r:
                    reverse = not reverse


        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_UP]:
            ant.move([0, -1])
        elif keys_pressed[pygame.K_DOWN]:
            ant.move([0, 1])
        elif keys_pressed[pygame.K_RIGHT]:
            ant.move([1, 0])
        elif keys_pressed[pygame.K_LEFT]:
            ant.move([-1, 0])


        if not pause:
            follow_mouse(ants, reverse)

        for color in range(len(v)):
            if COLOR[color] == 0:
                v[color] = v_change[color]
            elif COLOR[color] == 255:
                v[color] = (-1) * v_change[color]

        COLOR = update_color(COLOR, v)

        draw_window(WIN, ants, COLOR, BACKGROUND)
    pygame.quit()


if __name__ == "__main__":
    main()