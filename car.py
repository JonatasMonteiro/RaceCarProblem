#!/usr/bin/python

import os
from datetime import datetime
from time import sleep
import pygame
import copy
import math
import numpy as np
from pygame.locals import *

starting_grid   = [[0,0]]

class Agent:
    def __init__(self,car,NN):
        self.NN = NN
        self.c ar= car
        self.fitness = -1

def ga(agents,oldagents):
    popSize = len(agents)
    sum = fitness(agents)
    sumOld = 0
    for i in xrange(len(oldagents)):
        sumOld += oldagents[i].fitness

    print "Soma do Fitness da nova geracao: "+str(sum)
    print "Soma do Fitness da antiga geracao: "+str(sumOld)
    if sum > sumOld:
        agents = crossover(agents,popSize)
        agents = mutation(agents)
        return agents
    else:
        oldagents = crossover(oldagents, popSize)
        oldagents = mutation(oldagents)
        return oldagents




def fitness(agents):
    sum = 0
    for agent in agents:
        #timedeltaLife = agent.car.deathTime - agent.car.birthTime
        agent.fitness = agent.car.actual_step#timedeltaLife.seconds*1000000 + timedeltaLife.microseconds
        sum += agent.fitness
    return sum

def selection(agents):
    agents = sorted(agents,key=lambda agent:agent.fitness,reverse=True)
    agents = agents[0:2]
    return agents

def mutation(agents):
    for agent in agents:
        for i in xrange(len(agent.NN.hiddenLayerWeights)):
            for j in xrange(agent.NN.inputNodesNumber+1):
                chance = np.random.uniform(low=0.0, high=1.0)
                if chance <= 0.5:
                    newWeight = np.random.uniform(low=-0.1, high=0.1)
                    agent.NN.hiddenLayerWeights[i][j] = newWeight
    return agents

def crossover(agents,popSize):
    chance = np.random.uniform(low=0.0, high=1.0)
    if chance <= 1.0:
        result = []
        agents = selection(agents)
        for _ in xrange(popSize):
            parentOne = agents[0]
            parentTwo = agents[1]
            indexsOfHWeight = []
            amount = np.random.randint(low=0,high=parentOne.NN.inputNodesNumber)
            for x in xrange(amount):
                weight = np.random.randint(low=0,high=parentOne.NN.inputNodesNumber)
                while(weight in indexsOfHWeight):
                    weight = np.random.randint(low=0,high=parentOne.NN.inputNodesNumber)
                indexsOfHWeight.append(weight)
            childOne = parentOne
            childTwo = parentTwo
            indexsOfOWeight = []

            for x in xrange(amount):
                childOne.NN.hiddenLayerWeights[x][indexsOfHWeight[x]] = childTwo.NN.hiddenLayerWeights[x][indexsOfHWeight[x]]

            amounttwo = np.random.randint(low=0, high=len(parentOne.NN.hiddenLayerWeights))
            for i in xrange(amounttwo):
                weight = np.random.randint(low=0,high=len(parentOne.NN.hiddenLayerWeights))
                while weight in indexsOfOWeight:
                    weight = np.random.randint(low=0,high=len(parentOne.NN.hiddenLayerWeights))
                indexsOfOWeight.append(weight)


            for z in xrange(2):
                for y in xrange(amounttwo):
                    childOne.NN.outputLayerWeights[z][indexsOfOWeight[y]] = childTwo.NN.outputLayerWeights[z][indexsOfOWeight[y]]
            result.append(childOne)
        return result
    else:
        return agents

class neuralNetwork:
   def __init__(self,inputNodesNumber,hiddenLayerNodesNumber,outputNodesNumber):
         self.inputNodesNumber = inputNodesNumber
         self.hiddenLayerWeights = np.random.uniform(low=-0.1, high=0.1, size=(hiddenLayerNodesNumber,inputNodesNumber+1))
         self.outputLayerWeights = np.random.uniform(low=-0.1, high=0.1, size=(outputNodesNumber,hiddenLayerNodesNumber+1))
   def sigmoid(self,x):
        return 1.0/(1.0 + (np.exp((-1.0)*x)))

   def run(self,inputs):
       inputs.append(1.0)
       hiddenLayerValues = [self.sigmoid(value) for value in np.dot(self.hiddenLayerWeights,inputs)]
       hiddenLayerValues.append(1.0)
       outputLayerValues = [self.sigmoid(value) for value in np.dot(self.outputLayerWeights,hiddenLayerValues)]
       outputLayerValues[0] = (outputLayerValues[0] -0.3)
       outputLayerValues[1] = (outputLayerValues[1]/12.0)
       return outputLayerValues

        #nota para continuar: Implementar a segunda HiddenLayer





class RaceObject(pygame.sprite.Sprite):
    obj_counter  = 0

    def __init__(self,file_name,starting_grid_pos,terrain,brain):
        self.birthTime = datetime.now()
        self.brain = brain
        self.deathTime = None
        self.alive = True;
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

        xfront = int(xfront+ self.rect[0]+self.image_ref.get_width()/2.0)
        yfront = int(yfront+ self.rect[1]+self.image_ref.get_height()/2.0)

        for i in range(len(angles)):

            angle = angles[i] + self.direction
            dist  = distances[i]
            xmax = math.cos(math.radians(angle)) *dist
            ymax = math.sin(math.radians(angle)) *dist
            x = np.linspace(0,xmax,10).astype(int)
            y = np.linspace(0,ymax,10).astype(int)


            acc = 0 
            for (xpos,ypos) in zip(x,y):
                xpos += xfront  
                ypos += yfront
                try:acc += (255-np.average(screen.get_at((xpos,ypos))))
                except:
                    self.alive = False
                    self.deathTime = datetime.now()

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

    def runNN(self,inputs):
        output = self.brain.run(inputs)
        self.direction += output[0]
        self.forward += output[1]
        return 1

def isAnyCarAlive(cars):
    for car in cars:
        if car.alive == True:
            return True;
    return False;





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


    starting_grid   = [[280,90]]
    car_image_files = ["carro.png"]
    
    car_keymap      = [{'right':K_RIGHT,'left':K_LEFT,'up':K_UP,'down':K_DOWN,'pause':K_SPACE},
                       {'right':K_d,'left':K_a,'up':K_w,'down':K_s,'pause':K_x}]
     
    cars = []
    oldagents = []
    neuralTemp = neuralNetwork(1,2,3)
    car = RaceObject(car_image_files[0], starting_grid[0], terrain1,neuralTemp)
    agent = Agent(car,neuralTemp)
    oldagents.append(agent)
    afont = pygame.font.Font(None, 16)
    for j in xrange(1000):
        print "Generation: "+str(j)
        neuralNets = []
        if j == 0:
            for k in xrange(20):
                neuralNets.append(neuralNetwork(7, 10, 2))
        else:
            for k in xrange(20):
                neuralNets.append((agents[k].NN))
        agents = []
        for i in xrange(20):
            car = RaceObject(car_image_files[0], starting_grid[0], terrain1,neuralNets[i])
            agent = Agent(car,neuralNets[i])
            agents.append(agent)
        for agent in agents:
            events = pygame.event.get()
            while agent.car.alive == True:
                agent.car.update_pos()
                screen.fill((255, 255, 255))
                screen.blit(terrain1, (0, 0))
                msg_y = 0
                agent.car.draw(screen)
                if agent.car.terrain_overlap():
                    hitsurf = afont.render("Car " + str(agent.car.obj_id) + " terrain hit!", 1, (255, 255, 255))
                    screen.blit(hitsurf, (0, msg_y))
                    msg_y += 20
                    # limit the speed
                    agent.car.forward = 0
                    agent.car.alive = False
                    agent.car.deathTime = datetime.now()
    # message font

    # start the main loop.

        # draw the background color, and the terrain.


        # draw cars.
                sonar = agent.car.get_sonar_values(screen,[0,30,-30,60,-60,90,-90],[80,40,40,40,40,40,40])
                agent.car.runNN(sonar)
                # get your neural network input from here!

        # check collision among cars

        # flip the display.
                pygame.display.flip()

            # limit the frame rate.
                clock.tick(120)
        agents = ga(agents,oldagents)
        oldagents = agents


pygame.quit()


