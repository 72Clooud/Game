import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Game')

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

SHOOT_SOUND_EFFECT = pygame.mixer.Sound(os.path.join("assets", "shoot.wav"))
SHOOT_SOUND_EFFECT.set_volume(0.2)

DESTROY_SOUND_EFFECT = pygame.mixer.Sound(os.path.join('assets', 'invaderkilled.wav'))
DESTROY_SOUND_EFFECT.set_volume(0.15)

HEAL_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'heal.png')), (50, 50))
HEAL_SOUND_EFFECT = pygame.mixer.Sound(os.path.join('assets', 'heal_sound.mp3'))

UPGRADE_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'upgrade.png')), (50, 50))
UPGRADE_SOUND_EFFECT = pygame.mixer.Sound(os.path.join('assets', 'upgrade_sound.mp3'))


pygame.mixer.music.load(os.path.join('assets', 'music.mp3'))
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(loops=-1, fade_ms=2000)



class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        
    def move(self, vel):
        self.y += vel
        
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


class Ship:
    COOLDOWN = 30
    
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
            
    def move_lasers(self, vel, obj):
        self.cooldown(0)
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
            
                    
    def cooldown(self, upgrade_cooldown_level):
        if self.cool_down_counter >= self.COOLDOWN - upgrade_cooldown_level:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
            
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            SHOOT_SOUND_EFFECT.play()
            
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
                
class Player(Ship):
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        
    def move_lasers(self, vel, objs, upgrade_level):
        self.cooldown(upgrade_level)
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        DESTROY_SOUND_EFFECT.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
                        

class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
    }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            
class Heal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heal_img = HEAL_IMAGE
        self.mask = pygame.mask.from_surface(self.heal_img)
        
    def draw(self, window):
        window.blit(self.heal_img, (self.x, self.y))
        
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)
    
    def get_width(self):
        return self.heal_img.get_width()
    
    def get_height(self):
        return self.heal_img.get_height()
        
class Upgrade(Heal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.upgrade_img = UPGRADE_IMAGE
        self.mask = pygame.mask.from_surface(self.upgrade_img)
        
    def draw(self, window):
        window.blit(self.upgrade_img, (self.x, self.y))
        
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)
    
    def get_width(self):
        return self.upgrade_img.get_width()
    
    def get_height(self):
        return self.upgrade_img.get_height()
        
        
        
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x 
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('Courier New', 30)
    lost_font = pygame.font.SysFont('Courier New', 40)
    
    enemies = []
    wave_len = 5
    enemy_vel = 1
    
    heals = []
    heal_vel = 1
    heal_rate_spawn = 2000
    
    upgrades = []
    upgrades_vel = 1
    upgrade_vel = 0
    upgrade_cooldown_value = 0
    
    player_vel = 5 
    laser_vel = 5
    
    player = Player(300, 650, (255, 255, 0))
        
    clock = pygame.time.Clock() 
    
    lost = False
    lost_count = 0
    
    
    def redraw_window():
        WIN.blit(BACKGROUND, (0, 0))
        
        lives_label = main_font.render(f'Lives: {lives}', 1, (255, 255, 255))
        level_label = main_font.render(f'Level: {level}', 1, (255, 255, 255))
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
        
        for enemy in enemies:
            enemy.draw(WIN)
            
        for heal in heals:
            heal.draw(WIN)
        
        for upgrade in upgrades:
            upgrade.draw(WIN)
        
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render('You Lost!!!', 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    
    while run:
        clock.tick(FPS)
        redraw_window()
        
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if (len(enemies) == 0) and (level >= 1):
            upgrade = Upgrade(random.randrange(50, WIDTH - 100), 0)
            upgrades.append(upgrade)
        
        if len(enemies) == 0:
            level += 1
            wave_len += 5
            for i in range(wave_len):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)
                
        if random.randrange(0, heal_rate_spawn) == 1:
            heal = Heal(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
            heals.append(heal)
            
            
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < HEIGHT:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 10 < HEIGHT:
            player.y += player_vel
      
        if keys[pygame.K_SPACE]:
            player.shoot() 
            
      
      
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        for heal in heals[:]: 
            heal.move(heal_vel)
            if collide(heal, player):
                player.health += 20
                HEAL_SOUND_EFFECT.play()
                heals.remove(heal)  
            if player.health > player.max_health:  
                player.health = player.max_health
            elif heal.y + heal.get_height() > HEIGHT:
                heals.remove(heal)
        
        for upgrade in upgrades[:]: 
            upgrade.move(upgrades_vel)
            if collide(upgrade, player):
                upgrade_vel += 1
                upgrade_cooldown_value += 2
                UPGRADE_SOUND_EFFECT.play()
                upgrades.remove(upgrade)  
            elif upgrade.y + upgrade.get_height() > HEIGHT:
                upgrades.remove(upgrade)
            
        player.move_lasers(-laser_vel - upgrade_vel, enemies, upgrade_level=upgrade_cooldown_value)
        
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
        
        
main_menu()