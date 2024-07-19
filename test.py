import math
import os
import random
import sys
import pygame

from script.entities import PhysicsEntity, Player, Enemy
from script.spark import Spark
from script.utils import load_image, load_images, animation
from script.tilemap import Tilemap
from script.clouds import clouds
from script.particles import particle

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
            'player': load_image('entities//player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player//idle': animation(load_images('entities//player//idle'), img_dur=6),
            'player//run': animation(load_images('entities//player//run'), img_dur=7),
            'player//jump': animation(load_images('entities//player//jump')),
            'player//double_jump': animation(load_images('entities//player//double_jump'),img_dur=4),
            'player//slide': animation(load_images('entities//player//slide')),
            'player//wall_slide': animation(load_images('entities//player//wall_slide')),
            'particle//leaf': animation(load_images('particles//leaf'), img_dur= 20, loop= False),
            'particle//particle': animation(load_images('particles//particle'), img_dur= 2, loop= False),
            'enemy//idle': animation(load_images('entities//enemy//idle'), img_dur= 6),
            'enemy//run': animation(load_images('entities//enemy//run'), img_dur= 4),
            'gun':load_image('gun.png'),
            'projectile':load_image('projectile.png'),
            'menu':load_image('menu//bg_menu.jpg')
        }
        
        #âm thanh game
        self.sfx = {
            'jump': pygame.mixer.Sound('data//sfx//jump.wav'),
            'dash': pygame.mixer.Sound('data//sfx//dash.wav'),
            'hit': pygame.mixer.Sound('data//sfx//hit.wav'),
            'shoot': pygame.mixer.Sound('data//sfx//shoot.wav'),
            'ambience': pygame.mixer.Sound('data//sfx//ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        # khởi tạo đối tượng:
        #mây
        self.clouds = clouds(self.assets['clouds'], count=5)

        # người chơi
        self.player = Player(self, (50, 50), (8, 15))

        # vật thể trong map
        self.tilemap = Tilemap(self, tile_size=16)
        self.scroll = [0, 0]

        self.particles = []

        self.projectiles = []

        self.sparks = [] # hiệu ứng tia lửa

        self.level = 0 #biến lưu màn chơi

        self.load_level(0)

        self.dead = 0 #kiểm tra người chơi đã chết chưa

        self.screenshake = 0 #rung cam

        self.transition = -30

    def load_level(self,map_id):
        self.tilemap.load('data//maps//' + str(map_id) +'.json')

        # tạo hoạt ảnh lá rơi
        self.leaf_spawners = []
        self.tilemap.extract([('large_decor', 2)], keep=True)
        
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13)) # 4 4 rơi từ trái trên xuống dưới trái phải
        
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners',0),('spawners',1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self,spawner['pos'],(8,15)))



    def run(self):
        run = True
        
        pygame.mixer.music.load('data//music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # self.sfx['ambience'].play(-1)

        while run:
            self.display.fill((0,0,0,0))
            self.display_2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake -1) #rung cam

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data//maps')) - 1)
                    self.load_level(self.level)
                    self.transition = -30  # Reset transition after loading the new level
            if self.transition < 0:
                self.transition += 1

            if self.dead == 1:
                self.load_level(self.level)
                self.dead = 0 


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

            # cập nhật mây mỗi khi chuyển qua 1 khung hình
            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

            # cập nhật và hiển thị npc npc
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap,(0,0))
                enemy.render(self.display, offset = render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            # cập nhật và hiển thị nhân vật
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # tạo đạn
            # [[x, y], direction,timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img,(projectile[0][0] - img.get_width()/2 - render_scroll[0], projectile[0][1] - img.get_height() /2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]): #đạn biến mất nếu gặp vật cản
                    self.projectiles.remove(projectile)
                elif projectile[2] > 360: #thời gian đạn tồn tại
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing)<50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.screenshake = max(16, self.screenshake)
                        self.sfx['hit'].play()                    
                        
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            #hiệu ứng nổ khi trúng đạn
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                        self.dead += 1 #nhân vật trúng đạn sẽ chết và reset lại màn 0

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

            for offset in [(-1,0), (1,0),(0,-1),(0,1)]:
                self.display_2.blit(self.display,offset)

            #hiệu ứng rung màn hình
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,random.random() * self.screenshake - self.screenshake / 2 )
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)


            pygame.display.update()
            self.clock.tick(60)

    def menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.screen.blit(pygame.transform.scale(self.main_menu, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
            

# Run the game
if __name__ == "__main__":
    Test().run()
