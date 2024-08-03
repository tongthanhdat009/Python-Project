import pygame


class Bullet:
    def __init__(self, game, x, y, direction, time = 0, damage = 25):
        self.game = game
        self.x = x
        self.y = y
        self.direction = direction
        self.time = time
        self.damage = damage
        self.width = 6
        self.height = 4
    
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, img, render_scroll):
        self.game.display.blit(img,(self.x - img.get_width()/2 - render_scroll[0], self.y - img.get_height() /2 - render_scroll[1]))

    def bullet_solid_check(self):
        if self.game.tilemap.solid_check([self.x,self.y]):
            return True
        else:
            return False
        
    def time_checker(self):
        self.time += 1
        if self.time > 360:
            return True
        else:
            return False
    
    def player_checker(self,):
        if self.game.player.rect().collidepoint([self.x,self.y]):
            return True
        else:
            return False
    
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
    


    def x_update(self):
        self.x += self.direction
    
    def y_update(self):
        self.y += self.direction