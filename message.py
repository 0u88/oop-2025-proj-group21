import pygame

class MessageManager:
    def __init__(self, font):
        self.font = font
        self.messages = []  # 每個訊息是一個 dict
        self.mode = "default"  

    def set_mode(self, mode):
        self.mode = mode 

    def add(self, text, duration=2000):
        self.messages.append({
            "text": text,
            "start_time": pygame.time.get_ticks(),
            "duration": duration,
        })

    def update(self):
        now = pygame.time.get_ticks()
        self.messages = [
            msg for msg in self.messages
            if now - msg["start_time"] < msg["duration"]
        ]

    def draw(self, screen, pos=(400, 550)):
        if not self.messages:
            return

        now = pygame.time.get_ticks()
        msg = self.messages[0]  # 只顯示第一則
        elapsed = now - msg["start_time"]
        duration = msg["duration"]

        # 淡出 alpha（最後 1000ms 淡出）
        alpha = 255
        if elapsed > duration - 1000:
            alpha = max(0, int(255 * (duration - elapsed) / 1000))
        # ---- 根據 mode 設定框框顏色 ----
        if self.mode == "battle":
            bg_color = (250, 200, 200, alpha)
            border_color = (180, 50, 50, alpha)
            text_color = (100, 0, 0)
            box_width = 230
            box_height = 60

        else:  # default
            bg_color = (255, 240, 200, alpha)
            border_color = (200, 180, 140, alpha)
            text_color = (50, 30, 30)
            box_width = 600
            box_height = 50

        # 米色對話框樣式
        #box_width = 600
        #box_height = 60
        box_x, box_y = pos
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        msg_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        # 使用 mode 設定的顏色
        pygame.draw.rect(msg_surface, bg_color, msg_surface.get_rect(), border_radius=15)
        pygame.draw.rect(msg_surface, border_color, msg_surface.get_rect(), width=2, border_radius=15)

        text_surface = self.font.render(msg["text"], True, text_color)  # ✅ 使用根據 mode 的顏色
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(box_width // 2, box_height // 2))
        msg_surface.blit(text_surface, text_rect)

        screen.blit(msg_surface, (box_x, box_y))
