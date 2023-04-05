import os
import sys

from utils import logs, decrease, increase, is_positive, get_image, sign
from parser import get_level, display
from src.bullet import Bullet

import pygame

pygame.init()
pygame.font.init()

ARIAL = pygame.font.SysFont("ARIAL", 12)
LARGE_TEXT = pygame.font.SysFont("ARIAL", 40)

levels = []
level_directory = os.listdir("levels")

for filename in level_directory:
    id = int(filename.removesuffix(".json"))
    levels.append(id)

MAX_LEVEL = max(levels)

class Game:
    def __init__(self, fps) -> None:
        self.screen_width = 900
        self.screen_height = 600
        
        # self.screen is the actual screen. Everything should be drawn on self.g, because that screen will be resized and drawn onto the real screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("can pooper's adventures")
        self.g = self.screen.copy()

        self.clock = pygame.time.Clock()
        self.stopped = False
        self.framecap = fps
        self.entitycount = 1
        self.level = 1
        self.draw_level(self.level)

        self.bullets = pygame.sprite.Group()
    
    # to be called when an entire new level has to be loaded
    def draw_level(self, id):
        layout = get_level(id)
        self.g.fill((255, 255, 255))
        data = display(self.g, layout)
        self.player = data["player"]
        self.enemies = data["enemies"]
        self.collidables = data["collidables"]
        self.fatal = data["fatal"]
        self.objectives = data["objectives"]

    def process_events(self):
        # process keyboard events
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return
        
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.player.last_bullet_fired > self.player.firing_cooldown:
                self.bullets.add(Bullet(self.player.x, self.player.y, 1, 15, self.player.facing_right, False, 3000, 33))
                self.player.last_bullet_fired = current_time
            else:
                return
        elif keys[pygame.K_k]:
            pygame.time.wait(50)
            self.next_level()

    def next_level(self):
        pygame.display.flip()
        self.g.fill((255, 255, 255))

        if self.level >= MAX_LEVEL:
            self.level = 1
            self.screen.fill((255, 255, 255))
            w = LARGE_TEXT.render(
                f"you win lets goooooooooooo", False, (0, 0, 0))
            self.screen.blit(w, (10, 100))
            pygame.display.flip()
            self.player.respawn(2000)
        else:
            self.level += 1
            self.player.respawn(250)

        self.draw_level(self.level)

    def loop(self):
        while not self.stopped:
            self.process_events()
            pygame.event.pump()

            self.enemy_bullets = pygame.sprite.Group()

            self.g.fill((255, 255, 255))
            
            # draw grid
            for i in range(0, 900, 100):
                for j in range(0, 1800, 100):
                    rect = pygame.Rect(i, j, 100, 100)
                    pygame.draw.rect(self.g, (230, 230, 230), rect, 1)

            if self.player.has_reached_objective(self.objectives):
                self.next_level()
            
            for bullet in self.bullets:
                if (bullet.x > self.screen_width + 100 or bullet.x < -100) or bullet.y > (self.screen_height + 100 or bullet.y < -100):
                    bullet.kill()
                bullet.move(bullet.x_speed, bullet.y_speed, self.collidables)
                bullet.update()
            
            for enemy in self.enemies:
                enemy.update(self.collidables, self.fatal, self.bullets, self.g)
                for bullet in enemy.bullets:
                    self.bullets.add(bullet)

            self.player.update(self.collidables, self.fatal, self.bullets, self.g)

            self.player.draw(self.g)
            self.collidables.draw(self.g)
            self.fatal.draw(self.g)
            self.objectives.draw(self.g)
            self.bullets.draw(self.g)
            self.enemies.draw(self.g)
            
            self.entitycount = 1 + len(self.collidables) + len(self.fatal) + len(self.objectives) + len(self.bullets)
            coordinates = ARIAL.render(
                f"({self.player.x}, {self.player.y})", False, (0, 0, 0))
            onground = ARIAL.render(
                f"onGround: {self.player.on_ground}", False, (0, 0, 0))
            crouching = ARIAL.render(
                f"crouching: {self.player.crouching}", False, (0, 0, 0))
            direction = ARIAL.render(
                f"facing: {'RIGHT' if self.player.facing_right else 'LEFT'}", False, (0, 0, 0))
            fps = ARIAL.render(
                f"FPS: {round(self.clock.get_fps(), 1)}", False, (0, 0, 0))
            entitycount = ARIAL.render(
                f"entityCount: {self.entitycount}", False, (0, 0, 0))
            deaths = ARIAL.render(
                f"deathCount: {self.player.death_count}", False, (0, 0, 0))

            self.g.blit(coordinates, (10, 10))
            self.g.blit(onground, (10, 25))
            self.g.blit(crouching, (10, 40))
            self.g.blit(direction, (10, 55))
            self.g.blit(fps, (10, 70))
            self.g.blit(entitycount, (10, 85))
            self.g.blit(deaths, (10, 100))
            
            self.screen.blit(pygame.transform.scale(self.g, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(self.framecap)


if __name__ == "__main__":
    h = Game(fps=60)
    h.loop()
