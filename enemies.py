import pygame
import os

path = os.path.join(os.getcwd(), 'images')
file_names = sorted(os.listdir(path))
for name in file_names:
    if "enemy" not in name:
        file_names.remove(name)
IMAGES = {}
for name in file_names:
    image_name = name[:-4].upper()
    IMAGES[image_name] = pygame.image.load(os.path.join(path, name))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, player, speed, hp):
        super().__init__()
        self.player = player
        self.image = image
        self.rect = self.image.get_rect()
        self.speed = speed
        self.hp = hp


class Goblin(Enemy):
    images = [IMAGES[name] for name in IMAGES if "GOBLIN" in name]

    def __init__(self, image, player, speed=5, hp=100):
        super().__init__(image, player, speed, hp)

    def update(self):
        vect = pygame.math.Vector2(self.player.rect.x - self.rect.x, self.player.rect.y - self.rect.y)
        if vect.length() > 0:
            vect.normalize()
            vect.scale_to_length(self.speed)
        self.rect.move_ip(vect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Dragon(Enemy):
    images = [IMAGES[name] for name in IMAGES if "DRAGON" in name]

    def __init__(self, image, player, speed=6, hp=150):
        super().__init__(image, player, speed, hp)

    def update(self):
        vect = pygame.math.Vector2(self.player.rect.x - self.rect.x, self.player.rect.y - self.rect.y)
        if vect.length() > 0:
            vect.normalize()
            vect.scale_to_length(self.speed)
        self.rect.move_ip(vect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

