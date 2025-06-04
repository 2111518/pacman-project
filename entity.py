from random import randint

import pygame
from pygame.locals import *

from constants import *
from vector import Vector2


class Entity:
    def __init__(self, node) -> None:
        self.name = None
        self.directions = {UP:Vector2(0, -1),DOWN:Vector2(0, 1),
                          LEFT:Vector2(-1, 0), RIGHT:Vector2(1, 0), STOP:Vector2()}
        self.direction = STOP
        self.setSpeed(100)
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.visible = True
        self.disablePortal = False
        self.goal = None
        self.directionMethod = self.randomDirection
        self.setStartNode(node)
        self.image = None

    def setPosition(self) -> None:
        self.position = self.node.position.copy()

    def update(self, dt) -> None:
        self.position += self.directions[self.direction]*self.speed*dt

        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            if not self.disablePortal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()

    def validDirection(self, direction) -> bool:
        #print(f"Entity.validDirection for {self.name} at Node {self.node.position if self.node else 'None'} with Dir: {direction}") # DEBUG LINE
        if direction is not STOP:
            if self.node is None:
                #print(f"  validDirection REJECT: self.node is None") # DEBUG LINE
                return False
            if self.name not in self.node.access[direction]:
                #print(f"  validDirection REJECT: {self.name} not in Node access[{direction}] = {self.node.access[direction]}") # DEBUG LINE
                return False
            if self.node.neighbors[direction] is None:
                #print(f"  validDirection REJECT: Node neighbors[{direction}] is None") # DEBUG LINE
                return False
            #print(f"  validDirection ACCEPT: Node access and neighbor OK.") # DEBUG LINE
            return True
        #print(f"  validDirection REJECT: Direction is STOP") # DEBUG LINE
        return False

    def getNewTarget(self, direction):
        #print(f"Entity.getNewTarget for {self.name} at Node {self.node.position if self.node else 'None'} with input Dir: {direction}") # DEBUG LINE
        if self.validDirection(direction):
            #print(f"  getNewTarget SUCCESS: Returning neighbor {self.node.neighbors[direction].position if self.node and self.node.neighbors[direction] else 'Error getting neighbor'}") # DEBUG LINE
            return self.node.neighbors[direction]
        #print(f"  getNewTarget FAIL: validDirection was False. Returning current node {self.node.position if self.node else 'None'}") # DEBUG LINE
        return self.node

    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self) -> None:
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction) -> bool:
        return bool(direction is not STOP and direction == self.direction * -1)

    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key) and key != self.direction * -1:
                directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions):
        return directions[randint(0, len(directions)-1)]

    def goalDirection(self, directions):
        distances = []
        for direction in directions:
            vec = self.node.position  + self.directions[direction]*TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]

    def setStartNode(self, node) -> None:
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    def setBetweenNodes(self, direction) -> None:
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    def reset(self) -> None:
        self.setStartNode(self.startNode)
        self.direction = STOP
        self.speed = 100
        self.visible = True

    def setSpeed(self, speed) -> None:
        self.speed = speed * TILEWIDTH / 16

    def render(self, screen) -> None:
        if self.visible:
            if self.image is not None:
                adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.asTuple())
            else:
                p = self.position.asInt()
                pygame.draw.circle(screen, self.color, p, self.radius)
