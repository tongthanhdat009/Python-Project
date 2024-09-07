import random
import pygame

class spaceship:
    def __init__(self,pos,img,speed,depth):
        self.pos = list(pos)
        self.img = pygame.transform.scale(img, (55,20))
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed
    
    def render(self, surf, offset=(0,0)):
        render_pos=(self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1]*self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) -self.img.get_width(),render_pos[1] % (surf.get_height() + self.img.get_height())-self.img.get_height()))
class spaceships:
    def __init__(self, space_ship_images, count=16):
        self.space_ships =[]
        
        #chọn xuất ngẫu nhiên mây
        for i in range(count):
            self.space_ships.append(spaceship((random.random()*99999,random.random()*99999),random.choice(space_ship_images), random.random()*0.05+0.05, random.random()*0.6+0.2))

        self.space_ships.sort(key=lambda x: x.depth)
    
    def update(self):
        for space_ship in self.space_ships:
            space_ship.update()
    
    def render(self, surf, offset=(0,0)):
        for space_ship in self.space_ships:
            space_ship.render(surf, offset=offset)