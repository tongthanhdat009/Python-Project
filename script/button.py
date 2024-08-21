import pygame
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