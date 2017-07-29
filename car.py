#!/usr/bin/python

import os
from time import sleep
import pygame
import copy
import math
import numpy as np
from pygame.locals import *

class Agent:
    population_size = 20

#def fitness():


#def selection():


#def mutation():

#def crossover():



class RaceObject(pygame.sprite.Sprite):
    obj_counter  = 0

    def __init__(self,file_name,starting_grid_pos,terrain):
        
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = pygame.image.load(file_name).convert_alpha()
        self.image_ref = copy.copy(self.image)

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.starting_grid_pos = starting_grid_pos
        
        self.direction = 0
        self.forward   = 0

        self.prev_direction = 0
        self.prev_forward   = 0

        self.origin_pos = [0,0]
        self.unitx = 0
        self.unity = 0
        self.actual_step = 0

        self.collision_count = 0

        self.set_pos(starting_grid_pos)
        self.terrain      = terrain
        self.terrain_mask = pygame.mask.from_surface(terrain, 50)
        self.obj_id = RaceObject.obj_counter
        RaceObject.obj_counter += 1

    def neural_network(self,inputs):
        a = 1
        bias = 1
        inputs =

    def terrain_overlap(self):
        return self.terrain_mask.overlap(self.mask,(self.rect[0],self.rect[1]))

    def set_pos(self,pos):
        self.rect[0] = pos[0]
        self.rect[1] = pos[1]

    def set_keymap(self,keymap):
        self.keymap = keymap

    def rot_center(self,image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def draw(self,screen):
        screen.blit(self.image,(self.rect[0],self.rect[1]))

    def update_pos(self,dt=1):
        if self.direction != 0 or self.forward !=0:
            self.unitx = math.cos(math.radians(self.direction))
            self.unity = math.sin(math.radians(self.direction))
            if self.direction != self.prev_direction:

                self.actual_step = 0
                
                self.image = self.rot_center(self.image_ref,-self.direction)
                self.mask = pygame.mask.from_surface(self.image)

                self.prev_direction = self.direction
                self.origin_pos[0] = self.rect[0]
                self.origin_pos[1] = self.rect[1]

            if self.forward != self.prev_forward:

                self.origin_pos[0] = self.rect[0]
                self.origin_pos[1] = self.rect[1]

                self.actual_step = self.forward
                self.prev_forward   = self.forward

            self.step_forward()
    def get_sonar_values(self,screen,angles,distances):
        ret = []

        xfront = math.cos(math.radians(self.direction))
        yfront = math.sin(math.radians(self.direction))
        #print xfront,yfront, self.image_ref.get_rect()

        xfront = int(xfront+ self.rect[0]+self.image_ref.get_width()/2.0)
        yfront = int(yfront+ self.rect[1]+self.image_ref.get_height()/2.0)

        for i in range(len(angles)):

            angle = angles[i] + self.direction
            dist  = distances[i]
            xmax = math.cos(math.radians(angle)) *dist
            ymax = math.sin(math.radians(angle)) *dist
            x = np.linspace(0,xmax,10).astype(int)
            y = np.linspace(0,ymax,10).astype(int)

            #print xmax,ymax,x,y
            acc = 0 
            for (xpos,ypos) in zip(x,y):
                xpos += xfront  
                ypos += yfront 
                #print xpos,ypos, (255-np.average(screen.get_at((xpos,ypos))))
                acc += (255-np.average(screen.get_at((xpos,ypos))))
                pygame.draw.line(screen,[255,0,0],(xfront,yfront),(xpos,ypos))
            ret.append(acc)
        return ret




          

    def step_forward(self):
        if self.forward != 0:
            i = self.actual_step
            x = self.unitx*self.actual_step
            if self.unitx == 0:
                y = 0
            else:
                y = (self.unity/self.unitx)*x 

            self.rect[0] = self.origin_pos[0]+x
            self.rect[1] = self.origin_pos[1]+y

            self.actual_step+=self.forward
    def test(self):
        self.direction += 0.5
        self.forward += 0.5
        return 1

    def eval_event(self,events):
        left  = self.keymap['left']
        right = self.keymap['right']
        up    = self.keymap['up']
        down  = self.keymap['down']
        pause = self.keymap['pause']


        
        for e in events:
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
                return False
            if e.type == pygame.KEYDOWN:
                # move the object around, depending on the keys.
                if e.key == left:
                    self.direction -= 2
                if e.key == right:
                    self.direction += 2
                if e.key == up:
                    self.forward += 0.5
                if e.key == down:
                    self.forward -= 0.5
                if e.key == pause:
                    self.forward = 0
        return True





if __name__ == '__main__':
    if not hasattr(pygame, "Mask"):
        raise "Need pygame 1.8 for masks."

    pygame.display.init()
    pygame.font.init()

    screen = pygame.display.set_mode((640,480))
    pygame.key.set_repeat(500, 2)
    clock = pygame.time.Clock()


    # fill the screen 
    screen.fill((255,255,255))
    pygame.display.flip()
    pygame.display.set_caption("Trabalho de IA")


    terrain1 = pygame.image.load("terrain2.png").convert_alpha()


    starting_grid   = [[178,75],[230,75]]
    car_image_files = ["carro.png","carro.png"]
    
    car_keymap      = [{'right':K_RIGHT,'left':K_LEFT,'up':K_UP,'down':K_DOWN,'pause':K_SPACE},
                       {'right':K_d,'left':K_a,'up':K_w,'down':K_s,'pause':K_x}]
     
    cars = []
    for i in range(2):
        car = RaceObject(car_image_files[i], starting_grid[i], terrain1)
        car.set_keymap(car_keymap[i])
        cars.append(car)
        
    # message font
    afont = pygame.font.Font(None, 16)

    # start the main loop.
    going = 1
    while going:
        events = pygame.event.get()
        for car in cars:
            going = car.test()
            car.update_pos()


        # draw the background color, and the terrain.
        screen.fill((255,255,255))
        screen.blit(terrain1, (0,0))

        # draw cars.
        msg_y = 0
        for car in cars:
            car.draw(screen)
            if car.terrain_overlap():
                hitsurf = afont.render("Car "+str(car.obj_id)+" terrain hit!", 1, (255,255,255))
                screen.blit(hitsurf, (0,msg_y))
                msg_y+=20
                # limit the speed
                car.forward   = 0

        for car in cars:
            sonar = car.get_sonar_values(screen,[0,30,-30,60,-60,90,-90],[80,40,40,40,40,40,40])
            # get your neural network input from here!

            print car.obj_id, sonar

        # check collision among cars
        if len(cars) > 1: 
            for i in range(len(cars)):
                for j in range(i+1,len(cars)):
                    offset = (cars[i].rect[0]-cars[j].rect[0],cars[i].rect[1]-cars[j].rect[1])
                    if cars[i].mask.overlap(cars[j].mask,offset):
                        cars[i].forward = 0
                        cars[j].forward = 0
                        hitsurf = afont.render("Collision!! Cars "+str(cars[i].obj_id)+" and "+str(cars[j].obj_id), 1, (255,255,255))
                        screen.blit(hitsurf, (0,msg_y))
                        msg_y+=20





        # flip the display.
        pygame.display.flip()

        # limit the frame rate.
        clock.tick(20)

    pygame.quit()


