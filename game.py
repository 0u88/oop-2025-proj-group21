import pygame
import sys
from cat import Cat
from mission import MissionZone
from boss import BossCat
from message import MessageManager

WIDTH, HEIGHT = 800, 450

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Stray Cat Adventure")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("HiraginoSansGB", 24)
        self.msg_mgr = MessageManager(pygame.font.SysFont("HiraginoSansGB", 28))  # 訊息框用 28px 字體
        self.cat_msg_mgr = MessageManager(pygame.font.SysFont("HiraginoSansGB", 12))  # 貓咪攻擊訊息用 15px 字體
        self.boss_msg_mgr = MessageManager(pygame.font.SysFont("HiraginoSansGB", 12))
        self.prompt_mgr = MessageManager(pygame.font.SysFont("HiraginoSansGB", 28))
        self.status_box_img = pygame.image.load("assets/ui/status_box.png").convert_alpha()
        self.status_box_img = pygame.transform.scale(self.status_box_img, (200, 130))    
        self.bg = pygame.image.load("assets/bg/village_map_clean.png")
        self.cat = Cat(x=410, y=200)
        self.boss = BossCat(x=680, y=330)
        mask_surface = pygame.image.load("assets/bg/walkable_mask_scaled.png").convert()
        self.cat.set_walkable_mask(mask_surface)
        self.debug_mask = False
        self.heart_img = pygame.image.load("assets/ui/heart.png").convert_alpha()
        self.battle_result_shown = False
        self.rain_active = False
        self.rain_trigger_time = None
        #self.raindrops = [RainDrop() for _ in range(100)]
        self.start_ticks = pygame.time.get_ticks()
        self.in_boss_fight = False
        self.fight_started = False

        self.missions = [
            MissionZone(290,100,60,60, "撒嬌區域", self.beg_for_petting),
            MissionZone(510, 140, 30, 30, "圖書館出口", self.beg_for_food),
            MissionZone(510, 300, 40, 60, "屋簷避雨區", self.hide_from_rain),
            MissionZone(700, 200, 60, 60, "紙箱築巢區", self.find_box),
            MissionZone(410, 300, 60, 60, "磨爪訓練區", self.scratch_training),
            MissionZone(250, 300, 60, 60, "阿婆餵飯區", self.granny_feeds_too_much)
        ]

    def beg_for_petting(self, cat):
        if not hasattr(cat, "petting_done"):
            cat.cute += 1
            cat.petting_done = True
            self.msg_mgr.add("你對學生撒嬌成功，可愛值 +1")

            return True
        return False

    def beg_for_food(self, cat):
        if not hasattr(cat, "food_done"):
            if cat.cute < 1:
                self.msg_mgr.add("你喵了半天，路人沒理你...")
                return False
            else:
                cat.power += 1
                self.msg_mgr.add("你喵了一聲，得到了肉泥！戰力 +1！")
                return True

    def hide_from_rain(self, cat):
        if self.rain_trigger_time is None:
            return False  # 還沒下雨，直接跳過
        # 給 5 秒猶豫時間，之後判斷是否有成功避雨
        if not hasattr(cat, "rain_checked"):
            if pygame.time.get_ticks() - self.rain_trigger_time < 5000:
                return False

            cat.rain_checked = True
            if 490 <= cat.x <= 530 and 280 <= cat.y <= 320:
                self.msg_mgr.add("你成功躲雨，戰力沒有減少")
            else:
                cat.power -= 1
                self.msg_mgr.add("你被雨淋濕了... 戰力 -1")
            return True

        return False


    def find_box(self, cat):
        if cat.power < 1:
            if not hasattr(cat, "box_fail_checked"):
                cat.box_fail_checked = True
                self.msg_mgr.add("你太餓了，搬不動紙箱...")
            return False
        if not cat.has_box:
            cat.has_box = True
            self.msg_mgr.add("你找到了紙箱並成功築巢！")
            return True
        return False

    def scratch_training(self, cat):
        if not hasattr(cat, "scratch_done"):
            cat.power += 3
            cat.scratch_done = True
            self.msg_mgr.add("你在大樹旁努力磨爪，戰力 +3！")
            return True
        return False

    def granny_feeds_too_much(self, cat):
        if not hasattr(cat, "granny_done"):
            cat.granny_done = True
            cat.power -= 1
            self.msg_mgr.add("阿婆太熱情，你吃太飽肚子痛... 戰力 -1")
            return True
        return False
    
    def draw_health_bar(self,screen, x, y, hp, max_hp, color):
        bar_width = 100
        bar_height = 10
        fill = int((hp / max_hp) * bar_width)
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(screen, color, fill_rect)
        pygame.draw.rect(screen, (0, 0, 0), outline_rect, 2)

    def draw_battle_screen(self):
        self.screen.fill((250, 230, 230))
        self.screen.blit(self.font.render("BOSS 戰！", True, (200, 0, 0)), (WIDTH//2 - 50, 30))
        self.screen.blit(self.font.render(f"你（HP: {self.cat.hp})", True, (0, 0, 0)), (100, 130))
        self.screen.blit(self.font.render(f"Boss（HP: {self.boss.hp})", True, (0, 0, 0)), (500, 130))
        self.screen.blit(self.font.render("Q：可愛攻擊", True, (100, 100, 100)), (100, 200))
        self.screen.blit(self.font.render("W：戰力攻擊", True, (100, 100, 100)), (100, 240))

        if self.cat.hp <= 0:
            self.screen.blit(self.font.render("你輸了 QQ", True, (0, 0, 0)), (WIDTH//2 - 50, HEIGHT//2))
        elif self.boss.hp <= 0:
            self.screen.blit(self.font.render("你贏了！成為地盤主！", True, (0, 100, 0)), (WIDTH//2 - 100, HEIGHT//2))
        if self.msg_mgr:
            self.msg_mgr.draw(self.screen)

    def reset_game(self):
        
        self.rain_active = False
        self.rain_trigger_time = None
        self.start_ticks = pygame.time.get_ticks()

        self.cat.x, self.cat.y = 410, 200  # 回起點
        self.cat.hp = 5
        self.cat.power = 0
        self.cat.cute = 0
        self.cat.has_box = False
        self.cat.max_hp = 5
        self.cat.__dict__.pop("petting_done", None)  # 清除任務 flag（這些任務要自己補上 reset 清除）
        self.cat.__dict__.pop("rain_checked", None)
        
        for mission in self.missions:
            mission.triggered = False
        self.battle_result_shown = False
        self.result_text = ""
        #print("[RESET] rain_active:", self.rain_active, "trigger_time:", self.rain_trigger_time)


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.battle_result_shown:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.battle_result_shown = False
                    self.in_boss_fight = False
                    self.fight_started = False
                    self.reset_game()

            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE and self.boss.rect.colliderect(self.cat.rect):
                    self.in_boss_fight = True
                    self.fight_started = True
                    self.cat.hp = self.cat.power
                    # 進入 boss 對戰的時候
                    self.cat.max_hp = self.cat.power
                    self.cat.hp = self.cat.max_hp
                    self.boss.hp = self.boss.hp

                if self.in_boss_fight:
                    
                    #if event.key == pygame.K_q :
                    if event.key == 113:
                        cat_msg = self.cat.cute_attack(self.boss)
                        self.cat_msg_mgr.add(cat_msg)
                        print(cat_msg)
                        if self.boss.hp > 0:
                            boss_msg = self.boss.attack(self.cat)
                            self.boss_msg_mgr.add(boss_msg)
                            print(boss_msg)
                    if event.key == 119 :
                        cat_msg = self.cat.power_attack(self.boss)
                        self.cat_msg_mgr.add(cat_msg)
                        print(cat_msg)
                        if self.boss.hp > 0:
                            boss_msg = self.boss.attack(self.cat)
                            self.boss_msg_mgr.add(boss_msg)
                            print(boss_msg)
        return True
    def draw_cute_hearts(self):
        for i in range(self.cat.cute):
            x = 20 + i * 35  # 每顆心距離
            y = HEIGHT - 60
            self.screen.blit(self.heart_img, (x, y))

    def exit_battle(self, result):
        #self.in_boss_fight = False
        #self.fight_started = False
        #self.battle_result_shown = True  # 等待玩家按空白鍵繼續

        self.msg_mgr.set_mode("default")
        if result == "win":
            self.msg_mgr.add("你贏了！成為地盤主！按空白鍵繼續...")
        else:
            self.msg_mgr.add("你輸了 QQ，按空白鍵繼續...")
        self.msg_mgr.update()
        self.msg_mgr.draw(self.screen)

    def run(self):
        start_ticks = pygame.time.get_ticks()
        running = True

        while running:
            self.screen.blit(self.bg, (0, 0))
            if self.debug_mask and self.cat.walkable_mask:
                mask_surface = self.cat.walkable_mask.copy()
                mask_surface.set_alpha(100)  # 透明度設為100以便疊圖顯示
                self.screen.blit(mask_surface, (0, 0))


            seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000

            # ✅ 只在從沒下過雨時才開始下
            if seconds >= 20 and not self.rain_active and self.rain_trigger_time is None:
                self.rain_active = True
                self.rain_trigger_time = pygame.time.get_ticks()



            running = self.handle_events()

            if self.in_boss_fight:
                self.cat_msg_mgr.set_mode("battle")
                self.boss_msg_mgr.set_mode("battle")
                self.draw_battle_screen()
                self.draw_cute_hearts()
                # 玩家血條（綠色）
                self.draw_health_bar(self.screen, 100, 100, self.cat.hp, self.cat.max_hp, (0, 200, 0))
                self.draw_health_bar(self.screen, 500, 100, self.boss.hp, self.boss.max_hp, (200, 0, 0))
                self.msg_mgr.update()
                self.msg_mgr.draw(self.screen)
                self.cat_msg_mgr.update()
                self.cat_msg_mgr.draw((self.screen),pos=(70, HEIGHT - 80))
                self.boss_msg_mgr.update()
                self.boss_msg_mgr.draw((self.screen),pos=(WIDTH - 300, HEIGHT - 80))
                if self.cat.hp <= 0:
                    self.exit_battle("lose")
                    self.battle_result_shown = True
                    
                elif self.boss.hp <= 0:
                    self.exit_battle("win")
                    self.battle_result_shown = True
                    

                pygame.display.flip()
                self.clock.tick(60)
                continue

            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_LEFT]: dx = -5
            if keys[pygame.K_RIGHT]: dx = 5
            if keys[pygame.K_UP]: dy = -5
            if keys[pygame.K_DOWN]: dy = 5
            if dx != 0 or dy != 0:
                self.cat.move(dx, dy)
            else:
                self.cat.set_idle()

            self.cat.update()
            self.cat.draw(self.screen)
            self.boss.update()  
            self.boss.draw(self.screen)
            self.msg_mgr.update()
            self.msg_mgr.draw(self.screen,pos=(100, HEIGHT - 50))
            # 在每幀畫面更新中
            

            # 畫面左下角顯示玩家攻擊
            self.cat_msg_mgr.draw(self.screen, pos=(50, HEIGHT - 80))
            # 畫面右下角顯示 Boss 的反擊
            self.boss_msg_mgr.draw(self.screen, pos=(WIDTH - 350, HEIGHT - 80))

            if self.boss.rect.colliderect(self.cat.rect):
                if not self.prompt_mgr.messages:  # 避免每幀都重複加入
                    self.prompt_mgr.set_mode("default")  # 或你想設的模式
                    self.prompt_mgr.add("按下空白鍵挑戰成為地盤主！", duration=2000)
            self.prompt_mgr.update()
            self.prompt_mgr.draw(self.screen, pos=(WIDTH // 2 - 300, HEIGHT // 2 - 100))


            for mission in self.missions:
                mission.check_trigger(self.cat)
                #mission.draw(self.screen)

            self.screen.blit(self.status_box_img, (0, 3))  # 左上角
            text_color = (30, 30, 30)
            self.screen.blit(self.font.render(f"可愛值：{self.cat.cute}", True, text_color), (30, 35))
            self.screen.blit(self.font.render(f"戰力：{self.cat.power}", True, text_color), (30, 60))
            self.screen.blit(self.font.render(f"有紙箱：{'是' if self.cat.has_box else '否'}", True, text_color), (30, 85))

            if self.rain_active and not getattr(self.cat, "rain_checked", False):
                # 1. 螢幕變暗
                dark_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dark_surface.fill((0, 0, 0, 100))  # 半透明黑色
                self.screen.blit(dark_surface, (0, 0))

                # 2. 閃爍文字（每 500 毫秒閃一次）
                now = pygame.time.get_ticks()
                if (now // 500) % 2 == 0:
                    rain_text = self.font.render("下雨了，快找地方躲！", True, (255, 255, 255))
                    self.screen.blit(rain_text, rain_text.get_rect(center=(WIDTH // 2, 30)))


            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


