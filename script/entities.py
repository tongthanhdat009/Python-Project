import math
import random
import pygame
from script.particles import particle
from script.spark import Spark

class PhysicsEntity:
    def __init__ (self, game, e_type, pos, size):
        self.game = game
        self.e_type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up':False, 'down': False, 'right':False, 'left':False}

        self.action=''
        self.anim_offset=(-3,-3)
        self.flip = False
        self.set_action('idle')
        self.last_movement = [0,0]
    
    def rect(self):
        return pygame.Rect(self.pos[0],self.pos[1], self.size[0], self.size[1])
    
    #đặt hành đông
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.e_type + '//' + self.action].copy()

    #cập nhật vị trí nhân vật
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up':False, 'down': False, 'right':False, 'left':False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        # self.char_pos[0] += (self.movement[3] - self.movement[2])*5 #tọa độ di chuyển trái phải
        # self.char_pos[1] += (self.movement[1] - self.movement[0])*5 #tọa độ di chuyển lên xuống
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
    
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1]+0.1) #điều chỉnh vận tốc rơi

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()
    
    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(),self.flip,False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1]-offset[1]+self.anim_offset[1]))

#kế thừa
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size, health=150):
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 0 #di chuyển
        self.health = health  #máu
        
    def take_damage(self, amount=20): #giảm máu npc nếu bị player dash trúng
        self.health -= amount
        if self.health <= 0:
            self.die()
            
    def die(self): #xóa npc nếu máu < 0
        self.game.sfx['hit'].play()
        for i in range(30):  # hiẹu ứng khi chết 
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
            self.game.particles.append(particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
        self.game.enemies.remove(self)  
        
    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)): #điều kiện chuyển hướng cho npc
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking: #cho npc đứng yên để bắn
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement)
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        
        #player dash trúng sẽ trừ máu enemy
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()): #kiểm tra nếu player dash trúng npc thì sẽ trừ máu npc
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                self.take_damage(abs(self.game.player.dashing))  
                self.game.player.stop_dash()
                return True
            
        # trừ máu player nếu layer player đè trên enemy  
        if self.rect().colliderect(self.game.player.rect()) and abs(self.game.player.dashing) < 50:
            damage_amount = 1  # lượng máu sẽ giảm
            self.game.player.health -= damage_amount  # giảm máu
            self.game.sfx['hit'].play()
            if self.game.player.health <= 0:
                self.game.dead += 1
                #reset hiệu ứng chuyển cảnh
                self.game.transition = -50
                if self.game.transition:
                    transition_surf = pygame.Surface(self.game.display.get_size())
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.game.display.get_width() // 2, self.game.display.get_height() // 2), (30 - abs(self.game.transition)) * 8)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.game.display.blit(transition_surf, (0, 0))
                self.game.player.health = self.health
                self.game.player.cooldown_skill = 0
            else:
                self.game.dead = 0
            return True    

    def hit(self, amount = 20):
        self.take_damage(amount)

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
        #render súng cho npc đúng chiều và ngược chiều
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 8 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 8 - offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size, health=50):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0 # thời gian trên không
        self.jump_count = 2 #số lần nhảy
        self.wall_slide = False #kiểm tra bám tường
        self.dashing = 0 #kiểm tra lướt
        self.health = health #máu
        self.cooldown_skill = 0 # thời gian hồi chiêu
        self.skill_dmg = 1000
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        
        if self.air_time > 160:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1 #rơi ra khỏi map tự reset

        #kiểm tra rơi
        if self.collisions['down']:
            if self.air_time > 5:
                self.game.sfx['landing'].play()
            self.air_time=0
            self.jump_count = 2

        #kiểm tra rơi khi chạm tường
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4: #chạm tường bên trái hoặc phải nhân vật sẽ kích hoạt trượt tường
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        #nếu rơi không chạm tường
        if not self.wall_slide:
            if self.air_time > 4:
                if self.jump_count == 0: #nếu số lần nhảy = 0 thì sẽ chạy hoạt ảnh double_jump
                    self.set_action('double_jump')
                else:
                    self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        #giảm tốc độ và thời gian hồi dash
        self.stop_dash()
        
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)   
        else:     
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)   

        # kiểm tra giảm thời gian hồi chiêu
        if self.cooldown_skill > 0:
            self.cooldown_skill -= 50  
        if self.cooldown_skill < 0:
            self.cooldown_skill = 0  

    def render(self, surf,offset=(0,0)):
        if abs(self.dashing) <= 50:
            super().render(surf,offset=offset)

    #giảm tốc độ và thời gian hồi dash
    def stop_dash(self):
        if self.dashing > 0 :
            self.dashing = max(0,self.dashing - 1)
        if self.dashing < 0 :
            self.dashing = min(0,self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8    
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1 #thời gian hồi lại dash
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame=random.randint(0,7)))
        if abs(self.dashing) in {60,50}:
            for i  in range(20):
                angle = random.random() * math.pi * 2 #gốc lướt
                speed = random.random() * 0.5 * 0.5#tốc độ lướt
                pvelocity = [math.cos(angle)*speed,math.sin(angle)*speed]
                self.game.particles.append(particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame=random.randint(0,7)))

    #hàm kiểm soát việc nhảy của nhân vật
    def jump_perform(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.game.sfx['jump'].play()
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jump_count = max(0, self.jump_count - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.game.sfx['jump'].play()
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jump_count = max(0, self.jump_count - 1)
                return True 

        elif self.jump_count:
            self.velocity[1] = -3 #độ cao khi nhảy
            if self.jump_count == 0:
                self.set_action('double_jump')
                self.game.sfx['jump'].play()
            else:
                self.game.sfx['jump'].play()
                self.set_action('jump')
            self.jump_count -= 1 # giới hạn số lần nhảy
            self.air_time = 5 # thời gian trên không
            return True
        
        
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.game.sfx['dash'].play()
                self.dashing = -60
            else: 
                self.game.sfx['dash'].play()
                self.dashing = 60
    
    def hit(self):
        self.game.sfx['hit'].play()                    
        self.game.player.health -= 10
        if self.game.player.health <= 0:
            self.game.dead += 1
            #reset hiệu ứng chuyển cảnh
            self.game.transition = -50
            if self.game.transition:
                transition_surf = pygame.Surface(self.game.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.game.display.get_width() // 2, self.game.display.get_height() // 2), (30 - abs(self.game.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.game.display.blit(transition_surf, (0, 0))
            self.game.player.health = 150
            self.cooldown_skill = 0
        else:
            self.game.dead = 0
            
    def skill(self):
        if self.cooldown_skill == 0:
            if (self.game.player.flip):
                self.game.sfx['shoot'].play()
                self.game.projectiles_player.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                for i in range(4):
                    self.game.sparks.append(Spark(self.game.projectiles_player[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
            if (not self.game.player.flip):
                self.game.sfx['shoot'].play()
                self.game.projectiles_player.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                for i in range(4):
                    self.game.sparks.append(Spark(self.game.projectiles_player[-1][0], random.random() - 0.5, 2 + random.random()))
            self.cooldown_skill = 60 # thời gian hồi chiêu
        
    def display_bullet(self, render_scroll):
        for projectile_p in self.game.projectiles_player.copy():
            projectile_p[0][0] += projectile_p[1]
            projectile_p[2] += 1
            img = self.game.assets['projectile']

            draw_x = projectile_p[0][0] - img.get_width() / 2 - render_scroll[0]
            draw_y = projectile_p[0][1] - img.get_height() / 2 - render_scroll[1]

            self.game.display.blit(img, (draw_x, draw_y))

            if self.game.tilemap.solid_check(projectile_p[0]):  # Đạn biến mất nếu gặp vật cản
                self.game.projectiles_player.remove(projectile_p)
            elif projectile_p[2] > 360:  # Thời gian đạn tồn tại
                self.game.projectiles_player.remove(projectile_p)
            else:
                bullet_rect = pygame.Rect(draw_x, draw_y, img.get_width(), img.get_height())
                for enemy in self.game.enemies:
                    if bullet_rect.colliderect(enemy.rect()):
                        print(f"Bullet rect: {bullet_rect}, Enemy rect: {enemy.rect()}")  # Kiểm tra tọa độ va chạm
                        self.game.projectiles_player.remove(projectile_p)
                        enemy.take_damage(20)  # Gọi hàm để trừ máu địch
                        break

