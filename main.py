#!/usr/bin/env python3.10

import os
import time
import numpy as np
try:
    import pygame
except ImportError:
    print("Forcibly installing PyGame on your computer wtihout your consent...")
    if os.name == "nt":
        os.system("py3 -m pip install pygame")
        os.system("echo 🤡 imagine being on windows")
    else:
        os.system("python3 -m pip install pygame")

pygame.init()

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width = 100, height = 100, show_hitbox = False):
        super().__init__()

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = [x + width/2, y + height/2]

        self.x = x
        self.y = y

        self.width = width
        self.height = height
        
        self.hitbox = show_hitbox

    def draw(self, screen):
        if self.hitbox:
            pygame.draw.rect(screen, pygame.Color(255, 0, 0), self.rect, width = 5)
        center = np.array(self.rect.center) - (self.width/2, self.height/2)
        screen.blit(self.image, list(center))

class Player(Entity):
    def __init__(self, x, y, width = 100, height = 200, hitbox = False):
        super().__init__("assets/canpooper.png", x, y, width, height, hitbox)
        self.x_speed = 0
        self.y_speed = 0
        self.max_x_speed = 5
        self.gravity = 9.807

        self.respawn_x = x
        self.respawn_y = y

        self.jump_power = 1
    
    def move(self, x, y, collidables):
        dx = x
        dy = y

        while self.colliding_at(0, dy, collidables):
            dy -= np.sign(dy)
        while self.colliding_at(dx, dy, collidables):
            dx -= np.sign(dx)
        
        self.y += dy
        self.x += dx

        self.rect.move_ip((dx, dy))
    
    def colliding_at(self, x, y, entities):
        # returns group of entities
        self.rect.move_ip((x, y))
        colliding = pygame.sprite.spritecollideany(self, entities)
        self.rect.move_ip((-x, -y))
        return colliding
    
    def on_ground(self, entities):
        for entity in entities:
            if (entity.rect.top == self.rect.bottom) and (entity.rect.left <= self.rect.left <= entity.rect.right or entity.rect.left <= self.rect.right <= entity.rect.right):
                return True
        return False
    
    def hitting_ceiling(self, entities):
        for entity in entities:
            if (entity.rect.bottom == self.rect.top) and (entity.rect.left <= self.rect.left <= entity.rect.right or entity.rect.left <= self.rect.right <= entity.rect.right):
                return True
        return False
    
    def update(self, collidables, fatal):
        if pygame.sprite.spritecollideany(self, fatal):
            self.die(1000)
        
        keys = pygame.key.get_pressed()
        on_ground = self.on_ground(collidables)
        hitting_ceiling = self.hitting_ceiling(collidables)
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x_speed = -self.max_x_speed
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x_speed = self.max_x_speed
        
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
            self.y_speed = -self.jump_power * 10
        
        if (keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and on_ground:
            self.x_speed *= 0.6
        
        if not on_ground and self.y_speed < 15:
            self.y_speed += self.gravity * 0.06
        
        self.move(self.x_speed, self.y_speed, collidables)
        self.x_speed = 0
    
    def die(self, timeout):
        pygame.time.wait(timeout)
        self.x_speed = 0
        self.y_speed = 0
        self.rect.move_ip((self.respawn_x - self.x, self.respawn_y - self.y))
        self.x = self.respawn_x
        self.y = self.respawn_y

class Crate(Entity):
    def __init__(self, x, y, width=200, height=200, hitbox=False):
        super().__init__("assets/crate.png", x, y, width, height, hitbox)

class Lava(Entity):
    def __init__(self, x, y, width=960, height=100, hitbox=False):
        super().__init__("assets/lava.png", x, y, width, height, hitbox)

class Game:
    def __init__(self, fps) -> None:
        self.screen = pygame.display.set_mode((960, 640))
        pygame.display.set_caption("can pooper's adventures in Poopland")
        self.clock = pygame.time.Clock()
        self.stopped = False
        self.framecap = fps
        self.player = Player(100, 50, 50, 50, True)

        self.collidables = pygame.sprite.Group()
        self.collidables.add(Crate(100, 200, 100, 100, True))
        self.collidables.add(Crate(400, 200, 100, 100, True))
        self.collidables.add(Crate(700, 200, 100, 100, True))

        self.fatal = pygame.sprite.Group()
        self.fatal.add(Lava(0, 540, 960, 100, True))
    
    def process_events(self):
        # process keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
    
    def loop(self):
        while not self.stopped:
            self.process_events()

            pygame.event.pump()
            
            self.screen.fill((255, 255, 255))
            self.player.update(self.collidables, self.fatal)
            
            self.player.draw(self.screen)
            self.collidables.draw(self.screen)
            self.fatal.draw(self.screen)
            
            pygame.display.flip()
            
            self.clock.tick(self.framecap)

if __name__ == "__main__":
    h = Game(fps=56)
    h.loop()