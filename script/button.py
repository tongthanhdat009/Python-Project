import pygame


class Button():
    def __init__(self, game, x, y, image, scale, hover):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.hover = pygame.transform.scale(hover, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False
        self.type = type
        self.game = game
        self.hover_played = False

    def draw(self, screen):
        action = False
        # Lấy vị trí trỏ chuột
        pos = pygame.mouse.get_pos()
        
        # Kiểm tra chuột có trong vùng của nút không
        if self.rect.collidepoint(pos):
            # Nếu chuột vào vùng nút và âm thanh hover chưa được phát
            if not self.hover_played:
                self.game.sfx['hover'].play()
                self.hover_played = True

            screen.blit(self.hover, (self.rect.x, self.rect.y))
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:  # Kiểm tra nếu chuột được nhấn chuột trái
                self.game.sfx['click'].play()
                self.clicked = True
                action = True
            if pygame.mouse.get_pressed()[0] == 0 and self.clicked:  # Nếu chuột không còn nhấn
                self.clicked = False
        else:
            # Nếu chuột không ở trong vùng nút, vẽ nút lên menu
            screen.blit(self.image, (self.rect.x, self.rect.y))
            self.hover_played = False  # Reset trạng thái khi chuột rời khỏi vùng nút

        return action