import pygame

class Bullet:
    def __init__(self, game, x, y, direction, time = 0, damage = 25):
        self.game = game
        self.x = x # tọa độ hoành
        self.y = y # tọa độ tung
        self.direction = direction # vị trí hay khoảng được cộng thêm khi đạn bay
        self.time = time # thời gian đạn biến mất khi không gặp vật cản
        self.damage = damage # sát thường từ đạn
        self.width = 6 # chiều rộng của đạn
        self.height = 4 # chiều cao của đạn
    
    #đối tượng chứa ảnh đạn
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    #vẽ đạn
    def render(self, img, render_scroll):
        self.game.display.blit(img,(self.x - img.get_width()/2 - render_scroll[0], self.y - img.get_height() /2 - render_scroll[1]))

    #kiểm tra xem đạn có chạm tường không
    def bullet_solid_check(self):
        if self.game.tilemap.solid_check([self.x,self.y]):
            return True
        else:
            return False
        
    #kiểm tra thời gian đạn tồn tại
    def time_checker(self):
        self.time += 1
        if self.time > 360:
            return True
        else:
            return False
    
    #kiểm tra đạn chạm người chơi
    def player_checker(self,):
        if self.game.player.rect().collidepoint([self.x,self.y]):
            return True
        else:
            return False
    
    #kiểm tra skill nhân vật chạm npc
    def enemy_class_checker(self, skill, enemies, spec_enemies, dmg):
        for enemy in enemies:
            if skill.rect().colliderect(enemy.rect()):
                enemy.take_damage(dmg)
                return True
            
        for enemy in spec_enemies:
            if skill.rect().colliderect(enemy.rect()):
                enemy.take_damage(dmg)
                return True
            
        return False
    
    #cập nhật trục hoành
    def x_update(self):
        self.x += self.direction
    
    #cập nhật trục tung
    def y_update(self):
        self.y += self.direction