#!/usr/bin/env python

import pygame
from pygame.locals import *  # noqa
import sys
import random
from enum import Enum


class Actions(Enum):
    CLICK = 0,
    DO_NOTHING = 1


class FlappyBird:
    def __init__(self, alpha=0.3, gamma=0.9, debug=True):
        self.screen = pygame.display.set_mode((400, 708))
        self.bird = pygame.Rect(65, 50, 50, 50)
        self.background = pygame.image.load("assets/background.png").convert()
        self.birdSprites = [pygame.image.load("assets/1.png").convert_alpha(),
                            pygame.image.load("assets/2.png").convert_alpha(),
                            pygame.image.load("assets/dead.png")]
        self.wallUp = pygame.image.load("assets/bottom.png").convert_alpha()
        self.wallDown = pygame.image.load("assets/top.png").convert_alpha()
        self.gap = 130
        self.wallx = 400
        self.birdY = 350
        self.jump = 0
        self.jumpSpeed = 10
        self.gravity = 5
        self.dead = False
        self.sprite = 0
        self.counter = 0
        self.offset = random.randint(-110, 110)
        self.q = {}
        self.debug=True
        self.alpha = alpha
        self.gamma = gamma
        self.horizontal_dist_dash = 99999
        self.vertical_dist_hash = 99999
        self.action_to_perform = random.choice([Actions.CLICK, Actions.DO_NOTHING])

    def updateWalls(self):
        self.wallx -= 2
        if self.wallx < -80:
            self.wallx = 400
            self.counter += 1
            self.offset = random.randint(-110, 110)

    def getQ(self, state):
        return self.q.get(state, 0.0)

    def birdUpdate(self):
        if self.jump:
            self.jumpSpeed -= 1
            self.birdY -= self.jumpSpeed
            self.jump -= 1
        else:
            self.birdY += self.gravity
            self.gravity += 0.2
        self.bird[1] = self.birdY
        upRect = pygame.Rect(self.wallx,
                             360 + self.gap - self.offset + 10,
                             self.wallUp.get_width() - 10,
                             self.wallUp.get_height())
        downRect = pygame.Rect(self.wallx,
                               0 - self.gap - self.offset - 10,
                               self.wallDown.get_width() - 10,
                               self.wallDown.get_height())

        if upRect.colliderect(self.bird):
            self.dead = True
        if downRect.colliderect(self.bird):
            self.dead = True
        if not 0 < self.bird[1] < 720:
            self.bird[1] = 50
            self.birdY = 50
            self.dead = False
            self.counter = 0
            self.wallx = 400
            self.offset = random.randint(-110, 110)
            self.gravity = 5

        if self.debug:
            border_color = (255, 0, 0)
            blue_color = (0, 0, 255)

            # Draw the horizontal line
            pygame.draw.lines(self.screen, border_color, False, [(self.bird[0] + self.bird[2], self.bird[1] + self.bird[3]),
                                                                 (self.wallx, self.bird[1] + self.bird[3])], 2)

            # Draw the vertical line
            pygame.draw.lines(self.screen, border_color, False, [(self.bird[0] + self.bird[2], self.bird[1] + self.bird[3]),
                                                                 (self.bird[0] + self.bird[2], 360 + self.gap - self.offset + 10)], 2)

            horizontal_dist = min(0, self.wallx - (self.bird[0] + self.bird[2]))
            vertical_dist = min(0, (360 + self.gap - self.offset + 10) - (self.bird[1] + self.bird[3]))

            print("Horizontal Dist: %s --- Vertical Dist: %s" % (horizontal_dist, vertical_dist))
            input()

            # Q[s,a] ← Q[s,a] + α (r + γ * V(s') - Q[s,a])
            v_dash_do_nothing = self.getQ((self.horizontal_dist_dash, self.vertical_dist_hash, Actions.DO_NOTHING))
            v_dash_click = self.getQ((self.horizontal_dist_dash, self.vertical_dist_hash, Actions.CLICK))
            v_dash = max(v_dash_click, v_dash_do_nothing)

            current_state = (horizontal_dist, vertical_dist, self.action_to_perform)
            reward = 1 if self.dead is False else -1000

            original = self.getQ(current_state)
            self.q[current_state] = original + self.alpha * (reward + self.gamma * v_dash - original)
            print("Current State: %s   --> Q Value: %s" % (current_state, self.q[current_state]))

            pygame.draw.rect(self.screen, blue_color, self.bird, 2)
            pygame.draw.rect(self.screen, border_color, upRect, 2)
            pygame.draw.rect(self.screen, border_color, downRect, 2)
            self.screen.blit(self.birdSprites[self.sprite], (70, self.birdY))

            click_action = self.getQ((horizontal_dist, vertical_dist, Actions.CLICK))
            do_nothing_action = self.getQ((horizontal_dist, vertical_dist, Actions.DO_NOTHING))

            if click_action > do_nothing_action:
                return Actions.CLICK
            else:
                return Actions.DO_NOTHING

    def run(self):
        clock = pygame.time.Clock()
        pygame.font.init()
        font = pygame.font.SysFont("Arial", 50)
        next_action = random.choice([Actions.CLICK, Actions.DO_NOTHING])
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN or next_action == Actions.CLICK) and not self.dead:
                    self.jump = 17
                    self.gravity = 5
                    self.jumpSpeed = 10

            self.screen.fill((255, 255, 255))
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.wallUp,
                             (self.wallx, 360 + self.gap - self.offset))
            self.screen.blit(self.wallDown,
                             (self.wallx, 0 - self.gap - self.offset))
            self.screen.blit(font.render(str(self.counter),
                                         -1,
                                         (255, 255, 255)),
                             (200, 50))
            if self.dead:
                self.sprite = 2
            elif self.jump:
                self.sprite = 1
            if not self.dead:
                self.sprite = 0
            self.updateWalls()
            next_action = self.birdUpdate()
            for k, v in self.q.items():
                print(k, v)

            pygame.display.update()

if __name__ == "__main__":
    FlappyBird().run()
