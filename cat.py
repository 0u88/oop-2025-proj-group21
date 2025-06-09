import pygame
import os

class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.anim_speed = 0.2
        self.direction = "down"  # 預設面向下
        self.images = self.load_all_direction_images()
        self.current_images = self.images[self.direction]
        self.cute = 0
        self.power = 0
        self.has_box = False
        self.frame_index = 0     # 初始幀
        self.image = self.images[self.direction][self.frame_index]  # 取第一張圖
        self.rect = self.image.get_rect(topleft=(x, y))
        self.walkable_mask = None



    def load_all_direction_images(self):
        directions = ["up", "right", "down", "left"]
        images = {}
        for dir_name in directions:
            folder = os.path.join("assets/cat", dir_name)
            frames = [pygame.image.load(os.path.join(folder, img)).convert_alpha()
                      for img in sorted(os.listdir(folder)) if img.endswith(".png")]
            images[dir_name] = frames
        return images
    def set_walkable_mask(self, mask_surface):
        self.walkable_mask = mask_surface

    def is_walkable(self, x, y):
        if not self.walkable_mask:
            return True  # 若無遮罩預設都可走
        if 0 <= x < self.walkable_mask.get_width() and 0 <= y < self.walkable_mask.get_height():
            color = self.walkable_mask.get_at((x, y))
            return color.r > 128
        return False

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        # 檢查角色腳底中心點是否落在可行走區
        foot_x = new_x + self.rect.width // 2
        foot_y = new_y + self.rect.height - 5
        if self.is_walkable(foot_x, foot_y):
            self.x = new_x
            self.y = new_y
            self.rect.topleft = (self.x, self.y)
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            elif dy != 0:
                self.direction = "down" if dy > 0 else "up"
            self.set_state(self.direction)

    def set_idle(self):
        self.frame = 0

    def set_state(self, direction):
        self.current_images = self.images[direction]

    def update(self):
        self.frame += self.anim_speed
        if self.frame >= len(self.current_images):
            self.frame = 0

    def draw(self, screen):
        img = self.current_images[int(self.frame)]
        screen.blit(img, (self.x, self.y))

    def cute_attack(self, target_boss):
        if self.cute > 0:
            target_boss.hp -= 1
            self.cute -= 1
            return "你用了可愛攻擊！Boss 血量 -1"
        else:
            return "你不夠可愛了！"
    def power_attack(self, target_boss):
        if self.power > 0:
            target_boss.hp -= 2
            self.power -= 1
            return "你用了戰力攻擊！Boss 血量 -2"
        else:
            return "你沒有足夠戰力！"
    '''''
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        elif dy != 0:
            self.direction = "down" if dy > 0 else "up"
        self.set_state(self.direction)

    def set_idle(self):
        self.frame = 0

    def set_state(self, direction):
        self.current_images = self.images[direction]

    def update(self):
        self.frame += self.anim_speed
        if self.frame >= len(self.current_images):
            self.frame = 0

        self.image = self.current_images[int(self.frame)]  # 更新目前顯示圖片
        self.rect.topleft = (self.x, self.y)               # 同步碰撞區


    def draw(self, screen):
        img = self.current_images[int(self.frame)]
        screen.blit(img, (self.x, self.y))
'''