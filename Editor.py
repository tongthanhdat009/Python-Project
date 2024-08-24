import sys
import pygame
import json



from script.utils import load_images, animation
from script.tilemap import Tilemap

RENDER_SCALE = 2.0

class Editor:
    def __init__(self):#khởi tạo cửa sỏ    
        pygame.init()

        pygame.display.set_caption("editor") # đổi tiêu đề cửa sổ
        self.screen = pygame.display.set_mode((640,480))
        self.display = pygame.Surface((320,240))

        self.clock = pygame.time.Clock()
        
        self.path = 'data//maps//0.json'
        self.user_path = 'data//user.json'
        

        #hình ảnh
        self.assets = {
            'decor': load_images('tiles//decor'),
            'grass': load_images('tiles//grass'),
            'large_decor': load_images('tiles//large_decor'),
            'stone': load_images('tiles//stone'),
            'spawners': load_images('tiles//spawners'),
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
        }
        print(self.assets)
        
        self.movement = [False,False,False,False]
        

        #đối tượng vật thể trong map
        self.tilemap = Tilemap(self,tile_size=16)
        
        try:
            self.tilemap.load(self.path)
        except FileNotFoundError:
            pass


        #điều chỉnh camera
        self.scroll = [0,0]

        
        self.tile_list = list(self.assets)#chuyển asset thành mảng
        self.tile_group = 0 #vật cản
        self.tile_variant = 0 #biến thể của vật cản

        #kiểm tra nhấp chuột
        self.clicking= False
        self.right_clicking = False
        
        #kiểm tra nhấn shift trái
        self.shift = False

        #kiểm tra trong khu vật chia 
        self.ongrid = True

    def run(self):#chạy game
        run = True
        
        while run:
            self.display.fill((0,0,0))

            #di chuyển cam để tạo map: (bằng phím mũi tên)
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]),int(self.scroll[1]))

            #tạo map:
            render_scroll = (int(self.scroll[0]),int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll) 

            # hiển thị những phần vật cản đã chọn trong tile list
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            # vị trí chuột trong game
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0]+self.scroll[0]) // self.tilemap.tile_size),int((mpos[1] + self.scroll[1])//self.tilemap.tile_size))
            # print(mpos)

            if self.ongrid:
                self.display.blit(current_tile_img,(tile_pos[0] * self.tilemap.tile_size-self.scroll[0],tile_pos[1]*self.tilemap.tile_size-self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)

            #thêm thành phần map bằng click chuột
            if self.clicking and self.ongrid:
                #thêm thành phần 
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
                
            # xóa 1 thành phần bằng cách giữa chụp phải
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1]-self.scroll[1],tile_img.get_width(),tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)
            
            self.display.blit(current_tile_img,(5,5))

            for event in pygame.event.get(): #sự kiện tương tác trong game
                #cài đặt nút di chuyển 
                #di chuyển bằng WASD hoặc mũi tên
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key==pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key==pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key==pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN or event.key==pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_g: # chỉnh trên đường viền 
                        self.ongrid = False
                    if event.key == pygame.K_o: #lưu map đang tạo
                        self.tilemap.save(self.path)
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                    

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key==pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key==pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_UP or event.key==pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN or event.key==pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_g: # chỉnh trên đường viền 
                        self.ongrid = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
                        
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tile.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos':(mpos[0]+self.scroll[0],mpos[1]+self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    #chuyển loại vật cản bằng cách bấm shift
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])#hiển thị biến thể bằng lăn chuột lên
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])#hiển thị biến thể bằng lăn chuột xuống
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)#hiển thị vật cản bằng lăn chuột lên
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)#hiển thị vật cản bằng lăn chuột xuống
                            self.tile_variant = 0
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False
                        

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            

            self.screen.blit(pygame.transform.scale(self.display,self.screen.get_size()),(0,0))
            pygame.display.update()
            self.clock.tick(60) #cài đặt 60fps

Editor().run()