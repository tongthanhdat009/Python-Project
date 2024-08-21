import math
import os
import random
import sys
import time
import pygame

from script.entities import Boss, PhysicsEntity, Player, Enemy, Spec_Enemy
from script.spark import Spark
from script.utils import load_image, load_images, animation
from script.tilemap import Tilemap
from script.spaceships import spaceships
from script.particles import particle
from script.button import Button

class Test:
    def __init__(self):
        #khởi tạo cửa sỏ   
        pygame.init()
        pygame.display.set_caption("Test") # đổi tiêu đề cửa sổ
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240),pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320,240))
        self.main_menu = pygame.Surface((320,240))
        
        self.clock = pygame.time.Clock()

        self.movement = [False, False, False, False]

        # tải ảnh và hoạt ảnh
        self.assets = {
            'decor': load_images('tiles//decor'),
            'grass': load_images('tiles//grass'),
            'large_decor': load_images('tiles//large_decor'),
            'stone': load_images('tiles//stone'),
            'industry1': load_images('tiles//industry//industry_plat_1'),
            'industry2': load_images('tiles//industry//industry_plat_2'),
            'industry3': load_images('tiles//industry//industry_plat_3'),
            'industry4': load_images('tiles//industry//industry_plat_4'),
            'industry5': load_images('tiles//industry//industry_plat_5'),
            'industry6': load_images('tiles//industry//industry_plat_6'),
            'industry7': load_images('tiles//industry//industry_plat_7'),
            'industry8': load_images('tiles//industry//industry_plat_8'),
            'power_station1':load_images('tiles//power_station//pw_plat_1'),
            'power_station2':load_images('tiles//power_station//pw_plat_2'),
            'power_station3':load_images('tiles//power_station//pw_plat_3'),
            'power_station4':load_images('tiles//power_station//pw_plat_4'),
            'power_station5':load_images('tiles//power_station//pw_plat_5'),
            'background': load_image('background.png'),
            'spaceships': load_images('spaceships'),

            'player': load_image('entities//player.png'),
            'player//idle': animation(load_images('entities//player//idle'), img_dur=6),
            'player//run': animation(load_images('entities//player//run'), img_dur=7),
            'player//jump': animation(load_images('entities//player//jump')),
            'player//hurt': animation(load_images('entities//player//hurt'),img_dur=10),
            'player//double_jump': animation(load_images('entities//player//double_jump'),img_dur=4),
            'player//wall_slide': animation(load_images('entities//player//wall_slide')),
            'particle//leaf': animation(load_images('particles//leaf'), img_dur= 20, loop= False),
            'particle//particle': animation(load_images('particles//particle'), img_dur= 2, loop= False),
            'enemy//idle': animation(load_images('entities//enemy//idle'), img_dur= 6),
            'enemy//run': animation(load_images('entities//enemy//run'), img_dur= 7),
            'spec_enemy//idle': animation(load_images('entities//spec_enemy//idle'), img_dur= 6),
            'spec_enemy//run': animation(load_images('entities//spec_enemy//run'), img_dur= 7),
            'boss//idle': animation(load_images('entities//boss//idle'), img_dur= 6),
            'boss//run': animation(load_images('entities//boss//run'), img_dur= 7),

            'gun':load_image('gun.png'),
            'projectile':load_image('projectile.png'),
            'skill': load_image('skill.png'),
            'menu':load_image('menu//bg_menu.jpg'),

            'menu//EXIT_1': load_image('menu//EXIT_1.png'),
            'menu//EXIT_2': load_image('menu//EXIT_2.png'),
            'menu//START_1': load_image('menu//START_1.png'),
            'menu//START_2': load_image('menu//START_2.png'),
            'menu//TITLE_1': load_image('menu//TITLE.png'),
        }
        
        #âm thanh game
        self.sfx = {
            'jump': pygame.mixer.Sound('data//sfx//jump.wav'),
            'dash': pygame.mixer.Sound('data//sfx//dash.wav'),
            'hit': pygame.mixer.Sound('data//sfx//hit.wav'),
            'shoot': pygame.mixer.Sound('data//sfx//shoot.wav'),
            'ambience': pygame.mixer.Sound('data//sfx//ambience.wav'),
            'landing': pygame.mixer.Sound('data//sfx//landing.mp3'),
            'domain': pygame.mixer.Sound('data//sfx//domain.mp3'),
            'ouch': pygame.mixer.Sound('data//sfx//ouch.mp3'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.5)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.5)
        self.sfx['landing'].set_volume(0.4)
        self.sfx['domain'].set_volume(0.8)
        self.sfx['ouch'].set_volume(0.5)

        # khởi tạo đối tượng:
        #mây
        self.spaceships = spaceships(self.assets['spaceships'], count=8)

        # người chơi
        self.player = Player(self, (50, 50), (8, 15))

        # vật thể trong map
        self.tilemap = Tilemap(self, tile_size=16)
        self.scroll = [0, 0]

        self.particles = []

        #danh sách chứa đạn địch
        self.projectiles = []

        #danh sách chứa chiêu người chơi cần được xử lý:
        self.skills = []

        self.sparks = [] # hiệu ứng tia lửa

        self.level = 0 #biến lưu màn chơi

        self.load_level(0)

        self.dead = 0 #kiểm tra người chơi đã chết chưa

        self.screenshake = 0 #rung cam

        self.transition = -50

        # hiển số địch còn lại
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.font = pygame.font.Font('data//font//CyberpunkCraftpixPixel.otf', 32)
        
        #đếm số npc còn lại
        self.enemies_count = self.font.render(": "+str(len(self.enemies)), True, self.green)
        self.enemies_countRect = self.enemies_count.get_rect()
        self.enemies_countRect = (640//2,480//2)
        self.enemy_img = pygame.transform.scale(load_image('entities//enemy//idle//0.png'),(35,35))

        # hiển thị máu người chơi
        self.health_player_count = self.font.render(": "+str(self.player.health), True, self.green)
        self.health_player_countRect = self.enemies_count.get_rect()
        self.health_player_countRect = (640//2,480//2)
        self.player_img = pygame.transform.scale(load_image('entities//player//idle//0.png'),(35,35))

        #hiển thị hồi chiêu người chơi
        self.skill_img = pygame.transform.scale(load_image('skill.png'),(25,25))
        self.skill_img_cd = pygame.transform.scale(load_image('skill_cd.png'),(25,25))

        #hiển thị thông báo hết game:
        self.endGameText = self.font.render("Done!", True, self.green)

    def load_level(self,map_id):
        self.tilemap.load('data//maps//' + str(map_id) +'.json')

        self.projectiles = []
        self.skills = []

        # tạo hoạt ảnh lá rơi
        self.leaf_spawners = []
        self.tilemap.extract([('large_decor', 2)], keep=True)
        
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13)) # 4 4 rơi từ trái trên xuống dưới trái phải
        
        self.enemies = []
        self.spec_enemies = []
        self.bosses = []
        for spawner in self.tilemap.extract([('spawners',0),('spawners',1),('spawners',2),('spawners',3)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.health = 150
            elif spawner['variant'] == 1:
                self.enemies.append(Enemy(self,spawner['pos'],(8,15)))
            elif spawner['variant'] == 2:
                self.spec_enemies.append(Spec_Enemy(self,spawner['pos'],(8,15)))
            elif spawner['variant'] == 3:
                self.bosses.append(Boss(self,spawner['pos'],(8,15)))

    def endGame(self):
        enemy_remaining = len(self.bosses + self.spec_enemies + self.enemies)
        if self.level == (len(os.listdir('data//maps'))-1) and enemy_remaining == 0:
            print("hello")
            self.screen.fill('black')
            self.screen.blit(self.endGameText, (70,250))
  
    def run(self):
        run = True
        
        pygame.mixer.music.load('data//music.mp3')
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

        # self.sfx['ambience'].play(-1)

        while run:

            self.display.fill((0,0,0,0))
            self.display_2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake -1) #rung cam

            if not len(self.enemies)  and not len(self.spec_enemies) and not len(self.bosses):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data//maps')) - 1)
                    self.load_level(self.level)
                    self.transition = -50  # Reset transition after loading the new level

            if self.transition < 0:
                self.transition += 1

            if self.dead == 1:
                self.projectiles.clear()
                self.skills.clear()
                self.load_level(self.level)
                self.dead = 0
                self.player.health = 150 #hồi lại đầy máu


            # di chuyển cam
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # tạo lá
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            # tải vật thể trong map
            self.tilemap.render(self.display, offset=render_scroll)

            # cập nhật mây mỗi khi chuyển qua 1 khung hìnhdddd
            self.spaceships.update()
            self.spaceships.render(self.display_2, offset=render_scroll)

            # cập nhật và hiển thị npc
            for spec_enemy in self.spec_enemies.copy():
                kill = spec_enemy.update(self.tilemap,(0,0))
                spec_enemy.render(self.display, offset = render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap,(0,0))
                enemy.render(self.display, offset = render_scroll)

            for enemy in self.bosses.copy():
                kill = enemy.update(self.tilemap,(0,0))
                enemy.render(self.display, offset = render_scroll)

            # cập nhật và hiển thị nhân vật
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # tạo đạn từ địch
            for projectile in self.projectiles.copy():
                projectile.x_update()
                projectile.time_checker()
                img = self.assets['projectile']
                projectile.render(img, render_scroll)
                if projectile.bullet_solid_check():
                    self.projectiles.remove(projectile)
                elif projectile.time_checker():
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing)<50 and self.dead == 0:
                    if projectile.player_checker():
                        self.player.hit(projectile.damage)
                        # print(self.player.health)
                        self.projectiles.remove(projectile)
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            #hiệu ứng nổ khi trúng đạn
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random(),(240, 72, 50)))
                            self.particles.append(particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
            
            # kĩ năng từ người chơi
            for skill in self.skills.copy():
                skill.x_update()
                skill.time_checker()
                img = self.assets['skill']
                skill.render(img, render_scroll)
                if skill.bullet_solid_check():
                    self.skills.remove(skill)
                elif skill.time_checker():
                    self.skills.remove(skill)
                elif skill.enemy_class_checker(skill, self.enemies, self.spec_enemies, self.bosses, self.player.skill_dmg):
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        #hiệu ứng nổ khi trúng đạn
                        self.sparks.append(Spark(skill.rect().center, angle, 2 + random.random(), (187, 255, 0)))
                        self.particles.append(particle(self, 'particle', skill.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    self.skills.remove(skill)

            #hiển thị tia lửa khi trúng đạn
            for spk in self.sparks.copy():
                kill = spk.update() 
                spk.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spk)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0,0,0,100), unsetcolor=(0,0,0,0))
            self.display_2.blit(display_sillhouette,(0,0))

            
            # cập nhật và hiển thị vật thể
            for part in self.particles.copy():
                kill = part.update()
                part.render(self.display, offset=render_scroll)
                if part.type == 'leaf':
                    part.pos[0] += math.sin(part.animation.frame * 0.035) * 0.3 #giảm tốc độ hết 1 vòng lặp
                if kill:
                    self.particles.remove(part)

            # xử lý sự kiện nút
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.jump_perform()
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_SPACE: 
                        self.player.skill()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.KEYUP:
                    # if event.key == pygame.K_UP or event.key == pygame.K_w:
                    #     self.movement[2] = False
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            #hiệu ứng chuyển màn
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            for offset in [(-1,0), (1,0), (0,-1), (0,1)]:
                self.display_2.blit(self.display,offset)

            #hiệu ứng rung màn hình
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,random.random() * self.screenshake - self.screenshake / 2 )
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            
            #hiển thị số mục tiêu còn lại
            self.enemies_count = self.font.render(": "+str(len(self.enemies + self.spec_enemies + self.bosses)), True, self.green)
            self.screen.blit(self.enemy_img,(515,20))
            self.screen.blit(self.enemies_count,(555,20))
            
            #hiển thị máu người chơi
            self.health_player_count = self.font.render(": "+str(self.player.health)+"/150", True, self.green)
            self.screen.blit(self.player_img,(0,20))
            self.screen.blit(self.health_player_count,(50,20))

            #hiển thị hồi chiêu người chơi
            if(self.player.cooldown_skill > 0):
                self.screen.blit(self.skill_img_cd,(5,70))
            else:
                self.screen.blit(self.skill_img,(5,70))

            #hiển thị level hiện tại:
            self.level_count = self.font.render("level: "+str(self.level),True,self.green)
            self.screen.blit(self.level_count,(30,450))

            pygame.display.update()
            self.clock.tick(60)

    def menu(self):
        start_img = self.assets['menu//START_1']
        start_button = Button(100,200,start_img, 0.9)
        while True:
            self.screen.fill((202,228,241))
            if start_button.draw(self.screen):
                self.run()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            # self.screen.blit(pygame.transform.scale(self.main_menu, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
            
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def draw(self, screen):
        action = False
        #lấy vị trí trỏ chuột
        pos = pygame.mouse.get_pos()

        #kiểm tra chuột có trong vùng của nút không:
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                print("con chuot")
                self.clicked = True
                action = True
            if pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
                self.clicked = False

        #vẽ nút lên menu
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action
    
# Run the game
if __name__ == "__main__":
    Test().menu()
