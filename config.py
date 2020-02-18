import pygame
from pygame import display, event, image, time, draw, Rect
from pygame import transform, key, font
import pygame.locals
pygame.init()

size = width, height = 1024, 768
title = "Crossy River"
bigfont = font.Font(None, 100)
regfont = font.Font(None, 40)

p1spawnx = width/2-24
p1spawny = height-64
p2spawnx = width/2-24
p2spawny = 0

sharkSpdMultiplier = 4

blue = [0, 100, 255]
black = [0, 0, 0]
white = [200, 200, 200]
red = [255, 0, 0]
green = [0, 255, 0]

gameOverText = "You Lose"
p1SpawnText = "PLAYER 1 : GET READY!"
p2SpawnText = "PLAYER 2 : GET READY!"
