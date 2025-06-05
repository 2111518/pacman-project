import pygame
from pygame.locals import *

from constants import *
from entity import Entity
from sprites import PacmanSprites, PacmanGunSprites, PacmanShieldSprites

import time
from bullet import Bullet


class Pacman(Entity):
    def __init__(self, node) -> None:
        Entity.__init__(self, node )
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)

    def reset(self) -> None:
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self) -> None:
        self.alive = False
        self.direction = STOP

    def update(self, dt) -> None:
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        elif self.oppositeDirection(direction):
            self.reverseDirection()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other) -> bool:
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        return dSquared <= rSquared


class PacmanGun(Pacman):
    def __init__(self, node) -> None:
        super().__init__(node)
        self.name = PACMAN
        self.color = (255, 255, 255)
        self.sprites = PacmanGunSprites(self)
        self.character_type = "gun"
        self.ability = GunAbility(self)

    def update(self, dt) -> None:
        super().update(dt)
        self.ability.update(dt)

    def render(self, screen) -> None:
        super().render(screen)
        self.ability.render(screen)

#射擊子彈技能
class GunAbility:
    """管理槍技能的啟動、冷卻、子彈發射與顯示。"""
    def __init__(self, pacman) -> None:
        self.pacman = pacman
        self.state = "ready"  # ready, active, cooldown
        self.timer = 0.0
        self.cooldown = 10.0
        self.duration = 5.0
        self.bullets: list[Bullet] = []
        self.icon = pygame.image.load("ability_gun.png").convert_alpha()
        self.icon = pygame.transform.scale(self.icon, (48, 48))
        self.last_shot_time = 0.0

    def activate(self) -> None:
        if self.state == "ready":
            self.state = "active"
            self.timer = 0.0

    def update(self, dt: float) -> None:
        if self.state == "active":
            self.timer += dt
            if self.timer >= self.duration:
                self.state = "cooldown"
                self.timer = 0.0
        elif self.state == "cooldown":
            self.timer += dt
            if self.timer >= self.cooldown:
                self.state = "ready"
                self.timer = 0.0
        # 更新子彈
        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [b for b in self.bullets if b.active]

    def shoot(self) -> None:
        if self.state == "active":
            now = time.time()
            # 可加射速限制
            if now - self.last_shot_time > 0.15:
                bullet = Bullet(self.pacman.position.copy(), self.pacman.direction)
                self.bullets.append(bullet)
                self.last_shot_time = now

    def render(self, screen) -> None:
        # 畫圖示
        x = SCREENWIDTH // 2 - 24
        y = 10
        screen.blit(self.icon, (x, y))
        # 畫倒數
        font = pygame.font.Font("PressStart2P-Regular.ttf", 18)
        if self.state == "cooldown":
            cd = int(self.cooldown - self.timer) + 1
            text = font.render(str(cd), True, (255, 0, 0))
            screen.blit(text, (x + 54, y + 8))
        # 畫子彈
        for bullet in self.bullets:
            bullet.render(screen)

class PacmanShield(Pacman):
    def __init__(self, node) -> None:
        super().__init__(node)
        self.name = PACMAN
        self.color = (0, 255, 255)
        self.sprites = PacmanShieldSprites(self)
        self.character_type = "shield"
        self.ability = ShieldAbility(self)

    def update(self, dt) -> None:
        super().update(dt)
        self.ability.update(dt)

    def render(self, screen) -> None:
        super().render(screen)
        self.ability.render(screen)

class ShieldAbility:
    """管理盾牌技能的啟動、冷卻、圖片切換、鬼魂碰撞等。"""
    def __init__(self, pacman) -> None:
        self.pacman = pacman
        self.state = "ready"  # ready, active, cooldown
        self.timer = 0.0
        self.cooldown = 5.0
        self.duration = 3.0
        self.icon = pygame.image.load("ability_shield.png").convert_alpha()
        self.icon = pygame.transform.scale(self.icon, (48, 48))
        self.withshield_img = pygame.image.load("withshield.png").convert_alpha()
        self.withshield_img = pygame.transform.scale(self.withshield_img, (2*TILEWIDTH, 2*TILEHEIGHT))
        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 18)
        self.active = False

    def activate(self) -> None:
        if self.state == "ready":
            self.state = "active"
            self.timer = 0.0
            self.active = True
            self.pacman.image = self.withshield_img

    def update(self, dt: float) -> None:
        if self.state == "active":
            self.timer += dt
            self.pacman.image = self.withshield_img
  # 持續顯示盾牌圖
            if self.timer >= self.duration:
                self.state = "cooldown"
                self.timer = 0.0
                self.active = False
                self.pacman.image = self.pacman.sprites.getStartImage()
        elif self.state == "cooldown":
            self.timer += dt
            if self.timer >= self.cooldown:
                self.state = "ready"
                self.timer = 0.0

    def render(self, screen) -> None:
        # 畫技能圖示
        x = SCREENWIDTH // 2 - 24
        y = 10
        screen.blit(self.icon, (x, y))
        # 畫倒數
        if self.state == "cooldown":
            cd = int(self.cooldown - self.timer) + 1
            text = self.font.render(str(cd), True, (0, 191, 255))
            screen.blit(text, (x + 54, y + 8))

    def on_ghost_collide(self, ghost) -> None:
        # 技能啟動時，碰到鬼魂自動吃掉
        if self.state == "active" and ghost.mode.current is not SPAWN:
            ghost.startFreight()
            ghost.visible = False
            # 這裡分數與顯示由主流程處理
            ghost.startSpawn()
            self.pacman.game.nodes.allowHomeAccess(ghost)