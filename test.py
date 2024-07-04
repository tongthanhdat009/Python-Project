import sys
import pygame


from script.entities import PhysicsEntity, Player
from script.utils import load_image, load_images, animation
from script.tilemap import Tilemap
from script.clouds import clouds
class test:
    def __init__(self):#khởi tạo cửa sỏ    
        pygame.init()

        pygame.display.set_caption("test") # đổi tiêu đề cửa sổ
        self.screen = pygame.display.set_mode((640,480))
        self.display = pygame.Surface((320,240))

        self.clock = pygame.time.Clock()

        #ảnh bầu trời
        try:
            self.bg = pygame.image.load('data//images//background.png')
            self.bg = pygame.transform.scale(self.bg, (640,480))  # Resize the image
        except FileNotFoundError:
            print("Background image file not found.")
            self.bg = None

        self.movement = [False,False,False,False]

        #hình ảnh
        self.assets = {
            'decor': load_images('tiles//decor'),
            'grass': load_images('tiles//grass'),
            'large_decor': load_images('tiles//large_decor'),
            'stone': load_images('tiles//stone'),
            'player': load_image('entities//player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player//idle': animation(load_images('entities//player//idle'),img_dur=6),
            'player//run': animation(load_images('entities//player//run'),img_dur=4),
            'player//jump': animation(load_images('entities//player//jump')),
            'player//slide': animation(load_images('entities//player//slide')),
            'player//wall_slide': animation(load_images('entities//player//wall_slide')),
        }
        print(self.assets)

        #đối tượng mây
        self.clouds = clouds(self.assets['clouds'],count=10)

        #đối tượng người chơi
        self.player = Player(self, (50,50), (8,15))

        #đối tượng vật thể trong map
        self.tilemap = Tilemap(self,tile_size=16)

        #điều chỉnh camera
        self.scroll = [0,0]

        #tải map:
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
    def run(self):#chạy game
        run = True

        while run:
            self.display.blit(self.assets['background'],(0,0))
            
            #cho cam tự di chuyển
            # self.scroll[0]+=1
            self.scroll[0] += (self.player.rect().centerx-self.display.get_width()/2-self.scroll[0])/30
            self.scroll[1] += (self.player.rect().centery-self.display.get_width()/2-self.scroll[1])/30
            render_scroll = (int(self.scroll[0]),int(self.scroll[1]))
            
            #tạo vật thể trong map
            self.tilemap.render(self.display,offset=render_scroll)            

            self.clouds.update()
            self.clouds.render(self.display,offset=render_scroll)

            #spawn
            self.player.update(self.tilemap,(self.movement[1]-self.movement[0],0))
            self.player.render(self.display,offset=render_scroll)


            for event in pygame.event.get(): #sự kiện tương tác trong game
                #cài đặt nút di chuyển 
                #di chuyển bằng WASD hoặc mũi tên
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key==pygame.K_w:
                        self.player.velocity[1] = -3
                    #     self.movement[0] = True
                    # if event.key == pygame.K_DOWN or event.key==pygame.K_s:
                    #     self.movement[1] = True
                    if event.key == pygame.K_LEFT or event.key==pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key==pygame.K_d:
                        self.movement[1] = True

                if event.type == pygame.KEYUP:
                    # if event.key == pygame.K_DOWN or event.key==pygame.K_s:
                    #     self.movement[1] = False
                    if event.key == pygame.K_LEFT or event.key==pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key==pygame.K_d:
                        self.movement[1] = False
                        
                            
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.screen.blit(pygame.transform.scale(self.display,self.screen.get_size()),(0,0))
            pygame.display.update()
            self.clock.tick(60) #cài đặt 60fps

test().run()