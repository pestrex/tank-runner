import random
import os
from typing import List

import pygame as pg

# global variables
# game constants
OBS_ODDS = 80  # chances an obstacle appears
ClOUD_ODDS = 200  # chances a cloud appears
OBS_RELOAD = 10  # frames between new obstacles
ADD_SCORE = 15  # every half second the player earn 1 point
SCREENRECT = pg.Rect(0, 0, 640, 480)

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


class Player(pg.sprite.Sprite):
    FG = -.8  # gravity force
    itr = 15
    jump_height = itr
    images: List[pg.Surface] = []

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[1]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.rect.x = -200
        self.rect.y = 295
        self.dx = 2

    def jump(self, jump):
        # this function make the jump animation of the player
        if jump:
            # if the player pressed space bar
            self.jump_height += self.FG
            self.rect.move_ip(0, -self.jump_height)
            if self.rect.y > 295:
                self.rect.y = 295
                self.jump_height = self.itr
                return False

        if self.jump_height == self.itr:
            return False
        return True

    def start(self):
        if self.rect.x < 60:
            self.rect.move_ip(self.dx, 0)
        else:
            self.rect.x = 60


class MovableObj(pg.sprite.Sprite):
    images: List[pg.Surface] = []

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self._rect = None
        self._speed = 0

    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.left < -self.rect.width:
            self.kill()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        self._rect = rect


class Obstacle(MovableObj):
    s = -5

    def __init__(self, *groups):
        MovableObj.__init__(self, *groups)
        self.rect = self.image.get_rect(midbottom=SCREENRECT.bottomright)
        self.rect.y = 322
        self.speed = self.s


class Floor(MovableObj):
    s = -5

    def __init__(self, *groups):
        MovableObj.__init__(self, *groups)
        self.rect = self.image.get_rect(midbottom=SCREENRECT.bottomright)
        self.rect.y = 350
        self.speed = self.s


class Cloud(MovableObj):
    s = -1

    def __init__(self, *groups):
        MovableObj.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = pg.Rect(SCREENRECT.width, random.randint(50, 150), self.image.get_rect().height,
                            self.image.get_rect().width)
        self.speed = self.s


def main():
    # pygame setup
    pg.init()
    screen = pg.display.set_mode(SCREENRECT.size, pg.SCALED)
    pg.display.set_caption('Tank Runner')
    pg.mouse.set_visible(0)
    clock = pg.time.Clock()

    # load images to the sprite classes
    img = load_image('player1.gif')
    Player.images = [img, pg.transform.flip(img, 1, 0)]
    Obstacle.images = [load_image('obj_spike.jpg')]
    Floor.images = [load_image('floor2.jpg').convert()]
    Cloud.images = [load_image('cloud.jpg').convert()]

    # groups of object
    obstacles = pg.sprite.Group()
    floors = pg.sprite.Group()
    clouds = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()
    lastfloor = pg.sprite.GroupSingle()
    lastcloud = pg.sprite.GroupSingle()

    # decorate the game window
    icon = pg.transform.scale(Player.images[1], (32, 32))
    pg.display.set_icon(icon)

    # game variables
    global score
    score = 0  # the score increases by 1 every second
    jumping = False  # if True the player jumps
    starting = True
    obstacle_reload = OBS_RELOAD
    add_score = ADD_SCORE

    # background of the game
    background = pg.Surface(SCREENRECT.size)
    background.convert()
    background.fill('white')

    # show the score on screen
    text = "Score: " + str(score)
    score_font = pg.font.Font(None, 30)
    score_text = score_font.render(text, 0, (200, 60, 80))

    # initialize starting sprites
    Cloud(clouds, all, lastcloud)
    Floor(floors, all, lastfloor)
    player = Player(all)
    running = True

    # Menu's variables
    # Starting game
    font = pg.font.SysFont('Arial', 30)
    begin_text = font.render('Press the space bar to begin', 0, 'black')

    # End of game
    end_font = pg.font.Font(None, 80)
    exit_font = pg.font.SysFont('Arial', 20)
    game_over = end_font.render('Game Over', 0, (200, 60, 80))
    restart_exit = exit_font.render('Press E to exit.', 0, 'black')

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # tracks when the player press any key
        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)
        # update all the sprites
        all.update()

        # generates clouds
        if not int(random.random() * ClOUD_ODDS):
            if lastcloud:
                if lastcloud.sprite.rect.x + lastcloud.sprite.rect.width + 50 < SCREENRECT.width:
                    Cloud(clouds, all, lastcloud)
            else:
                Cloud(clouds, all, lastcloud)

        # generates path
        if lastfloor:
            if lastfloor.sprite.rect.x + lastfloor.sprite.rect.width < SCREENRECT.width:
                Floor(floors, all, lastfloor)

        if starting:
            if keystate[pg.K_SPACE]:
                starting = False

            screen.blit(background, (0, 0))
            screen.blit(Player.images[1], (280, 150))
            screen.blit(begin_text, (180, SCREENRECT.height // 2))

        elif player.alive():
            player.start()

            # generates clouds
            if not int(random.random() * ClOUD_ODDS):
                if lastcloud:
                    if lastcloud.sprite.rect.x + lastcloud.sprite.rect.width + 50 < SCREENRECT.width:
                        Cloud(clouds, all, lastcloud)
                else:
                    Cloud(clouds, all, lastcloud)

            # generates path
            if lastfloor:
                if lastfloor.sprite.rect.x + lastfloor.sprite.rect.width < SCREENRECT.width:
                    Floor(floors, all, lastfloor)

            if player.rect.x == 60:
                # when the space bar is pressed the player jumps
                if keystate[pg.K_SPACE]:
                    jumping = True
                jumping = player.jump(jumping)

                # create new obstacles
                if obstacle_reload:
                    obstacle_reload = obstacle_reload - 1
                elif not int(random.random() * OBS_ODDS):
                    Obstacle(obstacles, all)
                    obstacle_reload = OBS_RELOAD

                # increment the score
                if add_score:
                    add_score = add_score - 1
                else:
                    score += 1
                    text = "Score: " + str(score)
                    score_text = score_font.render(text, 0, (200, 60, 80))
                    add_score = ADD_SCORE

                # Detect collisions between aliens and players.
                for obstacles in pg.sprite.spritecollide(player, obstacles, 1):
                    player.kill()

            screen.blit(background, (0, 0))  # background into the screen
            screen.blit(score_text, (10, 10))  # score text into the screen

        else:
            final_score = font.render('Final score: ' + str(score), 0, 'black')

            if keystate[pg.K_r]:
                starting = True
                player = Player(all)
                score = 0
            if keystate[pg.K_e]:
                running = False

            screen.blit(background, (0, 0))
            screen.blit(game_over, (180, 220))
            screen.blit(final_score, (250, 420))
            screen.blit(restart_exit, (272, 280))

        # draw() to display all the elements on the screen, then update the display
        dirty = all.draw(screen)
        pg.display.update(dirty)

        clock.tick(30)  # limits FPS to 60

    pg.quit()


if __name__ == '__main__':
    main()
    pg.quit()
