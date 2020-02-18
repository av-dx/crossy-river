import pygame
from pygame import display, event, image, time, draw, Rect
from pygame import transform, key, font
import pygame.locals
pygame.init()

SIZE = WIDTH, HEIGHT = 1024, 768
FPS = 60
TITLE = "Crossy River"
bigfont = font.Font("Gamer.ttf", 100)
regfont = font.Font("Gamer.ttf", 40)

P1SPAWNX = WIDTH/2-24
P1SPAWNY = HEIGHT-64
P2SPAWNX = WIDTH/2-24
P2SPAWNY = 0

SHARKSPDMULTIPLIER = 4

BLUE = [0, 100, 255]
BLACK = [0, 0, 0]
WHITE = [200, 200, 200]

GAMEOVERTXT = "You Lose"
P1SPAWNTXT = "PLAYER 1 : GET READY!"
P2SPAWNTXT = "PLAYER 2 : GET READY!"
