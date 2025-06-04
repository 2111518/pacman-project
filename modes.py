from constants import *


class MainMode:
    def __init__(self) -> None:
        self.timer = 0
        self.scatter()

    def update(self, dt) -> None:
        self.timer += dt
        if self.timer >= self.time:
            if self.mode is SCATTER:
                self.chase()
            elif self.mode is CHASE:
                self.scatter()

    def scatter(self) -> None:
        self.mode = SCATTER
        self.time = 7
        self.timer = 0

    def chase(self) -> None:
        self.mode = CHASE
        self.time = 20
        self.timer = 0


class ModeController:
    def __init__(self, entity) -> None:
        self.timer = 0
        self.time = None
        self.mainmode = MainMode()
        self.current = self.mainmode.mode
        self.entity = entity

    def update(self, dt) -> None:
        self.mainmode.update(dt)
        if self.current is FREIGHT:
            self.timer += dt
            if self.timer >= self.time:
                self.time = None
                self.entity.normalMode()
                self.current = self.mainmode.mode
        elif self.current in [SCATTER, CHASE]:
            self.current = self.mainmode.mode

        if self.current is SPAWN and self.entity.node == self.entity.spawnNode:
            self.entity.normalMode()
            self.current = self.mainmode.mode

    def setFreightMode(self) -> None:
        if self.current in [SCATTER, CHASE]:
            self.timer = 0
            self.time = 7
            self.current = FREIGHT
        elif self.current is FREIGHT:
            self.timer = 0

    def setSpawnMode(self) -> None:
        if self.current is FREIGHT:
            self.current = SPAWN
