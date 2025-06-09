import pygame
import random
import os

class BossCat:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame_index = 0
        self.anim_speed = 0.1  # 控制動畫速度
        self.frames = self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_hp = 5
        self.hp = self.max_hp


    def load_frames(self):
        folder = "assets/boss"
        frames = []
        for i in range(4):  # 有 4 張圖 boss_frame_0.png ~ boss_frame_3.png
            path = os.path.join(folder, f"boss_punch_{i}.png")
            img = pygame.image.load(path).convert_alpha()
            frames.append(img)
        return frames
    
    def update(self):
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    '''''
    def take_damage(self, dmg):
        self.hp -= dmg

    def is_defeated(self):
        return self.hp <= 0
    '''
    def attack(self, target_cat):
        attack_type = random.choice(["normal", "claw", "scare", "fake"])

        if attack_type == "normal":
            target_cat.hp -= 1
            return "Boss 用了普通攻擊，你掉了 1 點血！"
        elif attack_type == "claw":
            target_cat.hp -= 2
            self.hp -= 1
            return "Boss 用爪擊！你掉 2 點血，牠自損 1 點！"
        elif attack_type == "scare":
            if target_cat.cute > 0:
                target_cat.cute -= 1
            return "Boss 嚇你一跳！你失去 1 點可愛！"
        elif attack_type == "fake":
            return "Boss 虛張聲勢，看起來兇但沒打中！"


