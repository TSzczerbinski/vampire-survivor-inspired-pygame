import random
import pygame


class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, px, py, vector, level, speed, damage):
        super().__init__()
        self.level = level
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = [px, py]
        self.speed = speed + speed * self.level/5
        vector.normalize()
        vector.scale_to_length(self.speed)
        self.vector = vector
        self.damage = damage + damage * self.level/5


class Missile(Projectile):
    def __init__(self, image, px, py, vector, level, speed=15, damage=100, ):
        super().__init__(image, px, py, vector, level, speed, damage)

    def update(self):
        self.rect.move_ip(self.vector)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Fireball(Projectile):
    def __init__(self, image, px, py, vector, level, speed=5, damage=10):
        super().__init__(image, px, py, vector, level, speed, damage)

    def update(self):
        self.rect.move_ip(self.vector)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Aura(pygame.sprite.Sprite):
    def __init__(self, image, player, level, damage=10, aoe=64):
        super().__init__()
        self.player = player
        self.image_base = image
        self.level = level
        self.base_aoe = aoe
        self.base_damage = damage
        self.update_stats()

    def update_stats(self):
        self.aoe = self.base_aoe + self.base_aoe * self.level / 5
        self.damage = self.base_damage + self.base_damage * self.level / 5
        self.image = pygame.transform.scale(self.image_base, (int(self.aoe), int(self.aoe)))
        self.rect = self.image.get_rect(center=self.player.rect.center)

    def update(self):
        self.rect.center = self.player.rect.center

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Orbit(pygame.sprite.Sprite):
    def __init__(self, image, player, level, radius=100, speed=2, duration=5000, damage=10):
        super().__init__()
        self.player = player
        self.level = level
        self.image = image
        self.radius = radius
        self.speed = speed + speed * self.level/5
        self.rect = self.image.get_rect()
        position = self.player.rect.center
        self.position = pygame.math.Vector2(position)
        self.offset = pygame.math.Vector2(self.radius, 0)
        self.angle = random.randint(0, 360)
        self.duration = duration + duration * self.level/5
        self.time_start = pygame.time.get_ticks()
        self.damage = damage + damage * self.level/5

    def update(self):
        timer = pygame.time.get_ticks()
        if timer - self.time_start > self.duration:
            self.kill()
        self.position = pygame.math.Vector2(self.player.rect.center)
        self.angle -= self.speed
        self.rect.center = self.position + self.offset.rotate(self.angle)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
