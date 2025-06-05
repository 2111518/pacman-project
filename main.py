import sys

import pygame
from pygame.locals import *

from constants import *
from fruit import Fruit
from ghosts import GhostGroup
from mazedata import MazeData
from nodes import NodeGroup
from pacman import Pacman, PacmanGun, PacmanShield
from pauser import Pause
from pellets import PelletGroup
from sprites import LifeSprites, MazeSprites
from text import TextGroup


class GameController:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()
        self.selected_character = self.character_select()

    def character_select(self) -> int:
        """顯示角色選擇畫面，回傳選擇的角色編號。"""
        font = pygame.font.Font("PressStart2P-Regular.ttf", 24)  # 用遊戲內字型
        options = [
            {"name": "PACMAN", "img": pygame.image.load("spritesheet_mspacman.png").convert(), "desc": "經典吃豆人"},
            {"name": "GUN PACMAN", "img": pygame.image.load("pacman_gun.png").convert_alpha(), "desc": "Gun Pacman"},
            {"name": "SHIELD PACMAN", "img": pygame.image.load("pacman_shield.png").convert_alpha(), "desc": "Shield Pacman"}
        ]
        # 縮放角色圖示
        options[0]["img"] = pygame.transform.scale(options[0]["img"].subsurface(pygame.Rect(8*TILEWIDTH, 0, 2*TILEWIDTH, 2*TILEHEIGHT)), (64, 64))
        options[1]["img"] = pygame.transform.scale(options[1]["img"], (64, 64))
        options[2]["img"] = pygame.transform.scale(options[2]["img"], (64, 64))
        selected = 0
        clock = pygame.time.Clock()
        while True:
            self.screen.fill(BLACK)
            title = font.render("Select Character", True, YELLOW)
            title2 = font.render(" (← → switch, Enter)", True, YELLOW)
            self.screen.blit(title, (SCREENWIDTH//2 - title.get_width()//2, 100))
            self.screen.blit(title2, (SCREENWIDTH//2 - title2.get_width()//2, 150))
            for i, opt in enumerate(options):
                x = SCREENWIDTH//2 - 160 + i*120
                y = 200
                border_color = YELLOW if i == selected else WHITE
                pygame.draw.rect(self.screen, border_color, (x-8, y-8, 80, 80), 4)
                self.screen.blit(opt["img"], (x, y))
                desc = font.render(opt["desc"], True, WHITE)
                self.screen.blit(desc, (x-10, y+70))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        selected = (selected - 1) % len(options)
                    elif event.key == K_RIGHT:
                        selected = (selected + 1) % len(options)
                    elif event.key == K_RETURN or event.key == K_KP_ENTER:
                        return selected
            clock.tick(30)

    def setBackground(self) -> None:
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level%5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self) -> None:
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(self.mazedata.obj.name+".txt", self.mazedata.obj.name+"_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        # 根據選擇建立角色
        if self.selected_character == 0:
            self.pacman = Pacman(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        elif self.selected_character == 1:
            self.pacman = PacmanGun(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        elif self.selected_character == 2:
            self.pacman = PacmanShield(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        self.pellets = PelletGroup(self.mazedata.obj.name+".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))
        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def startGame_old(self) -> None:
        self.mazedata.loadMaze(self.level)#######
        self.mazesprites = MazeSprites("maze1.txt", "maze1_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0,17), (27,17))
        homekey = self.nodes.createHomeNodes(11.5, 14)
        self.nodes.connectHomeNodes(homekey, (12,14), LEFT)
        self.nodes.connectHomeNodes(homekey, (15,14), RIGHT)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 0+14))
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0+11.5, 3+14))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(4+11.5, 3+14))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, LEFT, self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, RIGHT, self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.nodes.denyAccessList(12, 14, UP, self.ghosts)
        self.nodes.denyAccessList(15, 14, UP, self.ghosts)
        self.nodes.denyAccessList(12, 26, UP, self.ghosts)
        self.nodes.denyAccessList(15, 26, UP, self.ghosts)



    def update(self) -> None:
        dt = self.clock.tick(30) / 1250.0
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()

        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

    def checkEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.pacman.alive:
                    self.pause.setPause(playerPaused=True)
                    if not self.pause.paused:
                        self.textgroup.hideText()
                        self.showEntities()
                    else:
                        self.textgroup.showText(PAUSETXT)
            # 技能啟動與射擊
            elif event.type == KEYDOWN and hasattr(self.pacman, "ability"):
                if event.key == pygame.K_j:
                    if self.pacman.ability.state == "active":
                        self.pacman.ability.shoot()
                    elif self.pacman.ability.state == "ready":
                        self.pacman.ability.activate()

    def checkPelletEvents(self) -> None:
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self) -> None:
        for ghost in self.ghosts:
            # 子彈碰撞
            if hasattr(self.pacman, "ability"):
                for bullet in self.pacman.ability.bullets:
                    if ghost.visible and bullet.rect.colliderect(ghost.image.get_rect(center=ghost.position.asInt())) and ghost.mode.current is not SPAWN:
                        ghost.startFreight()  # 先進入可吃狀態
                        ghost.visible = False
                        self.updateScore(ghost.points)
                        self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                        self.ghosts.updatePoints()
                        self.pause.setPause(pauseTime=1, func=self.showEntities)
                        ghost.startSpawn()
                        self.nodes.allowHomeAccess(ghost)
                        bullet.active = False
            # 原本的 Pacman 碰撞
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)
                    self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -=  1
                        self.lifesprites.removeImage()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)

    def checkFruitEvents(self) -> None:
        if self.pellets.numEaten in {50, 140} and self.fruit is None:
            self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self) -> None:
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self) -> None:
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self) -> None:
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self) -> None:
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self) -> None:
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points) -> None:
        self.score += points
        self.textgroup.updateScore(self.score)

    def render(self) -> None:
        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))

        # 顯示技能圖示與倒數
        if hasattr(self.pacman, "ability"):
            self.pacman.ability.render(self.screen)

        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()



