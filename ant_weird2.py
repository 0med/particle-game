import time
from audioop import reverse

import pygame
import random
import math

from numpy.ma.core import nomask
import numpy as np

WIDTH, HEIGHT = 1000, 600
FPS = 20
RES = (WIDTH, HEIGHT)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = [0, 255, 0]
GREY = (136, 136, 136)

ant_color = GREEN
ant_color_change_vector = [0, 0, 0]
b_change = [0.3, 0.3, 0.3]
BACKGROUND = BLACK

VEL = 3
ant_size = 3
weird_radius = 50
MAP = np.zeros((int(WIDTH / VEL), int(HEIGHT / VEL)), dtype=bool)
ants = []

Mouse = pygame.mouse

# TODO antler kendi kuyruguna takılmalı mı?
# Index out of bounds gidiyo
# rastgele hız olunca kuyruklar yavaş kalıyo


def av(v1, v2):
    result = []
    if not isinstance(v2, list):
        for i in range(len(v1)):
            result.append(v1[i] + v2)
    else:
        for i in range(len(v1)):

            result.append(v1[i] + v2[i])
    return result


def mv(v1, s):
    result = []
    for i in range(len(v1)):
        result.append(v1[i] * s)

    return result


def vector_sum(v):
    sum = 0
    for i in range(len(v)):
        sum += v[i]
    return sum


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
    return False
    # return MAP[index[0], index[1]]


def update_on_map(old, new):
    MAP[old[0], old[1]] = 0
    MAP[new[0], new[1]] = 1


class Ant:

    def __init__(self):
        self.body = []
        head = self.createBody(ant_size, [random.randint(0, int((WIDTH/VEL)-1))*VEL,
                                          random.randint(0, int((HEIGHT/VEL)-1))*VEL])
        self.body.append(head)
        # self.vel = random.choice([VEL*2, VEL*2, VEL*2, VEL*2, VEL*3, VEL, VEL*2])
        self.vel = random.randint(VEL, 3*VEL)

        # they are particles with gravitation at this point
        self.acceleration = 0.1
        self.vel_vector = [0, 0]

        self.color = ant_color
        # remove comment if you want tail
        for i in range(3):
            tail = self.createBody(ant_size, [0, 0])
            self.body.append(tail)

    def createBody(self, size, coords):
        map_position = getIndex(coords)
        MAP[map_position[0], map_position[1]] = 1
        return pygame.Rect(coords[0], coords[1], size, size)


    def check_move(self, move):

        ind = getIndex(move)
        # position is occupied if it returns True
        return check_pos(ind)


    def set_velocity_vector(self, v):
        self.vel_vector[0] = v[0]
        self.vel_vector[1] = v[1]


    def update_velocity(self, move_vector=[0, 0]):
        acceleration_vector = mv(move_vector, self.acceleration)
        self.vel_vector = av(self.vel_vector, acceleration_vector)


    def update_tail(self, previous):
        # previous: coordinates of the head before it moved, so that we can make the other parts follow it
        length = len(self.body)
        for i in range(1, length):
            # the coords of the tail of the ant = coords of the head
            # so it looks more natural

            current = self.body[i]
            temp = [current.x, current.y]

            current.x = previous[0]
            current.y = previous[1]
            previous = [temp[0], temp[1]]

        # collision istiyosam alttakilerle ilgilenmem lazım
        # ind_old = getIndex(previous)
        # ind_new = getIndex([move[0], move[1]])
        # collision olsun dersen uncomment
        # update_on_map(ind_old, ind_new)


    def move_with_acceleration(self, vector):
        head = self.body[0]
        randomness = [0, 0]
        if random.choice([True, False, False]):
            x_entropy = random.randint(-2, 2)
            y_entropy = random.randint(-2, 2)
            randomness[0] += x_entropy
            randomness[1] += y_entropy

        previous = [head.x, head.y]

        head.x += self.vel_vector[0] + randomness[0] + vector[0]
        head.y += self.vel_vector[1] + randomness[1] + vector[1]

        self.update_tail(previous)


    def tp(self, vec):
        # same with move but takes in direct vectors instead of normalized vectors
        head = self.body[0]
        coords = [head.x, head.y]
        move = [0, 0]
        move[0] = head.x + vec[0]
        move[1] = head.y + vec[1]

        if random.choice([True, False, False]):
            x_entropy = random.randint(-2, 2)
            y_entropy = random.randint(-2, 2)
            move[0] += x_entropy
            move[1] += y_entropy

        if vec != [0, 0]:

            previous = coords
            head.x = move[0]
            head.y = move[1]

            self.update_tail(previous)


    def move(self, move_vector=[0, 0]):
        head = self.body[0]
        coords = [head.x, head.y]

        move = [coords[0] + move_vector[0] * self.vel,
                    coords[1] + move_vector[1] * self.vel]

        if random.choice([True, False, False]):
            x_entropy = random.randint(-2, 2)
            y_entropy = random.randint(-2, 2)
            move[0] += x_entropy
            move[1] += y_entropy


        if move_vector != [0, 0] and not (self.check_move(move)):

            previous = coords
            head.x = move[0]
            head.y = move[1]

            self.update_tail(previous)

        # time.sleep(0.1) bunu elleme kardeş


    def set_acceleration(self, v):
        self.acceleration = v


class Simulation:

    def __init__(self, resolution, agents):
        self.resolution = resolution
        self.agents = agents
        # resolution is a tuple that contains the width and height of the program
        # We divide by velocity to divide the map in equal blocks
        self.map = np.zeros((resolution[0] / VEL, resolution[1] / VEL))



def tp_particles(ants):
    for ant in ants:
        head = ant.body[0]
        mouse_pos = Mouse.get_pos()
        head.x = mouse_pos[0]
        head.y = mouse_pos[1]


def follow_mouse(ant, distance_to_mouse, distance, reverse, enable_physics, enable_weird, factor):

    coeff = 1
    if reverse:
        coeff = -1

    head = ant.body[0]
    ant_coords = [head.x, head.y]
    # distance_to_mouse = distance_vector(ant_coords, Mouse.get_pos())
    move = normalize(distance_to_mouse)
    move = mv(move, coeff)

    if enable_physics:
        vel_change = mv(move, factor)
        weird = [0, 0]
        if enable_weird and distance >= weird_radius:
            new_v2 = mv(distance_to_mouse, (-1))
            dot_prod = dot_product(new_v2, ant.vel_vector)
            sq_magnitude = distance ** 2
            if sq_magnitude == 0:
                sq_magnitude = 1
            temp = dot_prod / sq_magnitude

            temp = mv(new_v2, (-2) * temp)

            weird = av(vel_change, temp)

            ant.vel_vector = av(ant.vel_vector, weird)
            """ant.tp(move)"""
            # ant.move(move)
        ant.update_velocity(vel_change)
        ant.move_with_acceleration(weird)

    else:
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


def dot_product(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]


def color4vel(ant, factor, distance):
    # ismin aksine hıza göre renk değiştirme bu
    global ant_color, ant_color_change_vector, BACKGROUND, b_change
    v = [20, 10, 10]

    """factor = distance / 10
    print(factor)

    result_vector = (mv(v, factor * (-1)))"""

    vel = ant.vel_vector
    x = vel[0] ** 2
    y = vel[1] ** 2
    factor = math.sqrt(x + y)

    result_vector = (mv(v, factor))
    result_vector = av(result_vector, [10, 10, 10])


    result_color = update_color(BLACK, result_vector)
    ant.color = result_color
    return result_color


def manage_colors():
    global ant_color, ant_color_change_vector, BACKGROUND, b_change
    v_change = [0.5, 0.8, 1]
    b_factor = 0.3


    for color in range(len(ant_color_change_vector)):
        if ant_color[color] == 0:
            ant_color_change_vector[color] = v_change[color]
        elif ant_color[color] == 255:
            ant_color_change_vector[color] = (-1) * v_change[color]

    ant_color = update_color(ant_color, ant_color_change_vector)


    """if BACKGROUND[0] <= 0:
        b_change = [b_factor, b_factor, b_factor]

    elif BACKGROUND[0] > 70:
        b_change = [-b_factor, -b_factor, -b_factor]

    BACKGROUND = update_color(BACKGROUND, b_change)"""
    # uncomment if you want epilepsy background
    """avg_color_value = vector_sum(mv(ant_color, 1/3))
    extra = 30
    BACKGROUND = update_color(WHITE, int(avg_color_value) * (-1) - extra)
    print(BACKGROUND)"""

def draw_window(WIN, ants, color, background, enable_vel_color, distance):
    """WIN.fill(background)
    if enable_prox_color:
        for ant in ants:
            unique_color = color4proximity(ant, distance)
            for part in ant.body:
                pygame.draw.rect(WIN, (unique_color[0], unique_color[1], unique_color[2]), part)
    else:
        for ant in ants:
            for part in ant.body:
                pygame.draw.rect(WIN, (color[0], color[1], color[2]), part)"""


def modify_ants_and_simulate(WIN, pause, reverse, enable_physics, enable_vel_color, enable_weird):
    WIN.fill(BACKGROUND)
    if not enable_vel_color:
        manage_colors()

    for ant in ants:
        head = ant.body[0]
        ant_coords = [head.x, head.y]
        distance_to_mouse = distance_vector(ant_coords, Mouse.get_pos())
        distance = 0
        factor = 0
        x = distance_to_mouse[0] ** 2
        y = distance_to_mouse[1] ** 2
        distance = math.sqrt(x + y)
        if enable_physics or enable_vel_color:

            mouse_mass = 5
            d = distance / 100

            if d == 0 or d < 1:
                d = 1
            factor = (1 / ((d ** 2))) * mouse_mass

        if not pause:
            """if distance >= 100 and enable_weird:
                dot_prod = dot_product(distance_to_mouse, ant.vel_vector)
                sq_magnitude = distance**2

                temp = dot_prod/sq_magnitude
                temp = mv(distance_to_mouse, (-1) * temp)

                ant.vel_vector = av(ant.vel_vector, temp)"""
            follow_mouse(ant, distance_to_mouse, distance, reverse, enable_physics, enable_weird, factor)



        # ------ Color Part --------------
        if enable_vel_color:
            if enable_physics:
                unique_color = color4vel(ant, factor, distance)
                for part in ant.body:
                    pygame.draw.rect(WIN, (unique_color[0], unique_color[1], unique_color[2]), part)
            else:
                for part in ant.body:
                    pygame.draw.rect(WIN, (ant.color[0], ant.color[1], ant.color[2]), part)
        else:
            for part in ant.body:
                pygame.draw.rect(WIN, (ant_color[0], ant_color[1], ant_color[2]), part)

    pygame.display.update()


def main():
    global ant_color, BACKGROUND, ant_color_change_vector, weird_radius

    clock = pygame.time.Clock()
    run = True


    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ants?")

    for i in range(1000):
        ant = Ant()
        ants.append(ant)

    pause = False
    reverse = False
    enable_physics = True

    # particleların uçup gitmesini engelliyor
    enable_weird = False

    # When True, it enables ants to change to different colors
    # depending on their velocity of the ant
    enable_vel_color = False
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # most keyboard controls
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:
                    pause = not pause
                elif event.key == pygame.K_r:
                    reverse = not reverse
                elif event.key == pygame.K_e:
                    if enable_physics:
                        for ant in ants:
                            ant.set_velocity_vector([0, 0])
                    enable_physics = not enable_physics

                elif event.key == pygame.K_t:
                    tp_particles(ants)

                elif event.key == pygame.K_m:
                    enable_vel_color = not enable_vel_color

                elif event.key == pygame.K_w:
                    enable_weird = not enable_weird


        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:

            if weird_radius <= 0:
                weird_radius = 0

            else:
                weird_radius -= 2
        elif mouse_buttons[2]:
            weird_radius += 2

        modify_ants_and_simulate(WIN, pause, reverse, enable_physics, enable_vel_color, enable_weird)
    pygame.quit()


if __name__ == "__main__":
    main()