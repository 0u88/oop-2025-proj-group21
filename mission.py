import pygame

class MissionZone:
    def __init__(self, x, y, width, height, description, effect, repeatable=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.description = description
        self.effect = effect
        self.triggered = False
        self.repeatable = repeatable

    def check_trigger(self, cat):
        if self.rect.colliderect(pygame.Rect(cat.x, cat.y, 32, 48)):
            if self.repeatable or not self.triggered:
                result = self.effect(cat)
                if result and not self.repeatable:
                    self.triggered = True

    #def draw(self, screen):
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


