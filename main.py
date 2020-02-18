import sys
import pygame
from pygame import display, event, image, time, draw, Rect
from pygame import transform, key, font
import pygame.locals
import random
from config import *
pygame.init()

# load_tiles - separates a spritesheet into sprites and optionally scales them


def load_tiles(filename, width, height, scalex=1, scaley=1):
    img = image.load(filename).convert_alpha()
    image_width, image_height = img.get_size()
    tile_table = []
    for tile_x in range(0, image_width//width):
        for tile_y in range(0, image_height//height):
            rect = (tile_x*width, tile_y*height, width, height)
            tile_table.append(transform.scale(
                img.subsurface(rect), (scalex*width, scaley*height)))
    return tile_table


screen = display.set_mode(size)
display.set_caption(title)
clock = time.Clock()
timer = 0

p1Score = 0
p2Score = 0
p1Lvl = 4
p2Lvl = 4
Lvl = 4

p1SpawnMsg = bigfont.render(p1SpawnText, True, black)
p1SpawnMsgRect = p1SpawnMsg.get_rect()
p1SpawnMsgRect.center = ((width//2), (height//2))

p2SpawnMsg = bigfont.render(p2SpawnText, True, black)
p2SpawnMsgRect = p2SpawnMsg.get_rect()
p2SpawnMsgRect.center = ((width//2), (height//2))


mspawners = []
fspawners = []
shark = object

playerSprites = [[], []]
playerSprites[0] += load_tiles("player1.png", 16, 16, 2, 2)
playerSprites[1] += load_tiles("player2.png", 16, 16, 2, 2)

shipSprites = [
    transform.scale(image.load("ship1.png").convert_alpha(), (32, 32)),
    transform.scale(image.load("ship2.png").convert_alpha(), (32, 32))
]

fixedObstacleSprites = []
fixedObstacleSprites += load_tiles("huts.png", 16, 16, 3, 3)

sharkAnim = [
    transform.scale(image.load("shark1.png").convert_alpha(), (32, 32)),
    transform.scale(image.load("shark2.png").convert_alpha(), (32, 32))
]

bg = image.load("map.png")
bg = transform.scale(bg, (width, height))


class ObstacleSpawner:
    curtimer = 0
    frame = 0

    def __init__(self, x, y, mobile=False, dir=1):
        self.x = x
        self.y = y
        self.obstaclelist = []
        self.mobile = mobile
        self.dir = dir
        self.crossed = False

    def spawn(self, num=1, speed=0):
        if (self.mobile):
            if self.dir == 1:
                o = Obstacle(speed, -60, self.y)
            else:
                o = Obstacle(-speed, width + 60, self.y)
            o.setimg(shipSprites[self.frame])
            self.obstaclelist.append(o)
        else:
            for i in range(num):
                x_pos = random.randrange(64, width - 64)
                if (self.y > p1spawny - 32) or (self.y < p2spawny + 32):
                    while (x_pos > p1spawnx - 32) and (x_pos < p1spawnx + 32):
                        x_pos = random.randrange(64, width - 64)
                o = Obstacle(0, x_pos, self.y)
                o.setimg(fixedObstacleSprites[random.randrange(
                    len(fixedObstacleSprites))])
                self.obstaclelist.append(o)

    def update(self, p):
        if self.crossed is False:
            if (p.num == 1):
                if (self.y > p.y + 5):
                    global p1Score
                    if (self.mobile):
                        p1Score += 10
                    else:
                        p1Score += 5
                    self.crossed = True
            else:
                if (self.y < p.y - 10):
                    global p2Score
                    if (self.mobile):
                        p2Score += 10
                    else:
                        p2Score += 5
                    self.crossed = True

        if (self.mobile):
            if (timer - self.curtimer >= FPS):
                self.frame = (self.frame + 1) % 2
                for o in self.obstaclelist:
                    o.setimg(shipSprites[self.frame])
                self.curtimer = timer
        for o in self.obstaclelist:
            o.update(p)
            if o.rect.bottom < -128 or o.rect.top > height+128:
                self.obstaclelist.pop(self.obstaclelist.index(o))
            if o.rect.right < -128 or o.rect.left > width+128:
                self.obstaclelist.pop(self.obstaclelist.index(o))

    def draw(self):
        for o in self.obstaclelist:
            o.draw()


# Drawable : Base class for all objects with a sprite


class Drawable:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        self.spr = None

    def setimg(self, img):
        self.spr = img
        # Reduce the size of hitboxes to make things "fairer"
        self.rect = self.spr.get_rect().inflate(-10, -20)
        self.rect.move_ip(self.x, self.y)

    def draw(self):
        if (self.spr is not None):
            screen.blit(self.spr, self.rect)


# Obstacle Class


class Obstacle(Drawable):
    def __init__(self, speed, x=0, y=0):
        super().__init__(x, y)
        self.speed = speed

    def update(self, p):
        global gameStatus
        if self.rect.colliderect(p.rect):
            gameStatus = "hit"
        self.rect = self.rect.move([self.speed, 0])
        self.x += self.speed


# Special Shark Class


class Shark(Obstacle):
    def update(self, p):
        super().update(p)
        if self.rect.left < 40:
            self.setimg(sharkAnim[1])
            self.speed = -self.speed
        if self.rect.right > width - 80:
            self.setimg(sharkAnim[0])
            self.speed = -self.speed


# Player Class


class Player(Drawable):
    def __init__(self, x, y, pnum):
        super().__init__(x=x, y=y)
        self.num = pnum
        self.speed = [0, 0]

    def update(self, keyStates):
        global gameStatus
        global p1Lvl, p2Lvl
        upPressed = downPressed = leftPressed = rightPressed = 0

        # Change which keys are bound based on player
        if (self.num == 1):
            kup = pygame.K_UP
            kdown = pygame.K_DOWN
            kleft = pygame.K_LEFT
            kright = pygame.K_RIGHT
        else:
            kup = pygame.K_w
            kdown = pygame.K_s
            kleft = pygame.K_a
            kright = pygame.K_d

        if keyStates[kup]:
            upPressed = 1
        if keyStates[kdown]:
            downPressed = 1
        if keyStates[kleft]:
            leftPressed = 1
        if keyStates[kright]:
            rightPressed = 1

        if (upPressed):
            self.speed[1] -= 4
            self.setimg(playerSprites[self.num-1][0])
        elif (downPressed):
            self.speed[1] += 4
            self.setimg(playerSprites[self.num-1][2])
        elif (leftPressed):
            self.speed[0] -= 4
            self.setimg(playerSprites[self.num-1][3])
        elif (rightPressed):
            self.speed[0] += 4
            self.setimg(playerSprites[self.num-1][1])

        # Stop player when it reaches the edges of screen
        if (self.rect.top+self.speed[1] < 0 or
                self.rect.bottom+self.speed[1] > height):
            self.speed[1] = 0
        if (self.rect.left+self.speed[0] < 0 or
                self.rect.right+self.speed[0] > width):
            self.speed[0] = 0
        self.rect = self.rect.move(self.speed)
        self.x += self.speed[0]
        self.y += self.speed[1]
        self.speed = [0, 0]

        # Swap players if they reach the other side
        if (self.num == 1):
            if (self.y < 20):
                gameStatus = "swap"
        else:
            if (self.y > height - 64):
                gameStatus = "swap"


# init - what needs to be done at the start of every round


def init():
    global mspawners, fspawners, shark
    mspawners = [
        ObstacleSpawner(-60, 50, 1, 1),
        ObstacleSpawner(-60, 96, 1, -1),
        ObstacleSpawner(-60, 240, 1, 1),
        ObstacleSpawner(-60, 270, 1, -1),
        ObstacleSpawner(-60, 430, 1, 1),
        ObstacleSpawner(-60, 480, 1, -1),
        ObstacleSpawner(-60, 620, 1, 1),
        ObstacleSpawner(-60, 665, 1, -1),
    ]

    # The shark is faster than everything else
    shark = Shark(sharkSpdMultiplier*Lvl, 40, 350)
    shark.setimg(sharkAnim[1])

    fspawners = [
        ObstacleSpawner(-60, -8),
        ObstacleSpawner(-60, 148),
        ObstacleSpawner(-60, 310),
        ObstacleSpawner(-60, 380),
        ObstacleSpawner(-60, 540),
        ObstacleSpawner(-60, 700)
    ]

    # Spawn Lvl number of fixed obstacles in a line
    for s in fspawners:
        s.spawn(Lvl)

    # Set a random spawning rate for moving obstacles
    for ind, s in enumerate(mspawners):
        time.set_timer(pygame.USEREVENT+ind,
                       random.randrange(6000//Lvl, 12000//Lvl))


init()
p = Player(p1spawnx, p1spawny, 1)
p.setimg(playerSprites[0][0])
turnOf = 1
gameStatus = "run"

# Main game loop begins here
while True:

    clock.tick(FPS)  # Run the game at FPS defined in config
    timer += 1

    for event in pygame.event.get():
        # Exit if window is closed
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        # Spawn a moving obstacle with speed Lvl
        if event.type >= pygame.USEREVENT and event.type <= pygame.USEREVENT+8:
            mspawners[event.type - pygame.USEREVENT].spawn(1, Lvl)

    if gameStatus == "swap" or gameStatus == "hit":  # switch when reach end
        gameStatus = "run"
        init()

        if (turnOf == 1):
            del p
            p = Player(p2spawnx, p2spawny, 2)
            p.setimg(playerSprites[1][2])
            turnOf = 2
            Lvl = p2Lvl
            p1Score -= timer//FPS   # Time penalty
            screen.blit(p2SpawnMsg, p2SpawnMsgRect)
            display.flip()
            time.wait(2000)
            timer = 0
            continue
        else:
            del p
            p = Player(p1spawnx, p1spawny, 1)
            p.setimg(playerSprites[0][0])
            turnOf = 1
            Lvl = p1Lvl
            p2Score -= timer//FPS   # Time penalty
            # Decide winner
            if (p2Score > p1Score):
                p2Lvl += 1
                win = 2
            else:
                p1Lvl += 1
                win = 1
            p1Score = p2Score = 0
            winMsg = bigfont.render(
                "PLAYER " + str(win) + " WINS", True, black)
            winMsgRect = winMsg.get_rect()
            winMsgRect.center = p1SpawnMsgRect.center
            winMsgRect.centery -= 100
            screen.blit(winMsg, winMsgRect)
            screen.blit(p1SpawnMsg, p1SpawnMsgRect)
            display.flip()
            time.wait(2000)
            timer = 0
            continue

    keysPressed = key.get_pressed()
    p.update(keysPressed)

    for obs in mspawners:
        obs.update(p)
    for s in fspawners:
        s.update(p)
    shark.update(p)
    screen.fill(black)

    screen.blit(bg, (0, 0))

    for obs in mspawners:
        obs.draw()
    for s in fspawners:
        s.draw()
    shark.draw()
    p.draw()
    p1ScoreMsg = regfont.render("PLAYER 1 : " + str(p1Score), True, black)
    p2ScoreMsg = regfont.render("PLAYER 2 : " + str(p2Score), True, black)
    timeMsg = regfont.render("TIME : " + str(timer//FPS), True, black)

    screen.blit(p2ScoreMsg, (10, 60))
    screen.blit(p1ScoreMsg, (10, height-100))
    screen.blit(timeMsg, (850, 60))

    display.flip()

pygame.quit()
exit(0)
