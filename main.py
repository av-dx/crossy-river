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


screen = display.set_mode(SIZE)
display.set_caption(TITLE)
clock = time.Clock()
timer = 0

p1score = 0
p2score = 0
p1lvl = 4
p2lvl = 4
lvl = 4

p1_spawn_msg = bigfont.render(P1SPAWNTXT, True, BLACK)
p1_spawn_msg_rect = p1_spawn_msg.get_rect()
p1_spawn_msg_rect.center = ((WIDTH//2), (HEIGHT//2))

p2_spawn_msg = bigfont.render(P2SPAWNTXT, True, BLACK)
p2_spawn_msg_rect = p2_spawn_msg.get_rect()
p2_spawn_msg_rect.center = ((WIDTH//2), (HEIGHT//2))


mspawners = []
fspawners = []
shark = object

player_sprites = [[], []]
player_sprites[0] += load_tiles("player1.png", 16, 16, 2, 2)
player_sprites[1] += load_tiles("player2.png", 16, 16, 2, 2)

ship_sprites = [
    transform.scale(image.load("ship1.png").convert_alpha(), (32, 32)),
    transform.scale(image.load("ship2.png").convert_alpha(), (32, 32))
]

fixed_obstacle_sprites = []
fixed_obstacle_sprites += load_tiles("huts.png", 16, 16, 3, 3)

shark_sprites = [
    transform.scale(image.load("shark1.png").convert_alpha(), (32, 32)),
    transform.scale(image.load("shark2.png").convert_alpha(), (32, 32))
]

bg = image.load("map.png")
bg = transform.scale(bg, (WIDTH, HEIGHT))


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
                o = Obstacle(-speed, WIDTH + 60, self.y)
            o.setimg(ship_sprites[self.frame])
            self.obstaclelist.append(o)
        else:
            for i in range(num):
                x_pos = random.randrange(64, WIDTH - 64)
                # Check to make sure we dont spawn on top of player!
                if (self.y > P1SPAWNY - 32) or (self.y < P2SPAWNY + 32):
                    while (x_pos > P1SPAWNX - 32) and (x_pos < P1SPAWNX + 32):
                        x_pos = random.randrange(64, WIDTH - 64)
                o = Obstacle(0, x_pos, self.y)
                # Select a random sprite from huts.png
                o.setimg(fixed_obstacle_sprites[random.randrange(
                    len(fixed_obstacle_sprites))])
                self.obstaclelist.append(o)

    def update(self, p):
        if self.crossed is False:
            if (p.num == 1):
                if (self.y > p.y + 5):
                    global p1score
                    if (self.mobile):
                        p1score += 10
                    else:
                        p1score += 5
                    self.crossed = True
            else:
                if (self.y < p.y - 10):
                    global p2score
                    if (self.mobile):
                        p2score += 10
                    else:
                        p2score += 5
                    self.crossed = True

        if (self.mobile):
            if (timer - self.curtimer >= FPS):
                self.frame = (self.frame + 1) % 2
                for o in self.obstaclelist:
                    o.setimg(ship_sprites[self.frame])
                self.curtimer = timer
        for o in self.obstaclelist:
            o.update(p)
            if o.rect.bottom < -128 or o.rect.top > HEIGHT+128:
                self.obstaclelist.pop(self.obstaclelist.index(o))
            if o.rect.right < -128 or o.rect.left > WIDTH+128:
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
        global game_status
        if self.rect.colliderect(p.rect):
            game_status = "hit"
        self.rect = self.rect.move([self.speed, 0])
        self.x += self.speed


# Special Shark Class


class Shark(Obstacle):
    def update(self, p):
        super().update(p)
        if self.rect.left < 40:
            self.setimg(shark_sprites[1])
            self.speed = -self.speed
        if self.rect.right > WIDTH - 80:
            self.setimg(shark_sprites[0])
            self.speed = -self.speed


# Player Class


class Player(Drawable):
    def __init__(self, x, y, pnum):
        super().__init__(x=x, y=y)
        self.num = pnum
        self.speed = [0, 0]

    def update(self, keyStates):
        global game_status
        global p1lvl, p2lvl
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
            self.setimg(player_sprites[self.num-1][0])
        elif (downPressed):
            self.speed[1] += 4
            self.setimg(player_sprites[self.num-1][2])
        elif (leftPressed):
            self.speed[0] -= 4
            self.setimg(player_sprites[self.num-1][3])
        elif (rightPressed):
            self.speed[0] += 4
            self.setimg(player_sprites[self.num-1][1])

        # Stop player when it reaches the edges of screen
        if (self.rect.top+self.speed[1] < 0 or
                self.rect.bottom+self.speed[1] > HEIGHT):
            self.speed[1] = 0
        if (self.rect.left+self.speed[0] < 0 or
                self.rect.right+self.speed[0] > WIDTH):
            self.speed[0] = 0
        self.rect = self.rect.move(self.speed)
        self.x += self.speed[0]
        self.y += self.speed[1]
        self.speed = [0, 0]

        # Swap players if they reach the other side
        if (self.num == 1):
            if (self.y < 20):
                game_status = "swap"
        else:
            if (self.y > HEIGHT - 64):
                game_status = "swap"


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
    shark = Shark(SHARKSPDMULTIPLIER*lvl, 40, 350)
    shark.setimg(shark_sprites[1])

    fspawners = [
        ObstacleSpawner(-60, -8),
        ObstacleSpawner(-60, 148),
        ObstacleSpawner(-60, 310),
        ObstacleSpawner(-60, 380),
        ObstacleSpawner(-60, 540),
        ObstacleSpawner(-60, 700)
    ]

    # Spawn lvl number of fixed obstacles in a line
    for s in fspawners:
        s.spawn(lvl)

    # Set a random spawning rate for moving obstacles
    for ind, s in enumerate(mspawners):
        time.set_timer(pygame.USEREVENT+ind,
                       random.randrange(6000//lvl, 12000//lvl))


init()
p = Player(P1SPAWNX, P1SPAWNY, 1)
p.setimg(player_sprites[0][0])
turn_of = 1
game_status = "run"

# Main game loop begins here
while True:

    clock.tick(FPS)  # Run the game at FPS defined in config
    timer += 1

    for event in pygame.event.get():
        # Exit if window is closed
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        # Spawn a moving obstacle with speed lvl
        if event.type >= pygame.USEREVENT and event.type <= pygame.USEREVENT+8:
            mspawners[event.type - pygame.USEREVENT].spawn(1, lvl)

    if game_status == "swap" or game_status == "hit":  # switch when reach end
        game_status = "run"
        init()

        if (turn_of == 1):
            del p
            p = Player(P2SPAWNX, P2SPAWNY, 2)
            p.setimg(player_sprites[1][2])
            turn_of = 2
            lvl = p2lvl
            p1score -= timer//FPS   # Time penalty
            screen.blit(p2_spawn_msg, p2_spawn_msg_rect)
            display.flip()
            time.wait(2000)
            timer = 0
            continue
        else:
            del p
            p = Player(P1SPAWNX, P1SPAWNY, 1)
            p.setimg(player_sprites[0][0])
            turn_of = 1
            lvl = p1lvl
            p2score -= timer//FPS   # Time penalty
            # Decide winner
            if (p2score > p1score):
                p2lvl += 1
                win = 2
            else:
                p1lvl += 1
                win = 1
            p1score = p2score = 0
            winMsg = bigfont.render(
                "PLAYER " + str(win) + " WINS", True, BLACK)
            winMsgRect = winMsg.get_rect()
            winMsgRect.center = p1_spawn_msg_rect.center
            winMsgRect.centery -= 100
            screen.blit(winMsg, winMsgRect)
            screen.blit(p1_spawn_msg, p1_spawn_msg_rect)
            display.flip()
            time.wait(2000)
            timer = 0
            continue

    keysPressed = key.get_pressed()
    p.update(keysPressed)

    # Update - begin
    for obs in mspawners:
        obs.update(p)
    for s in fspawners:
        s.update(p)
    shark.update(p)

    # Draw - begin
    screen.fill(BLACK)
    screen.blit(bg, (0, 0))
    for obs in mspawners:
        obs.draw()
    for s in fspawners:
        s.draw()
    shark.draw()
    p.draw()
    p1ScoreMsg = regfont.render("PLAYER 1 : " + str(p1score), True, BLACK)
    p2ScoreMsg = regfont.render("PLAYER 2 : " + str(p2score), True, BLACK)
    timeMsg = regfont.render("TIME : " + str(timer//FPS), True, BLACK)

    screen.blit(p2ScoreMsg, (10, 60))
    screen.blit(p1ScoreMsg, (10, HEIGHT-100))
    screen.blit(timeMsg, (850, 60))

    display.flip()

pygame.quit()
exit(0)
