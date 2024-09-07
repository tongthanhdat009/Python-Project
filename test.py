import json
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
        
        #tạo cửa sổ không viền
        self.screen = pygame.display.set_mode((640, 480), pygame.NOFRAME)
        
        #cho trỏ chuột trong cửa sổ
        pygame.event.set_grab(True)

        self.display = pygame.Surface((320, 240),pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320,240))
        
        self.user_path = 'data//user.json'

        self.clock = pygame.time.Clock()

        self.movement = [False, False, False, False]

        # tải ảnh và hoạt ảnh
        self.assets = {
            'decor': load_images('tiles//decor'),
            'grass': load_images('tiles//grass'),
            'large_decor': load_images(r'tiles/large_decor'),
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

            'menu//pause//EXIT_1': load_image('menu//pause//EXIT_1.png'),
            'menu//pause//EXIT_2': load_image('menu//pause//EXIT_2.png'),
            'menu//pause//RESUME_1': load_image('menu//pause//RESUME_1.png'),
            'menu//pause//RESUME_2': load_image('menu//pause//RESUME_2.png'),
            'menu//pause//MENU_1': load_image('menu//pause//MENU_1.png'),
            'menu//pause//MENU_2': load_image('menu//pause//MENU_2.png'),

            'menu//main//EXIT_1': load_image('menu//main//EXIT_1.png'),
            'menu//main//EXIT_2': load_image('menu//main//EXIT_2.png'),
            'menu//main//START_1': load_image('menu//main//START_1.png'),
            'menu//main//START_2': load_image('menu//main//START_2.png'),
            'menu//main//TITLE_1': load_image('menu//main//TITLE_1.png'),
            'menu//main//TITLE_2': load_image('menu//main//TITLE_2.png'),
            'menu//main//TITLE_3': load_image('menu//main//TITLE_3.png'),
            'menu//main//TUTORIAL_1': load_image('menu//main//TUTORIAL_1.png'),
            'menu//main//TUTORIAL_2': load_image('menu//main//TUTORIAL_2.png'),
            'menu//main//CONTINUE_1': load_image('menu//main//CONTINUE_1.png'),
            'menu//main//CONTINUE_2': load_image('menu//main//CONTINUE_2.png'),
            'menu//main//background': load_images('menu//background'),
            'menu//main//TUTOR_TITLE': load_image('menu//main//TUTOR_TITLE.png'),
            'menu//main//TUTOR': load_image('menu//main//TUTOR.png'),

            'menu//end//RESTART_1': load_image('menu//end/RESTART_1.png'),
            'menu//end//RESTART_2': load_image('menu//end/RESTART_2.png'),
            'menu//end//EXIT_1': load_image('menu//end/EXIT_1.png'),
            'menu//end//EXIT_2': load_image('menu//end/EXIT_2.png'),
        }
        
        #âm thanh game
        self.sfx = {
            'jump': pygame.mixer.Sound('data//sfx//jump.wav'),
            'dash': pygame.mixer.Sound('data//sfx//dash.wav'),
            'hit': pygame.mixer.Sound('data//sfx//hit.wav'),
            'shoot': pygame.mixer.Sound('data//sfx//shoot.wav'),
            'ambience': pygame.mixer.Sound('data//sfx//ambience.wav'),
            'landing': pygame.mixer.Sound('data//sfx//landing.mp3'),
            'ouch': pygame.mixer.Sound('data//sfx//ouch.mp3'),
            'start': pygame.mixer.Sound('data//sfx//start.mp3'),
            'click': pygame.mixer.Sound('data//sfx//click.mp3'),
            'hover': pygame.mixer.Sound('data//sfx//hover.mp3'),
            'skill': pygame.mixer.Sound('data//sfx//skill.MP3'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.2)
        self.sfx['hit'].set_volume(0.3)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.5)
        self.sfx['landing'].set_volume(0.4)
        self.sfx['ouch'].set_volume(0.1)
        self.sfx['start'].set_volume(1.2)
        self.sfx['click'].set_volume(1.2)
        self.sfx['hover'].set_volume(1)
        self.sfx['skill'].set_volume(1)
        

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

        # Đọc nội dung file JSON hiện tại
        with open(self.user_path, 'r') as file:
            data = json.load(file)

        self.level = data['user']['level'] #biến lưu màn chơi

        self.load_level(self.level)

        self.dead = 0 #kiểm tra người chơi đã chết chưa

        self.screenshake = 0 #rung cam

        self.transition = -50

        # hiển số địch còn lại
        self.font = pygame.font.Font('data//font//CyberpunkCraftpixPixel.otf', 32)
        self.menu_font = pygame.font.Font('data//font//CyberpunkCraftpixPixel.otf', 19)
        self.end_font = pygame.font.Font('data//font//CyberpunkCraftpixPixel.otf', 35)
        
        #đếm số npc còn lại
        self.enemies_count = self.font.render(": "+str(len(self.enemies)), True,(0, 255, 0))
        self.enemies_countRect = self.enemies_count.get_rect()
        self.enemies_countRect = (640//2,480//2)
        self.enemy_img = pygame.transform.scale(load_image('entities//enemy//idle//0.png'),(35,35))

        # hiển thị máu người chơi
        self.health_player_count = self.font.render(": "+str(self.player.health), True,(0, 255, 0))
        self.health_player_countRect = self.enemies_count.get_rect()
        self.health_player_countRect = (640//2,480//2)
        self.player_img = pygame.transform.scale(load_image('entities//player//idle//0.png'),(35,35))

        #hiển thị hồi chiêu người chơi
        self.skill_img = pygame.transform.scale(load_image('skill.png'),(25,25))
        self.skill_img_cd = pygame.transform.scale(load_image('skill_cd.png'),(25,25))

        #hiển thị thông báo hết game:
        self.endGameText = self.font.render("Done!", True,(0, 255, 0))

    def load_level(self,map_id):
        self.tilemap.load('data//maps//' + str(map_id) +'.json')

        self.projectiles = []
        self.skills = []

        self.enemies = []
        self.spec_enemies = []
        self.bosses = []
        for spawner in self.tilemap.extract([('spawners',0),('spawners',1),('spawners',2),('spawners',3)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.health = 300
            elif spawner['variant'] == 1:
                self.enemies.append(Enemy(self,spawner['pos'],(8,15)))
            elif spawner['variant'] == 2:
                self.spec_enemies.append(Spec_Enemy(self,spawner['pos'],(8,15)))
            elif spawner['variant'] == 3:
                self.bosses.append(Boss(self,spawner['pos'],(8,15)))

    def save_level(self,level):
        # Đọc nội dung file JSON hiện tại
        with open(self.user_path, 'r') as file:
            data = json.load(file)

        # Cập nhật giá trị level
        data['user']['level'] = level  # Thay đổi giá trị level thành 10 (hoặc bất kỳ giá trị nào bạn muốn)

        # Ghi lại dữ liệu đã cập nhật vào file JSON
        with open(self.user_path, 'w') as file:
            json.dump(data, file, indent=4)

    def enemies_upd(self):
        remain = len(self.enemies) + len(self.spec_enemies) + len(self.bosses)
        return remain

    def run(self):
        run = True

        while run:

            self.display.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake -1) #rung cam

            # if not len(self.enemies)  and not len(self.spec_enemies) and not len(self.bosses):
            if not self.enemies_upd():
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data//maps')) - 1)
                    print(self.level)
                    self.save_level(self.level)
                    self.transition = -50  # tạo lại hiệu ứng chuyển cảnh khi qua màn
                    self.load_level(self.level)
                    
            if ((len(os.listdir('data//maps')) - 1) == self.level) and not self.enemies_upd():
                self.level += 1
                self.endGame()
                    

            if self.transition < 0:
                self.transition += 1

            if self.dead == 1:
                self.projectiles.clear()
                self.skills.clear()
                self.load_level(self.level)
                self.dead = 0
                self.player.health = 300 #hồi lại đầy máu


            # di chuyển cam
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # # tạo lá
            # for rect in self.leaf_spawners:
            #     if random.random() * 49999 < rect.width * rect.height:
            #         pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
            #         self.particles.append(particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

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
                        # self.particles.append(particle(self, 'particle', skill.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
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
                # if part.type == 'leaf':
                #     part.pos[0] += math.sin(part.animation.frame * 0.035) * 0.3 #giảm tốc độ hết 1 vòng lặp
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
                        self.pause()

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
            self.enemies_count = self.font.render(": "+str(self.enemies_upd()), True,(0, 255, 0))
            self.screen.blit(self.enemy_img,(515,20))
            self.screen.blit(self.enemies_count,(555,20))
            
            #hiển thị máu người chơi
            self.health_player_count = self.font.render(": "+str(self.player.health)+"/300", True,(0, 255, 0))
            self.screen.blit(self.player_img,(0,20))
            self.screen.blit(self.health_player_count,(50,20))

            #hiển thị hồi chiêu người chơi
            self.space_text = self.font.render(": Space", True,(0, 255, 0))
            if(self.player.cooldown_skill > 0):
                self.screen.blit(self.skill_img_cd, (5,70))
                self.screen.blit(self.space_text,(35,70))
            else:
                self.screen.blit(self.skill_img, (5,70))
                self.screen.blit(self.space_text,(35,70))

            #hiển thị level hiện tại:
            self.level_count = self.font.render("level: "+str(self.level),True, (0, 255, 0))
            
            #hiển thị FPS:
            self.fps_count = self.font.render(str(self.clock.get_fps()),True, (0, 255, 0))

            self.screen.blit(self.level_count,(30,450))
            self.screen.blit(self.fps_count,(600,440))

            pygame.display.update()
            self.clock.tick(60)

    def menu(self):

        text_color = [(255,16,0), (224, 199, 69), (181, 255, 116)]
        slogan_text = self.menu_font.render("Hunt your foes, dash to victory!", True, (255,16,0))
        
        start_img = self.assets['menu//main//START_1']
        start_img_hover = self.assets['menu//main//START_2']
        start_button = Button(self,265,225,start_img, 0.4, start_img_hover)

        continue_img = self.assets['menu//main//CONTINUE_1']
        continue_img_hover = self.assets['menu//main//CONTINUE_2']
        continue_button = Button(self,425,225,continue_img, 0.4, continue_img_hover)


        tutor_img = self.assets['menu//main//TUTORIAL_1']
        tutor_img_hover = self.assets['menu//main//TUTORIAL_2']
        turtor_button = Button(self,263,300,tutor_img, 0.4, tutor_img_hover)
        
        exit_img = self.assets['menu//main//EXIT_1']
        exit_img_hover = self.assets['menu//main//EXIT_2']
        exit_button = Button(self,265,375,exit_img, 0.4,exit_img_hover)

        # Danh sách ảnh sẽ đổi trong thời gian hiện hành của menu
        title_images = [self.assets['menu//main//TITLE_1'], self.assets['menu//main//TITLE_2'], self.assets['menu//main//TITLE_3']]
        current_title_index = 0
        title_img = title_images[current_title_index]
        
        background_list = self.assets['menu//main//background'].copy()
        current_background_index = 0
        background = pygame.transform.scale(background_list[current_background_index], (640,480))

        # Đặt bộ đếm thời gian giữa mỗi lần hiển thị thay đổi
        title_switch_time = 1000  # mỗi 1 giây đổi màu title
        last_switch_time = pygame.time.get_ticks()
        
        background_switch_time = 3000  # mỗi 5 giây sẽ đổi 1 background
        bg_last_switch_time = pygame.time.get_ticks()

        pygame.mixer.music.load('data//music.mp3')
        pygame.mixer.music.set_volume(0.01)
        pygame.mixer.music.play(-1)
        
        # Đọc nội dung file JSON hiện tại
        with open(self.user_path, 'r') as file:
            data = json.load(file)

        while True:
            # kiểm tra thời gian để thay đổi ảnh
            current_time = pygame.time.get_ticks()
            if current_time - last_switch_time > title_switch_time:
                current_title_index = (current_title_index + 1) % len(title_images)
                title_img = title_images[current_title_index]
                slogan_text = self.menu_font.render("Hunt your foes, dash to victory!", True, text_color[current_title_index])
                last_switch_time = current_time

            if current_time - bg_last_switch_time > background_switch_time:
                current_background_index = (current_background_index + 1) % len(background_list) #tăng chỉ số của nền hiện tại
                background = pygame.transform.scale(background_list[current_background_index], (640,480))
                bg_last_switch_time = current_time #cập nhật thời gian chuyển


            # vẽ ảnh + chữ lên menu
            self.screen.blit(background, (0,0))
            self.screen.blit(title_img, (-33, -1))
            self.screen.blit(slogan_text,(135,175))

            #nút
            if start_button.draw(self.screen):
                self.sfx['start'].play()
                # Cập nhật giá trị level về 0 khi ấn vào nút start
                self.level = 0 
                self.save_level(self.level)

                self.load_level(self.level)
                self.run()
                
            if exit_button.draw(self.screen):
                pygame.quit()
                sys.exit()
                
            if turtor_button.draw(self.screen):
                self.tutorial()
            
            if data['user']['level'] > 0:
                if continue_button.draw(self.screen):
                    self.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    return
            
            pygame.display.update()
            self.clock.tick(60)

    def tutorial(self):
        
        running = True
        
        while running:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Nhấn ESC để thoát tutorial
                        running = False
            # Vẽ nội dung tutorial
            tutor_content = pygame.transform.scale(self.assets['menu//main//TUTOR'],(630,480))
            self.screen.blit(tutor_content,(0,0))
            
            # Cập nhật màn hình
            pygame.display.update()
            self.clock.tick(60)

    def pause(self):
        running = True
        pause_title = self.menu_font.render("Paused!", True, (255,16,0))

        resume_img = self.assets['menu//pause//RESUME_1']
        resume_img_hover = self.assets['menu//pause//RESUME_2']
        resume_button = Button(self,0,200,resume_img, 0.4, resume_img_hover)

        menu_img = self.assets['menu//pause//MENU_1']
        menu_img_hover = self.assets['menu//pause//MENU_2']
        menu_button = Button(self,0,275,menu_img, 0.4, menu_img_hover)

        exit_img = self.assets['menu//pause//EXIT_1']
        exit_img_hover = self.assets['menu//pause//EXIT_2']
        exit_button = Button(self,0,350,exit_img, 0.4, exit_img_hover)

        while running:
            if resume_button.draw(self.screen):
                self.run()
            if menu_button.draw(self.screen):
                self.menu()
            if exit_button.draw(self.screen):
                pygame.quit()
                sys.exit()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            self.display.blit(pause_title, (35,175))
            pygame.display.update()
            self.clock.tick(60)
    
    def endGame(self):
        running = True

        # Tải hình ảnh và tạo nút
        restart_img = self.assets['menu//end//RESTART_1']
        restart_img_hover = self.assets['menu//end//RESTART_2']
        restart_button = Button(self, 125, 400, restart_img, 0.4, restart_img_hover)

        exit_img = self.assets['menu//end//EXIT_1']
        exit_img_hover = self.assets['menu//end//EXIT_2']
        exit_button = Button(self, 350, 400, exit_img, 0.4, exit_img_hover)

        # Tạo văn bản và thiết lập vị trí ban đầu
        text = self.end_font.render('CONGRATULATION!!!', True, (255, 0, 0))
        text_rect_1 = text.get_rect(center=(self.screen.get_width() // 2, -100))  # Bắt đầu từ ngoài màn hình
        text_2 = self.end_font.render('Wanna Play Again?', True, (255, 0, 0))
        text_rect_2 = text_2.get_rect(center=(-150, self.screen.get_height() // 2))  # Bắt đầu từ ngoài màn hình

        while running:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                

            # Cập nhật vị trí văn bản
            if text_rect_2.x < 140:
                text_rect_2.x += 4

            if text_rect_1.y < 175:
                text_rect_1.y += 3

            # if text_rect_2.right > :
            # if text_rect_1.top > self.screen.get_height():
            #     text_rect_1.bottom = -100  # Đặt lại vị trí văn bản khi nó ra khỏi màn hình

            # Làm sạch màn hình
            self.screen.fill((0, 0, 0))  # Hoặc màu nền khác bạn muốn

            # Vẽ nút và văn bản
            self.screen.blit(text, text_rect_1)
            self.screen.blit(text_2, text_rect_2)

            if restart_button.draw(self.screen):
                self.level = 0
                self.save_level(self.level)
                self.load_level(self.level)
                self.run()

            if exit_button.draw(self.screen):
                pygame.quit()
                sys.exit()

            # Cập nhật màn hình
            pygame.display.update()
            self.clock.tick(60)


# # Run the game
if __name__ == "__main__":
    Test().menu()
