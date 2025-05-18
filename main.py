import pygame
from pygame.locals import *
import sys
import random
import numpy
import threading
from music import MusicManager
from tkinter import Tk, Button

# freq, size, channel, buffsize
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

soundtrack = ["background_village.wav", "battle_music.wav", "gameover.wav"]
swordtrack = [pygame.mixer.Sound("sword1.wav"), pygame.mixer.Sound("sword2.wav")]
fsound = pygame.mixer.Sound("fireball_sound.wav")
hit = pygame.mixer.Sound("enemy_hit.wav")

mmanager = MusicManager()
mmanager.playsoundtrack(soundtrack[0], -1, 0.05)

vec = pygame.math.Vector2
HEIGHT, WIDTH = 600, 1100
ACC, FRIC, FPS = 0.3, -0.10, 60
FPS_CLOCK = pygame.time.Clock()
game_over = False

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

color_light = (170, 170, 170)
color_dark = (100, 100, 100)
color_white = (255, 255, 255)

headingfont = pygame.font.SysFont("Verdana", 40)
regularfont = pygame.font.SysFont('Corbel', 25)
smallerfont = pygame.font.SysFont('Corbel', 16)
text = regularfont.render('LOAD', True, color_light)

SCALE = 1.5

def scale_img(img, factor=SCALE):
    w, h = img.get_size()
    return pygame.transform.smoothscale(img, (int(w * factor), int(h * factor)))

# Run animation for the RIGHT
run_ani_R = [
    scale_img(pygame.image.load("Player_Sprite_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite2_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite3_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite4_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite5_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite6_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite_R.png").convert_alpha())
]

run_ani_L = [
    scale_img(pygame.image.load("Player_Sprite_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite2_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite3_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite4_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite5_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite6_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite_L.png").convert_alpha())
]

# Attack animation for the RIGHT
attack_ani_R = [
    scale_img(pygame.image.load("Player_Sprite_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack2_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack2_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack3_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack3_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack4_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack4_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack5_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack5_R.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite_R.png").convert_alpha())
]

# Attack animation for the LEFT
attack_ani_L = [
    scale_img(pygame.image.load("Player_Sprite_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack2_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack2_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack3_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack3_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack4_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack4_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack5_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Attack5_L.png").convert_alpha()),
    scale_img(pygame.image.load("Player_Sprite_L.png").convert_alpha())
]

# Animations for the Health Bar
health_ani = [
    scale_img(pygame.image.load("heart0.png").convert_alpha()),
    scale_img(pygame.image.load("heart.png").convert_alpha()),
    scale_img(pygame.image.load("heart2.png").convert_alpha()),
    scale_img(pygame.image.load("heart3.png").convert_alpha()),
    scale_img(pygame.image.load("heart4.png").convert_alpha()),
    scale_img(pygame.image.load("heart5.png").convert_alpha())
]

class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bgimage = pygame.image.load("Background.png").convert_alpha()
        self.bgimage = pygame.transform.smoothscale(self.bgimage, (WIDTH, HEIGHT))
        self.rectBGimg = self.bgimage.get_rect()
        self.bgY = 0
        self.bgX = 0

    def render(self):
        displaysurface.blit(self.bgimage, (self.bgX, self.bgY))

class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Ground.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (WIDTH, 100))
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, HEIGHT - 100))

    def render(self):
        displaysurface.blit(self.image, self.rect)

class Item(pygame.sprite.Sprite):
    def __init__(self, itemtype):
        super().__init__()
        if itemtype == 1:
            self.image = scale_img(pygame.image.load("heart.png").convert_alpha())
        elif itemtype == 2:
            self.image = scale_img(pygame.image.load("coin.png").convert_alpha())
        self.rect = self.image.get_rect()
        self.type = itemtype
        self.posx = 0
        self.posy = 0

    def render(self):
        self.rect.x = self.posx
        self.rect.y = self.posy
        displaysurface.blit(self.image, self.rect)

    def update(self):
        hits = pygame.sprite.spritecollide(self, Playergroup, False)
        if hits:
            if player.health < 5 and self.type == 1:
                player.health += 1
                health.image = health_ani[player.health]
                self.kill()
            if self.type == 2:
                handler.money += 1
                self.kill()

class FireBall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.direction = player.direction
        if self.direction == "RIGHT":
            self.image = scale_img(pygame.image.load("fireball1_R.png").convert_alpha())
        else:
            self.image = scale_img(pygame.image.load("fireball1_L.png").convert_alpha())
        self.rect = self.image.get_rect(center=player.rect.center)

    def fire(self):
        player.magic_cooldown = 0
        if -10 < self.rect.x < WIDTH + 10:
            displaysurface.blit(self.image, self.rect)
            if self.direction == "RIGHT":
                self.rect.move_ip(18, 0)
            else:
                self.rect.move_ip(-18, 0)
        else:
            self.kill()
            player.magic_cooldown = 1
            player.attacking = False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = run_ani_R[0]
        self.rect = self.image.get_rect()
        self.pos = vec((WIDTH // 2 - self.rect.width // 2, HEIGHT - 220))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"
        self.jumping = False
        self.running = False
        self.move_frame = 0
        self.attacking = False
        self.cooldown = False
        self.immune = False
        self.special = False
        self.experiance = 0
        self.attack_frame = 0
        self.health = 5
        self.magic_cooldown = 1
        self.mana = 0
        self.slash = 0

    def move(self):
        if cursor.wait == 1:
            return
        self.acc = vec(0, 0.5)
        if abs(self.vel.x) > 0.3:
            self.running = True
        else:
            self.running = False
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[KEY_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[KEY_RIGHT]:
            self.acc.x = ACC
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        # Keep player within screen bounds
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.x > WIDTH - self.rect.width:
            self.pos.x = WIDTH - self.rect.width
        self.rect.topleft = self.pos

    def gravity_check(self):
        hits = pygame.sprite.spritecollide(player, ground_group, False)
        if self.vel.y > 0:
            if hits:
                lowest = hits[0]
                if self.rect.bottom >= lowest.rect.top:
                    self.rect.y = lowest.rect.top - self.rect.height + 1
                    self.pos.y = lowest.rect.top - self.rect.height + 1
                    self.vel.y = 0
                    self.jumping = False

    def update(self):
        if cursor.wait == 1:
            return
        if self.move_frame > 6:
            self.move_frame = 0
            return
        if self.jumping == False and self.running == True:
            if self.vel.x > 0:
                self.image = run_ani_R[self.move_frame]
                self.direction = "RIGHT"
            else:
                self.image = run_ani_L[self.move_frame]
                self.direction = "LEFT"
            self.move_frame += 1
        if abs(self.vel.x) < 0.2 and self.move_frame != 0:
            self.move_frame = 0
            if self.direction == "RIGHT":
                self.image = run_ani_R[self.move_frame]
            elif self.direction == "LEFT":
                self.image = run_ani_L[self.move_frame]

    def attack(self):
        if cursor.wait == 1:
            return
        if self.attack_frame > 10:
            self.attack_frame = 0
            self.attacking = False
        if self.attack_frame == 0:
            mmanager.playsound(swordtrack[self.slash], 0.05)
            self.slash += 1
            if self.slash >= 2:
                self.slash = 0
        if self.direction == "RIGHT":
            self.image = attack_ani_R[self.attack_frame]
        elif self.direction == "LEFT":
            self.correction()
            self.image = attack_ani_L[self.attack_frame]
        self.attack_frame += 1

    def jump(self):
        self.rect.x += 1
        hits = pygame.sprite.spritecollide(self, ground_group, False)
        self.rect.x -= 1
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -12

    def correction(self):
        if self.attack_frame == 1:
            self.pos.x -= 20
        if self.attack_frame == 10:
            self.pos.x += 20

    def player_hit(self):
        global game_over
        if self.cooldown == False:
            self.cooldown = True
            pygame.time.set_timer(hit_cooldown, 1000)
            self.health = self.health - 1
            health.image = health_ani[self.health]
            if self.health <= 0:
                self.kill()
                mmanager.stop()
                mmanager.playsoundtrack(soundtrack[2], -1, 0.1)
                pygame.display.update()
                game_over = True

class Bolt(pygame.sprite.Sprite):
    def __init__(self, x, y, d):
        super().__init__()
        self.image = scale_img(pygame.image.load("bolt.png").convert_alpha())
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 20
        self.direction = d
        if self.direction == 0:
            self.rect.x += 20
        else:
            self.rect.x -= 20

    def fire(self):
        if -10 < self.rect.x < WIDTH + 10:
            displaysurface.blit(self.image, self.rect)
            if self.direction == 0 and cursor.wait == 0:
                self.rect.move_ip(15, 0)
            elif self.direction == 1 and cursor.wait == 0:
                self.rect.move_ip(-15, 0)
        else:
            self.kill()
        hits = pygame.sprite.spritecollide(self, Playergroup, False)
        if hits:
            player.player_hit()
            self.kill()

class Enemy2(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.direction = random.randint(0, 1)
        if self.direction == 0:
            self.image = scale_img(pygame.image.load("enemy2.png").convert_alpha())
        else:
            self.image = scale_img(pygame.image.load("enemy2_L.png").convert_alpha())
        self.rect = self.image.get_rect()
        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.wait = 0
        self.wait_status = False
        self.turning = 0
        # Increase speed for Hell Dungeon
        if handler.world == 3:
            self.vel.x = random.randint(5, 10) / 1.2
        else:
            self.vel.x = random.randint(2, 6) / 3
        self.mana = random.randint(2, 3)
        if self.direction == 0:
            self.pos.x = 0
        else:
            self.pos.x = WIDTH - self.rect.width
        self.pos.y = HEIGHT - 100 - self.rect.height

    def turn(self):
        if self.wait > 0:
            self.wait -= 1
            return
        elif int(self.wait) <= 0:
            self.turning = 0
        if (self.direction):
            self.direction = 0
            self.image = scale_img(pygame.image.load("enemy2.png").convert_alpha())
        else:
            self.direction = 1
            self.image = scale_img(pygame.image.load("enemy2_L.png").convert_alpha())

    def move(self):
        if cursor.wait == 1:
            return
        if self.turning == 1:
            self.turn()
        if self.pos.x >= (WIDTH - 20):
            self.direction = 1
        elif self.pos.x <= 0:
            self.direction = 0
        if self.wait > 60:
            self.wait_status = True
        elif int(self.wait) <= 0:
            self.wait_status = False
        if (self.direction_check()):
            self.turn()
            self.wait = 90
            self.turning = 1
        if self.wait_status == True:
            rand_num = numpy.random.uniform(0, 60)
            if int(rand_num) == 30:
                bolt = Bolt(self.pos.x, self.pos.y, self.direction)
                Bolts.add(bolt)
            self.wait -= 1
        elif self.direction == 0:
            self.pos.x += self.vel.x
            self.wait += self.vel.x
        elif self.direction == 1:
            self.pos.x -= self.vel.x
            self.wait += self.vel.x
        self.rect.topleft = self.pos

    def direction_check(self):
        if (player.pos.x - self.pos.x < 0 and self.direction == 0):
            return 1
        if (player.pos.x - self.pos.x > 0 and self.direction == 1):
            return 1

    def update(self):
        hits = pygame.sprite.spritecollide(self, Playergroup, False)
        f_hits = pygame.sprite.spritecollide(self, Fireballs, False)
        if hits and player.attacking == True or f_hits:
            self.kill()
            mmanager.playsound(hit, 0.05)
            handler.dead_enemy_count += 1
            if player.mana < 100:
                player.mana += self.mana
            player.experiance += 1
            rand_num = numpy.random.uniform(0, 100)
            item_no = 0
            if rand_num >= 0 and rand_num <= 5:
                item_no = 1
            elif rand_num > 5 and rand_num <= 15:
                item_no = 2
            if item_no != 0:
                item = Item(item_no)
                Items.add(item)
                item.posx = self.pos.x
                item.posy = self.pos.y

    def render(self):
        displaysurface.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = scale_img(pygame.image.load("Enemy.png").convert_alpha())
        self.rect = self.image.get_rect()
        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.direction = random.randint(0, 1)
        # Increase speed for Hell Dungeon
        if handler.world == 3:
            self.vel.x = random.randint(5, 10) / 1.5
        else:
            self.vel.x = random.randint(2, 6) / 2
        self.mana = random.randint(1, 3)
        if self.direction == 0:
            self.pos.x = 0
        if self.direction == 1:
            self.pos.x = WIDTH - self.rect.width
        self.pos.y = HEIGHT - 100 - self.rect.height

    def move(self):
        if cursor.wait == 1:
            return
        if self.pos.x >= (WIDTH - 20):
            self.direction = 1
        elif self.pos.x <= 0:
            self.direction = 0
        if self.direction == 0:
            self.pos.x += self.vel.x
        if self.direction == 1:
            self.pos.x -= self.vel.x
        self.rect.topleft = self.pos

    def update(self):
        hits = pygame.sprite.spritecollide(self, Playergroup, False)
        f_hits = pygame.sprite.spritecollide(self, Fireballs, False)
        if hits and player.attacking == True or f_hits:
            self.kill()
            mmanager.playsound(hit, 0.05)
            handler.dead_enemy_count += 1
            if player.mana < 100:
                player.mana += self.mana
            player.experiance += 1
            rand_num = numpy.random.uniform(0, 100)
            item_no = 0
            if rand_num >= 0 and rand_num <= 5:
                item_no = 1
            elif rand_num > 5 and rand_num <= 15:
                item_no = 2
            if item_no != 0:
                item = Item(item_no)
                Items.add(item)
                item.posx = self.pos.x
                item.posy = self.pos.y
        elif hits and player.attacking == False:
            player.player_hit()

    def render(self):
        displaysurface.blit(self.image, self.rect)

class Castle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hide = False
        self.image = scale_img(pygame.image.load("castle.png").convert_alpha(), 2)

    def update(self):
        if self.hide == False:
            displaysurface.blit(self.image, (WIDTH // 2 - self.image.get_width() // 2, 80))

class EventHandler():
    def __init__(self):
        self.enemy_count = 0
        self.dead_enemy_count = 0
        self.battle = False
        self.enemy_generation = pygame.USEREVENT + 2
        self.enemy_generation2 = pygame.USEREVENT + 3
        self.stage = 1
        self.money = 0
        self.world = 0
        self.stage_enemies = []
        for x in range(1, 21):
            self.stage_enemies.append(int((x ** 2 / 2) + 1))
        self.stage_select_open = False
        self.next_world = None

    def stage_handler(self):
        try:
            root = Tk()
            root.geometry('200x170')
            root.title("Select Dungeon")

            def select_world(world_num):
                self.next_world = world_num
                self.stage_select_open = False
                root.destroy()

            button1 = Button(root, text="Skyward Dungeon", width=18, height=2, command=lambda: select_world(1))
            button2 = Button(root, text="Gerudo Dungeon", width=18, height=2, command=lambda: select_world(2))
            button3 = Button(root, text="Hell Dungeon", width=18, height=2, command=lambda: select_world(3))
            button1.place(x=40, y=15)
            button2.place(x=40, y=65)
            button3.place(x=40, y=115)

            def on_close():
                self.stage_select_open = False
                root.destroy()

            root.protocol("WM_DELETE_WINDOW", on_close)
            root.mainloop()
        except Exception as e:
            print("Stage selection error:", e)
            self.stage_select_open = False

    def world1(self):
        pygame.time.set_timer(self.enemy_generation, 2000)
        button.imgdisp = 1
        self.world = 1
        castle.hide = True
        self.battle = True
        mmanager.playsoundtrack(soundtrack[1], -1, 0.05)
        background.bgimage = pygame.image.load("Background.png").convert_alpha()
        background.bgimage = pygame.transform.smoothscale(background.bgimage, (WIDTH, HEIGHT))
        ground.image = pygame.image.load("Ground.png").convert_alpha()
        ground.image = pygame.transform.smoothscale(ground.image, (WIDTH, 100))
        self.stage_select_open = False

    def world2(self):
        background.bgimage = pygame.image.load("desert.jpg").convert_alpha()
        background.bgimage = pygame.transform.smoothscale(background.bgimage, (WIDTH, HEIGHT))
        ground.image = pygame.image.load("desert_ground.png").convert_alpha()
        ground.image = pygame.transform.smoothscale(ground.image, (WIDTH, 100))
        pygame.time.set_timer(self.enemy_generation2, 2000)
        self.world = 2
        button.imgdisp = 1
        castle.hide = True
        self.battle = True
        mmanager.playsoundtrack(soundtrack[1], -1, 0.05)
        self.stage_select_open = False

    def world3(self):
        try:
            background.bgimage = pygame.image.load("hell_bg.png").convert_alpha()
            background.bgimage = pygame.transform.smoothscale(background.bgimage, (WIDTH, HEIGHT))
            ground.image = pygame.image.load("hell_ground.png").convert_alpha()
            ground.image = pygame.transform.smoothscale(ground.image, (WIDTH, 100))
        except Exception as e:
            print("Hell Dungeon images not found, using default. Error:", e)
            background.bgimage = pygame.image.load("Background.png").convert_alpha()
            background.bgimage = pygame.transform.smoothscale(background.bgimage, (WIDTH, HEIGHT))
            ground.image = pygame.image.load("Ground.png").convert_alpha()
            ground.image = pygame.transform.smoothscale(ground.image, (WIDTH, 100))
        pygame.time.set_timer(self.enemy_generation2, 2000)
        self.world = 3
        button.imgdisp = 1
        castle.hide = True
        self.battle = True
        mmanager.playsoundtrack(soundtrack[1], -1, 0.05)
        self.stage_select_open = False

    def next_stage(self):
        self.stage += 1
        self.enemy_count = 0
        self.dead_enemy_count = 0
        if self.world == 1:
            pygame.time.set_timer(self.enemy_generation, max(500, 1500 - (50 * self.stage)))
        elif self.world == 2 or self.world == 3:
            pygame.time.set_timer(self.enemy_generation2, max(800, 2200 - (30 * self.stage)))

    def update(self):
        if self.dead_enemy_count == self.stage_enemies[self.stage - 1]:
            self.dead_enemy_count = 0
            stage_display.stage_clear()
            stage_display.clear = True

    def home(self):
        pygame.time.set_timer(self.enemy_generation, 0)
        pygame.time.set_timer(self.enemy_generation2, 0)
        self.battle = False
        self.enemy_count = 0
        self.dead_enemy_count = 0
        self.stage = 1
        self.world = 0
        for group in Enemies, Items:
            for entity in group:
                entity.kill()
        castle.hide = False
        background.bgimage = pygame.image.load("Background.png").convert_alpha()
        background.bgimage = pygame.transform.smoothscale(background.bgimage, (WIDTH, HEIGHT))
        ground.image = pygame.image.load("Ground.png").convert_alpha()
        ground.image = pygame.transform.smoothscale(ground.image, (WIDTH, 100))

class HealthBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("heart5.png").convert_alpha()

    def render(self):
        displaysurface.blit(self.image, (10, 10))

class StageDisplay(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.text = headingfont.render("STAGE: " + str(handler.stage), True, color_dark)
        self.rect = self.text.get_rect()
        self.posx = -100
        self.posy = 100
        self.display = False
        self.clear = False

    def move_display(self):
        self.text = headingfont.render("STAGE: " + str(handler.stage), True, color_dark)
        if self.posx < 720:
            self.posx += 6
            displaysurface.blit(self.text, (self.posx, self.posy))
        else:
            self.display = False
            self.posx = -100
            self.posy = 100

    def stage_clear(self):
        button.imgdisp = 0
        self.text = headingfont.render("STAGE CLEAR!", True, color_dark)
        if self.posx < 720:
            self.posx += 10
            displaysurface.blit(self.text, (self.posx, self.posy))
        else:
            self.clear = False
            self.posx = -100
            self.posy = 100

class StatusBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((90, 66))
        self.rect = self.surf.get_rect(topright=(WIDTH - 20, 10))
        self.exp = player.experiance

    def update_draw(self):
        text1 = smallerfont.render("STAGE: " + str(handler.stage), True, color_white)
        text2 = smallerfont.render("EXP: " + str(player.experiance), True, color_white)
        text3 = smallerfont.render("MANA: " + str(player.mana), True, color_white)
        fps = int(FPS_CLOCK.get_fps()) if FPS_CLOCK.get_fps() > 0 else FPS
        text4 = smallerfont.render("FPS: " + str(fps), True, color_white)
        self.exp = player.experiance
        displaysurface.blit(text1, (WIDTH - 105, 7))
        displaysurface.blit(text2, (WIDTH - 105, 22))
        displaysurface.blit(text3, (WIDTH - 105, 37))
        displaysurface.blit(text4, (WIDTH - 105, 52))

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = scale_img(pygame.image.load("cursor.png").convert_alpha())
        self.rect = self.image.get_rect()
        self.wait = 0

    def pause(self):
        if self.wait == 1:
            self.wait = 0
        else:
            self.wait = 1

    def hover(self, mouse):
        if 620 <= mouse[0] <= 660 and 300 <= mouse[1] <= 345:
            pygame.mouse.set_visible(False)
            self.rect.center = mouse
            displaysurface.blit(self.image, self.rect)
        else:
            pygame.mouse.set_visible(True)

class PButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.vec = vec(WIDTH - 110, 80)
        self.imgdisp = 0

    def render(self, num):
        if (num == 0):
            self.image = scale_img(pygame.image.load("home_small.png").convert_alpha())
        elif (num == 1):
            if cursor.wait == 0:
                self.image = scale_img(pygame.image.load("pause_small.png").convert_alpha())
            else:
                self.image = scale_img(pygame.image.load("play_small.png").convert_alpha())
        displaysurface.blit(self.image, self.vec)

Enemies = pygame.sprite.Group()
Items = pygame.sprite.Group()
Bolts = pygame.sprite.Group()
Fireballs = pygame.sprite.Group()
player = Player()
Playergroup = pygame.sprite.Group(player)
background = Background()
ground = Ground()
cursor = Cursor()
button = PButton()
ground_group = pygame.sprite.Group(ground)
castle = Castle()
handler = EventHandler()
health = HealthBar()
stage_display = StageDisplay()
status_bar = StatusBar()
hit_cooldown = pygame.USEREVENT + 1

KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_JUMP = pygame.K_UP
KEY_JUMP2 = pygame.K_SPACE
KEY_ATTACK = pygame.K_z
KEY_MAGIC = pygame.K_x
KEY_NEXT_STAGE = pygame.K_RETURN
KEY_STAGE_SELECT = pygame.K_TAB

while True:
    player.gravity_check()
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == hit_cooldown:
            player.cooldown = False
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == handler.enemy_generation:
            if handler.enemy_count < handler.stage_enemies[handler.stage - 1]:
                enemy = Enemy()
                Enemies.add(enemy)
                handler.enemy_count += 1
        elif event.type == handler.enemy_generation2:
            if handler.enemy_count < handler.stage_enemies[handler.stage - 1]:
                enemy = Enemy2() if handler.enemy_count % 2 else Enemy()
                Enemies.add(enemy)
                handler.enemy_count += 1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if WIDTH - 110 <= mouse[0] <= WIDTH - 70 and 80 <= mouse[1] <= 120:
                if button.imgdisp == 1:
                    cursor.pause()
                elif button.imgdisp == 0:
                    handler.home()
        elif event.type == pygame.KEYDOWN and cursor.wait == 0:
            if event.key == KEY_MAGIC and player.magic_cooldown == 1 and player.mana >= 6:
                player.mana -= 6
                player.attacking = True
                fireball = FireBall()
                Fireballs.add(fireball)
                mmanager.playsound(fsound, 0.3)
            elif event.key == KEY_NEXT_STAGE and handler.battle and len(Enemies) == 0:
                handler.next_stage()
                stage_display = StageDisplay()
                stage_display.display = True
            elif event.key == KEY_STAGE_SELECT and 450 < player.rect.x < 550:
                if not handler.stage_select_open:
                    handler.stage_select_open = True
                    threading.Thread(target=handler.stage_handler, daemon=True).start()
            elif event.key in (KEY_JUMP, KEY_JUMP2):
                player.jump()
            elif event.key == KEY_ATTACK and not player.attacking:
                player.attack()
                player.attacking = True

    # After event handling, before player.update()
    if handler.next_world:
        if handler.next_world == 1:
            handler.world1()
        elif handler.next_world == 2:
            handler.world2()
        elif handler.next_world == 3:
            handler.world3()
        handler.next_world = None

    player.update()
    if player.attacking:
        player.attack()
    player.move()

    background.render()
    ground.render()
    button.render(button.imgdisp)
    cursor.hover(mouse)

    if stage_display.display:
        stage_display.move_display()
    if stage_display.clear:
        stage_display.stage_clear()

    castle.update()
    if player.health > 0:
        displaysurface.blit(player.image, player.rect)
    health.render()

    displaysurface.blit(status_bar.surf, (WIDTH - 110, 5))
    status_bar.update_draw()
    handler.update()

    for i in Items.sprites():
        i.render()
        i.update()
    for ball in Fireballs.sprites():
        ball.fire()
    for bolt in Bolts.sprites():
        bolt.fire()
    for entity in Enemies.sprites():
        entity.update()
        entity.move()
        entity.render()

    # --- GAME OVER SCREEN AND RESTART ---
    if game_over:
        displaysurface.fill((0, 0, 0))
        over_text = headingfont.render("GAME OVER", True, (255, 0, 0))
        restart_text = regularfont.render("Press R to Restart", True, (255, 255, 255))
        displaysurface.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))
        displaysurface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    handler.home()
                    player.__init__()
                    Playergroup.empty()
                    Playergroup.add(player)
                    health.image = health_ani[player.health]
                    stage_display.__init__()
                    status_bar.__init__()
                    waiting = False
                    game_over = False
            FPS_CLOCK.tick(15)

    pygame.display.update()
    FPS_CLOCK.tick(FPS)
