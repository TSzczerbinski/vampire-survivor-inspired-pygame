import sys
import pygame
import os
import random
import weapons
import enemies

pygame.init()

SCREENSIZE = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(SCREENSIZE)

YELLOW = pygame.color.THECOLORS['yellow']
RED = pygame.color.THECOLORS['red']

clock = pygame.time.Clock()
missile_timer_start = pygame.time.get_ticks()
fireball_timer_start = pygame.time.get_ticks()
orbit_timer_start = pygame.time.get_ticks()

path = os.path.join(os.getcwd(), 'images')
file_names = sorted(os.listdir(path))
BACKGROUND = pygame.image.load(os.path.join(path, 'background.png')).convert()
for name in file_names:
    if "enemy" in name:
        file_names.remove(name)
file_names.remove('background.png')
PLAYER = []
for name in file_names:
    if "player" in name:
        PLAYER.append(pygame.image.load(os.path.join(path, name)))
IMAGES = {}
for name in file_names:
    image_name = name[:-4].upper()
    IMAGES[image_name] = pygame.image.load(os.path.join(path, name)).convert_alpha(BACKGROUND)
path_music = os.path.join(os.getcwd(), 'sound')
hit = pygame.mixer.Sound(os.path.join(path_music, "sound_effect.wav"))


class Gameplay:
    def __init__(self):
        self.set_of_enemies = pygame.sprite.Group()
        self.set_of_weapons = pygame.sprite.Group()
        self.text_lvl = Text(player.level, YELLOW, WIDTH - 100, 50, font_size=76)
        self.text_hp = Text(player.hp, YELLOW, 120, 50, font_size=76)
        self.score = 0

    def _add_enemy(self):
        if player.level <= 2:
            enemy_image = random.choice(enemies.Goblin.images)
            enemy = enemies.Goblin(enemy_image, player)
        else:
            enemy_image = random.choice(enemies.Dragon.images)
            enemy = enemies.Dragon(enemy_image, player)
        edge = random.randint(0, 3)
        match edge:
            case 0:
                enemy.rect.x = 0
                enemy.rect.y = random.randint(0, HEIGHT - enemy.rect.height)
            case 1:
                enemy.rect.x = WIDTH
                enemy.rect.y = random.randint(0, HEIGHT - enemy.rect.height)
            case 2:
                enemy.rect.x = random.randint(0, WIDTH - enemy.rect.height)
                enemy.rect.y = 0
            case 3:
                enemy.rect.x = random.randint(0, WIDTH - enemy.rect.height)
                enemy.rect.y = WIDTH
        self.set_of_enemies.add(enemy)

    def level_up(self):
        player.level_up()
        if hasattr(self, "aura") and self.aura.alive():
            self.aura.level = player.weapons["Aura"]
            self.aura.update_stats()
        level_screen(player)

    def update(self):
        if not hasattr(self, "aura") or not self.aura.alive():
            self.aura = weapons.Aura(IMAGES["AURA"], player, player.weapons["Aura"])
            self.set_of_weapons.add(self.aura)
        player.shoot()

        self.set_of_weapons.update()
        self.set_of_enemies.update()
        if player.level <= 5:
            if random.randint(1, 25) == 1:
                self._add_enemy()
        else:
            if random.randint(1, 10) == 1:
                self._add_enemy()
                self._add_enemy()

        if pygame.sprite.groupcollide(self.set_of_enemies, self.set_of_weapons, False, False):
            pygame.mixer.Sound.play(hit)
            collided = pygame.sprite.groupcollide(self.set_of_weapons, self.set_of_enemies, False, False)
            weapon = list(collided)[0]
            enemy = collided.get(weapon)[0]
            enemy.hp -= weapon.damage
            if enemy.hp <= 0:
                enemy.kill()
                if isinstance(enemy, enemies.Goblin):
                    player.exp += 1
                    self.score += 1
                elif isinstance(enemy, enemies.Dragon):
                    player.exp += 2
                    self.score += 2
            if isinstance(weapon, weapons.Missile):
                weapon.kill()
        if pygame.sprite.spritecollide(player, self.set_of_enemies, True):
            player.hp -= 1
        if player.exp >= player.exp_to_level:
            self.level_up()

        self.text_lvl = Text("lvl: " + str(player.level), YELLOW, WIDTH - 100, 50, font_size=76)
        self.text_hp = Text("hp: " + str(player.hp) + "/10", YELLOW, 120, 50, font_size=76)

    def draw(self, surface):
        self.set_of_weapons.draw(surface)
        self.set_of_enemies.draw(surface)
        self.text_lvl.draw(surface)
        self.text_hp.draw(surface)


class Text:
    def __init__(self, text, text_color, px, py, font_type=None, font_size=74):
        self.text = str(text)
        font = pygame.font.SysFont(font_type, font_size)
        self.image = font.render(self.text, True, text_color)
        self.rect = self.image.get_rect()
        self.rect.center = px, py

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Button(pygame.sprite.Sprite):
    def __init__(self, text, position, offset_x, offset_y):
        super().__init__()
        self.text = Text(text, YELLOW, position[0], position[1], font_size=70)
        self.rect = (self.text.rect.x + offset_x, self.text.rect.y + offset_y)
        self.position_x = position[0]
        self.position_y = position[1]
        self.Rect = pygame.Rect(self.position_x, self.position_y, 400, 100)

    def draw(self, surface):
        image = pygame.draw.rect(screen, (0, 0, 255), self.Rect)
        surface.blit(self.text.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, px, py, hp=10, exp_to_level=10):
        super().__init__()
        self.images = PLAYER
        self.walk_count = 0
        self.image = self.images[self.walk_count//12]
        self.rect = self.image.get_rect()
        self.rect.center = px, py
        self.movement_speed = 5
        self.exp = 0
        self.level = 0
        self.game = None
        self.weapons = {"Missile": 1, "Fireball": 1, "Aura": 1, "Orbit": 1}
        self.hp = hp
        self.exp_to_level = exp_to_level

    def _handle_events(self, keys_pressed):
        if keys_pressed[pygame.K_a]:
            self.rect.move_ip([-self.movement_speed, 0])
            self.walk_count += 1
        if keys_pressed[pygame.K_d]:
            self.rect.move_ip([self.movement_speed, 0])
            self.walk_count += 1
        if keys_pressed[pygame.K_w]:
            self.rect.move_ip([0, -self.movement_speed])
            self.walk_count += 1
        if keys_pressed[pygame.K_s]:
            self.rect.move_ip([0, self.movement_speed])
            self.walk_count += 1

    def shoot(self):
        if len(level.set_of_enemies) > 0:
            distance_min = pygame.math.Vector2(level.set_of_enemies.sprites()[0].rect.x - self.rect.x, level.set_of_enemies.sprites()[0].rect.y - self.rect.y).length()
            index = 0
            index_min = 0
            for enemy in level.set_of_enemies:
                distance = pygame.math.Vector2(enemy.rect.x - self.rect.x, enemy.rect.y - self.rect.y).length()
                if distance < distance_min:
                    distance_min = distance
                    index_min = index
                index += 1
            vect = pygame.math.Vector2(level.set_of_enemies.sprites()[index_min].rect.x - self.rect.x, level.set_of_enemies.sprites()[index_min].rect.y - self.rect.y)
            if vect.length() > 0:
                missile_timer_now = pygame.time.get_ticks()
                global missile_timer_start
                if missile_timer_now - missile_timer_start > 850 - self.weapons["Missile"] * 100:
                    missile_timer_start = missile_timer_now
                    missile = weapons.Missile(IMAGES["MISSILE"], self.rect.centerx, self.rect.centery, vect, self.weapons["Missile"])
                    self.game.set_of_weapons.add(missile)
                fireball_timer_now = pygame.time.get_ticks()
                global fireball_timer_start
                if fireball_timer_now - fireball_timer_start > 1100 - self.weapons["Fireball"] * 100:
                    fireball_timer_start = fireball_timer_now
                    fireball = weapons.Fireball(IMAGES["FIREBALL"], self.rect.centerx, self.rect.centery, vect, self.weapons["Fireball"])
                    self.game.set_of_weapons.add(fireball)
                orbit_timer_now = pygame.time.get_ticks()
                global orbit_timer_start
                if orbit_timer_now - orbit_timer_start > 2500 - self.weapons["Orbit"] * 100:
                    orbit_timer_start = orbit_timer_now
                    orbit = weapons.Orbit(IMAGES["ORBIT"], self, self.weapons["Orbit"])
                    self.game.set_of_weapons.add(orbit)

    def update(self, keys_pressed):
        self._handle_events(keys_pressed)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

        if self.walk_count >= 96:
            self.walk_count = 0
        self.image = self.images[self.walk_count//12]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def level_up(self):
        self.exp -= self.exp_to_level
        self.level += 1
        self.exp_to_level *= 1.2


def menu():
    menu_open = True
    while menu_open:
        screen.blit(IMAGES["MENU"], (0, 0))
        title = Text("TITLE", RED, 625, 150, font_size=300)
        title.draw(screen)
        exit = Button("EXIT", (440, 500), 200, 50)
        exit.draw(screen)
        start = Button("START", (440, 300), 200, 50)
        start.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            mouse = pygame.mouse.get_pos()
            if pygame.Rect.collidepoint(start.Rect, mouse):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu_open = False
                    break
            if pygame.Rect.collidepoint(exit.Rect, mouse):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()
        clock.tick(60)


def death_screen(time):
    screen_open = True
    while screen_open:
        screen.blit(IMAGES["MENU"], (0, 0))
        score = level.score * time/1000
        score = int(score)
        text = Text("SCORE: " + str(score), RED, WIDTH//2, HEIGHT//2, font_size=100)
        text.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()
        clock.tick(60)


def level_screen(player):
    screen_open = True
    r1, r2, r3 = random.sample(list(player.weapons.keys()), k=3)
    while screen_open:
        level.draw(screen)
        player.draw(screen)
        text = Text("CHOOSE SKILL TO LEVEL UP:", RED, 650, 75, font_size=100)
        text.draw(screen)
        choice_1 = Button(r1, (440, 150), 200, 50)
        choice_1.draw(screen)
        choice_2 = Button(r2, (440, 350), 200, 50)
        choice_2.draw(screen)
        choice_3 = Button(r3, (440, 550), 200, 50)
        choice_3.draw(screen)

        for event in pygame.event.get():
            mouse = pygame.mouse.get_pos()
            if pygame.Rect.collidepoint(choice_1.Rect, mouse):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.weapons[r1] += 1
                    screen_open = False
            if pygame.Rect.collidepoint(choice_2.Rect, mouse):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.weapons[r2] += 1
                    screen_open = False
            if pygame.Rect.collidepoint(choice_3.Rect, mouse):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.weapons[r3] += 1
                    screen_open = False
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)


player = Player(WIDTH // 2, HEIGHT // 2)
level = Gameplay()
player.game = level
window_open = True
pygame.mixer.music.load(os.path.join(path_music, "music.wav"))
pygame.mixer.music.play(-1)
menu()
timer_start = pygame.time.get_ticks()
while window_open:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            window_open = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                window_open = False

    if player.hp <= 0:
        timer_end = pygame.time.get_ticks()
        time = timer_end - timer_start
        death_screen(time)

    keys_pressed = pygame.key.get_pressed()

    screen.blit(BACKGROUND, (0, 0))

    level.update()
    player.update(keys_pressed)

    level.draw(screen)
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
