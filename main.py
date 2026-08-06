import asyncio
import pygame
import os

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spidey's Perfect Troll Adventure")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
dialogue_font = pygame.font.SysFont(None, 32)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

# Physics
GRAVITY = 0.5
MAX_FALL_SPEED = 10
JUMP_STRENGTH = -12
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# Dialogues
level_dialogues = {
    1: ["Spidey: Where is my Gwen?", "Black Widow: I don't know, maybe in the next level."],
    2: ["Spidey: Where is my Gwen?", "Ghost Rider: Who is Gwen?", "Spidey: She is my MJ.", "Ghost Rider: I don't know, you can get information in the next level."],
    3: ["Spidey: Where is my Gwen?", "Wolverine: I don't know, do you know where Deadpool is?", "Spidey: I don't know, but why?", "Wolverine: I need to kill that guy.", "Spidey: Okay, all the best."],
    4: ["Spidey: Where is my Gwen?", "Thor: I don't know, but you can ask my brother.", "Spidey: Who is that, Loki?", "Thor: Yeah, maybe he can help you.", "Spidey: He killed 40 peoples.", "Thor: I mean he is adopted, you can ask him."],
    5: ["Spidey: Where is my Gwen?", "Loki: Who are you?", "Spidey: I am Spidey, your brother said to seek help from you.", "Loki: I won't help people I don't know, ask help from that green guy."],
    6: ["Spidey: Where is my Gwen?", "Hulk: I don't know.", "Spidey: Who can I ask?", "Hulk: If you waste my time I'll give you my smash.", "Spidey: Ok, byee..."],
    7: ["Spidey: Where is my Gwen?", "Deadpool: I don't know you can ask my friend wolverine.", "Spidey: I saw him and he wanted to kill you.", "Deadpool: OMG !!! Ok beyyyy.... I need to hide somewhere."],
    8: ["Spidey: Dr. Strange, where is my Gwen?", "Dr. Strange: Tony Stark knows that.", "Spidey: Where is he?", "Dr. Strange: He will be in the next level."],
    9: ["Spidey: Mr. Stark where is my Gwen?", "Iron Man: Peter I tried to bring her here but I can't.", "Spidey: So, where is my MJ?", "Iron Man: Peter she is in the last stage.", "Spidey: How many stages are there?", "Iron Man: One last stage, final stage, your MJ is stuck in that stage.", "Spidey: Thank you Mr. Stark."],
    10: ["Spidey: MJ......!!!!!", "Gwen: Spidyyy.....!!!!", "Spidey and Gwen: They couldn't bring us together in a movie, but at least they brought us together in a game ❤️. Thanks for that!"]
}

# UI
restart_button_rect = pygame.Rect(WIDTH - 50, 10, 40, 40)
btn_left = pygame.Rect(20, HEIGHT - 100, 80, 80)
btn_right = pygame.Rect(120, HEIGHT - 100, 80, 80)
btn_jump = pygame.Rect(WIDTH - 120, HEIGHT - 100, 100, 80)

# Load Assets
try:
    player_stand_img = pygame.image.load('standing.png').convert_alpha()
    player_stand_img = pygame.transform.scale(player_stand_img, (40, 40))
    player_stand_img_left = pygame.transform.flip(player_stand_img, True, False)
    
    player_run_img = pygame.image.load('running.png').convert_alpha()
    player_run_img = pygame.transform.scale(player_run_img, (40, 40))
    player_run_img_left = pygame.transform.flip(player_run_img, True, False)
    
    enemy_img = pygame.image.load('enemy.png').convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (40, 40))
    
    spike_img = pygame.image.load('struggle.png').convert_alpha()
    spike_img = pygame.transform.scale(spike_img, (40, 40))

    bg_img_base = pygame.image.load('city.jpg').convert()
    bg_img_base = pygame.transform.scale(bg_img_base, (WIDTH, HEIGHT))

    npc_images = {}
    for i in range(1, 11):
        filename = f"NPC_{i}.png"
        try:
            img = pygame.image.load(filename).convert_alpha()
            img = pygame.transform.scale(img, (40, 40))
            npc_images[i] = img
        except:
            img = pygame.Surface((40, 40)); img.fill((255, 255, 0))
            npc_images[i] = img
            
    restart_icon_img = pygame.image.load('Restart.png').convert_alpha()
    restart_icon_img = pygame.transform.scale(restart_icon_img, (40, 40))

except Exception as e:
    print(f"Warning: Could not load some images. {e}")
    player_stand_img = pygame.Surface((40, 40)); player_stand_img.fill((0, 0, 255))
    player_stand_img_left = player_stand_img
    player_run_img = player_stand_img; player_run_img_left = player_stand_img
    enemy_img = pygame.Surface((40, 40)); enemy_img.fill((255, 0, 0))
    spike_img = pygame.Surface((40, 40)); spike_img.fill((128, 128, 128))
    bg_img_base = pygame.Surface((WIDTH, HEIGHT)); bg_img_base.fill(SKY_BLUE)
    npc_images = {i: pygame.Surface((40, 40)) for i in range(1, 11)}
    for img in npc_images.values(): img.fill((255, 255, 0))
    restart_icon_img = pygame.Surface((40, 40)); restart_icon_img.fill((255, 0, 0))

def get_level_tint(level):
    if level <= 3: return (255, 255, 255)
    elif level <= 6: return (255, 180, 100)
    elif level <= 9: return (100, 100, 150)
    else: return (255, 100, 100)

def get_platform_color(level):
    if level <= 3: return (139, 69, 19)
    elif level <= 6: return (160, 82, 45)
    elif level <= 9: return (47, 79, 79)
    else: return (105, 105, 105)

def create_tinted_bg(level):
    tint = get_level_tint(level)
    if tint == (255, 255, 255): return bg_img_base
    tinted = bg_img_base.copy()
    tint_surf = pygame.Surface(tinted.get_size())
    tint_surf.fill(tint)
    tinted.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_MULT)
    return tinted

# =======================
# THE LEVEL DEVIL TRAPS
# =======================

class Platform:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.active = True

    def update(self, player):
        pass

    def draw(self, surface, camera_x):
        if self.active:
            draw_rect = self.rect.copy()
            draw_rect.x -= camera_x
            pygame.draw.rect(surface, self.color, draw_rect)

class TrollPlatform(Platform):
    def update(self, player):
        if self.active and self.rect.colliderect(player.rect):
            self.active = False
            self.rect.y = 9999 

class InvisiblePlatform(Platform):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
        self.visible = False

    def update(self, player):
        if abs(player.rect.centerx - self.rect.centerx) < 150:
            self.visible = True

    def draw(self, surface, camera_x):
        if self.visible and self.active:
            super().draw(surface, camera_x)

class Spike:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.active = True
        
    def update(self, player):
        pass
        
    def draw(self, surface, camera_x):
        if self.active:
            draw_rect = self.rect.copy()
            draw_rect.x -= camera_x
            surface.blit(spike_img, draw_rect)

class FallingSpike(Spike):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.triggered = False
        self.vel_y = 0

    def update(self, player):
        if not self.triggered and abs(player.rect.centerx - self.rect.centerx) < 70 and player.rect.y > self.rect.y:
            self.triggered = True
        
        if self.triggered:
            self.vel_y += GRAVITY * 2
            self.rect.y += self.vel_y

class InvisibleSpike(Spike):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.visible = False

    def update(self, player):
        if abs(player.rect.centerx - self.rect.centerx) < 80:
            self.visible = True

    def draw(self, surface, camera_x):
        if self.visible and self.active:
            super().draw(surface, camera_x)

class NPC:
    def __init__(self, x, y, img, is_troll=False, stop_x=None):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.img = img
        self.is_troll = is_troll
        self.stop_x = stop_x
        
    def update(self, player):
        if self.is_troll:
            if abs(player.rect.x - self.rect.x) < 250:
                if self.stop_x is None or self.rect.x < self.stop_x:
                    self.rect.x += PLAYER_SPEED + 1 
                
    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        surface.blit(self.img, draw_rect)

# =======================
# PLAYER & ENEMIES
# =======================

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.is_grounded = False
        self.facing_right = True
        self.is_running = False

    def update(self, keys, platforms, t_left=False, t_right=False, t_jump=False):
        self.vel_x = 0
        self.is_running = False
        if keys[pygame.K_LEFT] or t_left:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
            self.is_running = True
        if keys[pygame.K_RIGHT] or t_right:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
            self.is_running = True

        self.rect.x += self.vel_x
        
        for platform in platforms:
            if platform.active and self.rect.colliderect(platform.rect):
                if self.vel_x > 0: self.rect.right = platform.rect.left
                elif self.vel_x < 0: self.rect.left = platform.rect.right

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or t_jump) and self.is_grounded:
            self.vel_y = JUMP_STRENGTH
            self.is_grounded = False

        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.rect.y += self.vel_y
        self.is_grounded = False
        
        for platform in platforms:
            if platform.active and self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.is_grounded = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        if self.rect.y > HEIGHT + 100: return True
        return False

    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        if self.is_running: img = player_run_img if self.facing_right else player_run_img_left
        else: img = player_stand_img if self.facing_right else player_stand_img_left
        surface.blit(img, draw_rect)

class Enemy:
    def __init__(self, x, y, walk_distance, speed=ENEMY_SPEED):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.start_x = x
        self.walk_distance = walk_distance
        self.direction = 1
        self.speed = speed
        
    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x > self.start_x + self.walk_distance: self.direction = -1
        elif self.rect.x < self.start_x: self.direction = 1
            
    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        surface.blit(enemy_img, draw_rect)

def draw_text_wrapped(surface, text, font, color, rect):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        fw, fh = font.size(' '.join(current_line))
        if fw > rect.width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    y = rect.top
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (rect.left, y))
        y += font.get_height() + 5

def load_level(level_number):
    player = Player(50, HEIGHT - 100)
    platforms, enemies, spikes = [], [], []
    
    platform_color = get_platform_color(level_number)
    level_width = 2000 + (level_number * 100)

    if level_number == 1:
        platforms.append(Platform(0, HEIGHT - 40, 300, 40, platform_color))
        spikes.append(FallingSpike(200, 100))
        platforms.append(TrollPlatform(300, HEIGHT - 40, 100, 40, platform_color)) 
        platforms.append(Platform(400, HEIGHT - 40, 300, 40, platform_color))
        spikes.append(InvisibleSpike(600, HEIGHT - 80))
        platforms.append(Platform(800, HEIGHT - 40, 2000, 40, platform_color))
        
    elif level_number == 2:
        platforms.append(Platform(0, HEIGHT - 40, 250, 40, platform_color))
        platforms.append(TrollPlatform(250, HEIGHT - 40, 100, 40, platform_color))
        platforms.append(InvisiblePlatform(350, HEIGHT - 100, 100, 20, platform_color))
        platforms.append(Platform(550, HEIGHT - 40, 2000, 40, platform_color))
        
    elif level_number == 3:
        platforms.append(Platform(0, HEIGHT - 40, 400, 40, platform_color))
        enemies.append(Enemy(200, HEIGHT - 80, 100, ENEMY_SPEED * 2))
        platforms.append(Platform(500, HEIGHT - 100, 100, 20, platform_color))
        platforms.append(TrollPlatform(650, HEIGHT - 100, 100, 20, platform_color)) 
        platforms.append(Platform(750, HEIGHT - 40, 2000, 40, platform_color))
        spikes.append(FallingSpike(900, 100))
        
    elif level_number == 4:
        platforms.append(Platform(0, HEIGHT - 40, 600, 40, platform_color))
        platforms.append(TrollPlatform(600, HEIGHT - 40, 100, 40, platform_color))
        platforms.append(Platform(750, HEIGHT - 40, 2000, 40, platform_color))
        spikes.append(InvisibleSpike(500, HEIGHT - 80))
        spikes.append(FallingSpike(800, 100))
        
    elif level_number == 5:
        platforms.append(Platform(0, HEIGHT - 40, 200, 40, platform_color))
        platforms.append(InvisiblePlatform(300, HEIGHT - 100, 100, 20, platform_color))
        spikes.append(FallingSpike(350, 0)) 
        platforms.append(InvisiblePlatform(550, HEIGHT - 160, 100, 20, platform_color))
        platforms.append(TrollPlatform(750, HEIGHT - 160, 100, 20, platform_color))
        platforms.append(Platform(850, HEIGHT - 40, 2000, 40, platform_color))
        
    elif level_number == 6:
        platforms.append(Platform(0, HEIGHT - 40, 3000, 40, platform_color))
        enemies.append(Enemy(400, HEIGHT - 80, 100, ENEMY_SPEED * 2))
        spikes.append(FallingSpike(600, 100))
        enemies.append(Enemy(900, HEIGHT - 80, 100, ENEMY_SPEED * 2))
        spikes.append(InvisibleSpike(1100, HEIGHT - 80))
        
    # === NEW HARDER LEVELS 7, 8, 9 ===
    
    elif level_number == 7:
        platforms.append(Platform(0, HEIGHT - 40, 300, 40, platform_color))
        platforms.append(TrollPlatform(300, HEIGHT - 40, 100, 40, platform_color)) 
        platforms.append(Platform(450, HEIGHT - 40, 200, 40, platform_color))
        spikes.append(FallingSpike(550, 100))
        platforms.append(TrollPlatform(650, HEIGHT - 40, 100, 40, platform_color))
        platforms.append(Platform(800, HEIGHT - 40, 2000, 40, platform_color))
        spikes.append(InvisibleSpike(950, HEIGHT - 80))
        
    elif level_number == 8:
        platforms.append(Platform(0, HEIGHT - 40, 200, 40, platform_color))
        platforms.append(InvisiblePlatform(350, HEIGHT - 100, 100, 20, platform_color))
        spikes.append(FallingSpike(400, 50)) 
        platforms.append(InvisiblePlatform(600, HEIGHT - 150, 100, 20, platform_color))
        platforms.append(TrollPlatform(800, HEIGHT - 150, 100, 20, platform_color)) 
        platforms.append(Platform(900, HEIGHT - 40, 2000, 40, platform_color))
        spikes.append(InvisibleSpike(1100, HEIGHT - 80))
        enemies.append(Enemy(1300, HEIGHT - 80, 200, ENEMY_SPEED * 3))
        
    elif level_number == 9:
        platforms.append(Platform(0, HEIGHT - 40, 300, 40, platform_color))
        spikes.append(InvisibleSpike(150, HEIGHT - 80))
        platforms.append(TrollPlatform(300, HEIGHT - 40, 100, 40, platform_color))
        platforms.append(Platform(450, HEIGHT - 40, 200, 40, platform_color))
        spikes.append(FallingSpike(550, 100))
        spikes.append(FallingSpike(650, 100))
        platforms.append(TrollPlatform(750, HEIGHT - 40, 100, 40, platform_color))
        platforms.append(Platform(900, HEIGHT - 40, 2000, 40, platform_color))
        spikes.append(InvisibleSpike(1000, HEIGHT - 80))
        enemies.append(Enemy(1200, HEIGHT - 80, 200, ENEMY_SPEED * 4))
        
    else:
        platforms.append(Platform(0, HEIGHT - 40, 3000, 40, platform_color))
        enemies.append(Enemy(300, HEIGHT - 80, 100, ENEMY_SPEED * 4))
        spikes.append(InvisibleSpike(500, HEIGHT - 80))
        spikes.append(FallingSpike(900, 100))
        enemies.append(Enemy(1200, HEIGHT - 80, 200, ENEMY_SPEED * 4))

    # NPC placement and Wall logic
    end_wall_x = level_width - 200
    
    if level_number == 4:
        npc = NPC(300, HEIGHT - 80, npc_images[level_number], is_troll=True, stop_x=end_wall_x - 50)
    else:
        npc = NPC(level_width - 300, HEIGHT - 80, npc_images.get(level_number, npc_images[1]))
    
    platforms.append(Platform(end_wall_x, 0, 200, HEIGHT, platform_color))
    
    current_bg_img = create_tinted_bg(level_number)
    return player, platforms, enemies, spikes, npc, current_bg_img

async def main():
    global current_level, player, platforms, enemies, spikes, npc, camera_x, game_over, game_won, dialogue_active, dialogue_index, enter_pressed

    current_level = 1
    player, platforms, enemies, spikes, npc, current_bg_img = load_level(current_level)
    camera_x = 0

    game_over = False
    game_won = False
    dialogue_active = False
    dialogue_index = 0
    enter_pressed = False 
    active_touches = {} 

    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and restart_button_rect.collidepoint(event.pos):
                    player, platforms, enemies, spikes, npc, current_bg_img = load_level(current_level)
                    game_over = False; dialogue_active = False; game_won = False
            elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                tx, ty = event.x * WIDTH, event.y * HEIGHT
                active_touches[event.finger_id] = (tx, ty)
            elif event.type == pygame.FINGERUP:
                if event.finger_id in active_touches:
                    del active_touches[event.finger_id]

        keys = pygame.key.get_pressed()
        t_left, t_right, t_jump = False, False, False
        for tx, ty in active_touches.values():
            if btn_left.collidepoint((tx, ty)): t_left = True
            if btn_right.collidepoint((tx, ty)): t_right = True
            if btn_jump.collidepoint((tx, ty)): t_jump = True

        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed:
            mouse_pos = pygame.mouse.get_pos()
            if btn_left.collidepoint(mouse_pos): t_left = True
            if btn_right.collidepoint(mouse_pos): t_right = True
            if btn_jump.collidepoint(mouse_pos): t_jump = True

        if keys[pygame.K_r]:
            player, platforms, enemies, spikes, npc, current_bg_img = load_level(current_level)
            game_over = False; dialogue_active = False; game_won = False

        if (keys[pygame.K_RETURN] or t_jump) and not enter_pressed:
            enter_pressed = True
            if dialogue_active:
                dialogue_index += 1
                if dialogue_index >= len(level_dialogues.get(current_level, [])):
                    dialogue_active = False
                    if current_level >= 10: game_won = True
                    else:
                        current_level += 1
                        player, platforms, enemies, spikes, npc, current_bg_img = load_level(current_level)
            elif game_won:
                current_level = 1
                player, platforms, enemies, spikes, npc, current_bg_img = load_level(current_level)
                game_won = False
        elif not keys[pygame.K_RETURN] and not t_jump:
            enter_pressed = False

        if not game_over and not dialogue_active and not game_won:
            fell_out = player.update(keys, platforms, t_left, t_right, t_jump)
            if fell_out: game_over = True
                
            for platform in platforms:
                platform.update(player)
                
            for spike in spikes:
                spike.update(player)
                if spike.active and player.rect.colliderect(spike.rect):
                    game_over = True
                    
            for enemy in enemies:
                enemy.update()
                if player.rect.colliderect(enemy.rect):
                    game_over = True

            npc.update(player)
            if player.rect.colliderect(npc.rect):
                dialogue_active = True
                dialogue_index = 0

            camera_x = player.rect.x - (WIDTH // 2) + (player.rect.width // 2)
            if camera_x < 0: camera_x = 0
                
        else:
            if game_over and (keys[pygame.K_r] or t_jump):
                player, platforms, enemies, spikes, npc, current_bg_img = load_level(current_level)
                game_over = False

        parallax_factor = 0.5
        bg_x = -(camera_x * parallax_factor) % WIDTH
        screen.blit(current_bg_img, (bg_x, 0))
        screen.blit(current_bg_img, (bg_x - WIDTH, 0))
            
        lvl_text = font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(lvl_text, (10, 10))
        screen.blit(restart_icon_img, restart_button_rect.topleft)
        
        for platform in platforms: platform.draw(screen, camera_x)
        for spike in spikes: spike.draw(screen, camera_x)
        for enemy in enemies: enemy.draw(screen, camera_x)
        npc.draw(screen, camera_x)
        player.draw(screen, camera_x)

        if game_over:
            text = font.render("GAME OVER! Press Jump to Restart", True, RED)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text, text_rect)
        elif dialogue_active:
            box_w = WIDTH - 200
            box_x = (WIDTH - box_w) // 2
            box_surface = pygame.Surface((box_w, 120))
            box_surface.set_alpha(200); box_surface.fill(BLACK)
            screen.blit(box_surface, (box_x, HEIGHT - 150))
            pygame.draw.rect(screen, WHITE, (box_x, HEIGHT - 150, box_w, 120), 3)
            
            lines = level_dialogues.get(current_level, ["..."])
            if dialogue_index < len(lines):
                current_line = lines[dialogue_index]
                text_rect = pygame.Rect(box_x + 20, HEIGHT - 130, box_w - 40, 100)
                draw_text_wrapped(screen, current_line, dialogue_font, WHITE, text_rect)
                prompt = dialogue_font.render("Press JUMP to continue...", True, (200, 200, 200))
                prompt_rect = prompt.get_rect(); prompt_rect.bottomright = (box_x + box_w - 15, HEIGHT - 45)
                screen.blit(prompt, prompt_rect)
                
        elif game_won:
            text = font.render("YOU SAVED THE GIRL! YOU WIN!", True, GOLD)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text, text_rect)
            
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 120), btn_left, border_radius=10)
        pygame.draw.rect(s, (255, 255, 255, 120), btn_right, border_radius=10)
        pygame.draw.rect(s, (255, 255, 255, 120), btn_jump, border_radius=10)
        left_text = font.render("<", True, BLACK)
        s.blit(left_text, left_text.get_rect(center=btn_left.center))
        right_text = font.render(">", True, BLACK)
        s.blit(right_text, right_text.get_rect(center=btn_right.center))
        jump_text = dialogue_font.render("JUMP", True, BLACK)
        s.blit(jump_text, jump_text.get_rect(center=btn_jump.center))
        screen.blit(s, (0, 0))

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
