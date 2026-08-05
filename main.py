import asyncio
import pygame
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario-style Platformer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
dialogue_font = pygame.font.SysFont(None, 32)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

# Physics Constants
GRAVITY = 0.5
MAX_FALL_SPEED = 10
JUMP_STRENGTH = -12
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# Dialogues for each level
level_dialogues = {
    1: ["Spidey: Where is my Gwen?", "Black Widow: I don't know, maybe in the next level."],
    2: [
        "Spidey: Where is my Gwen?",
        "Ghost Rider: Who is Gwen?",
        "Spidey: She is my MJ.",
        "Ghost Rider: I don't know, you can get information in the next level."
    ],
    3: [
        "Spidey: Where is my Gwen?",
        "Wolverine: I don't know, do you know where Deadpool is?",
        "Spidey: I don't know, but why?",
        "Wolverine: I need to kill that guy.",
        "Spidey: Okay, all the best."
    ],
    4: [
        "Spidey: Where is my Gwen?",
        "Thor: I don't know, but you can ask my brother.",
        "Spidey: Who is that, Loki?",
        "Thor: Yeah, maybe he can help you.",
        "Spidey: He killed 40 peoples.",
        "Thor: I mean he is adopted, you can ask him."
    ],
    5: [
        "Spidey: Where is my Gwen?",
        "Loki: Who are you?",
        "Spidey: I am Spidey, your brother said to seek help from you.",
        "Loki: I won't help people I don't know, ask help from that green guy."
    ],
    6: [
        "Spidey: Where is my Gwen?",
        "Hulk: I don't know.",
        "Spidey: Who can I ask?",
        "Hulk: If you waste my time I'll give you my smash.",
        "Spidey: Ok, byee..."
    ],
    7: [
        "Spidey: Where is my Gwen?",
        "Deadpool: I don't know you can ask my friend wolverine.",
        "Spidey: I saw him and he wanted to kill you.",
        "Deadpool: OMG !!! Ok beyyyy.... I need to hide somewhere."
    ],
    8: [
        "Spidey: Dr. Strange, where is my Gwen?",
        "Dr. Strange: Tony Stark knows that.",
        "Spidey: Where is he?",
        "Dr. Strange: He will be in the next level."
    ],
    9: [
        "Spidey: Mr. Stark where is my Gwen?",
        "Iron Man: Peter I tried to bring her here but I can't.",
        "Spidey: So, where is my MJ?",
        "Iron Man: Peter she is in the last stage.",
        "Spidey: How many stages are there?",
        "Iron Man: One last stage, final stage, your MJ is stuck in that stage.",
        "Spidey: Thank you Mr. Stark."
    ],
    10: [
        "Spidey: MJ......!!!!!",
        "Gwen: Spidyyy.....!!!!",
        "Spidey and Gwen: They couldn't bring us together in a movie, but at least they brought us together in a game ❤️. Thanks for that!"
    ]
}

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

    
    # NPC Images
    npc_images = {}
    for i in range(1, 11):
        filename = f"NPC_{i}.png"
        try:
            img = pygame.image.load(filename).convert_alpha()
            img = pygame.transform.scale(img, (40, 40))
            npc_images[i] = img
        except:
            img = pygame.Surface((40, 40))
            img.fill((255, 255, 0))
            npc_images[i] = img
            
    # Restart Icon
    restart_icon_img = pygame.image.load('Restart.png').convert_alpha()
    restart_icon_img = pygame.transform.scale(restart_icon_img, (40, 40))

except Exception as e:
    print(f"Warning: Could not load some images. {e}")
    player_stand_img = pygame.Surface((40, 40))
    player_stand_img.fill((0, 0, 255))
    player_stand_img_left = player_stand_img
    player_run_img = player_stand_img
    player_run_img_left = player_stand_img
    enemy_img = pygame.Surface((40, 40))
    enemy_img.fill((255, 0, 0))
    spike_img = pygame.Surface((40, 40))
    spike_img.fill((128, 128, 128))
        # Background Image
    bg_img = pygame.image.load('bg.jpg').convert()
    bg_width = int(HEIGHT * (16 / 9))
    bg_img = pygame.transform.scale(bg_img, (bg_width, HEIGHT))
    npc_images = {i: pygame.Surface((40, 40)) for i in range(1, 11)}
    for img in npc_images.values(): img.fill((255, 255, 0))
    restart_icon_img = pygame.Surface((40, 40))
    restart_icon_img.fill((255, 0, 0))
    bubble_img = pygame.Surface((WIDTH - 100, 150))
    bubble_img.fill((255, 255, 255))
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.is_grounded = False
        self.facing_right = True
        self.is_running = False

    def update(self, keys, platforms, t_left=False, t_right=False, t_jump=False):
        # --- Horizontal movement ---
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

        # Apply horizontal movement
        self.rect.x += self.vel_x
        
        # Horizontal collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0: # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0: # Moving left
                    self.rect.left = platform.rect.right

        # --- Vertical movement ---
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or t_jump) and self.is_grounded:
            self.vel_y = JUMP_STRENGTH
            self.is_grounded = False

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Apply vertical movement
        self.rect.y += self.vel_y

        self.is_grounded = False
        
        # Vertical collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0: # Falling down
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.is_grounded = True
                elif self.vel_y < 0: # Moving up (hitting ceiling)
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Die if fall out of map
        if self.rect.y > HEIGHT + 100:
            return True # Indicates death
        return False

    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        if self.is_running:
            img = player_run_img if self.facing_right else player_run_img_left
        else:
            img = player_stand_img if self.facing_right else player_stand_img_left
        surface.blit(img, draw_rect)

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        pygame.draw.rect(surface, BROWN, draw_rect)

class Enemy:
    def __init__(self, x, y, walk_distance):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.start_x = x
        self.walk_distance = walk_distance
        self.direction = 1
        
    def update(self):
        self.rect.x += ENEMY_SPEED * self.direction
        if self.rect.x > self.start_x + self.walk_distance:
            self.direction = -1
        elif self.rect.x < self.start_x:
            self.direction = 1
            
    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        surface.blit(enemy_img, draw_rect)

class Spike:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        
    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        surface.blit(spike_img, draw_rect)

class NPC:
    def __init__(self, x, y, img):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.img = img
        
    def draw(self, surface, camera_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        surface.blit(self.img, draw_rect)

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
    player = Player(100, HEIGHT - 100)
    platforms = []
    enemies = []
    spikes = []
    
    # Procedural level generation based on difficulty
    level_width = 1000 + (level_number * 500)
    
    x = 0
    while x < level_width - 400:
        segment_width = max(100, 400 - (level_number * 15))
        gap_width = min(200, 40 + (level_number * 15))
        
        platforms.append(Platform(x, HEIGHT - 40, segment_width, 40))
        
        # Add obstacles
        if level_number >= 2 and x > 200:
            spikes.append(Spike(x + segment_width//2, HEIGHT - 80))
            
        if level_number >= 4 and x > 400:
            platforms.append(Platform(x + segment_width//2 - 50, HEIGHT - 150, 100, 20))
            enemies.append(Enemy(x + segment_width//2 - 40, HEIGHT - 190, 80))
            
        x += segment_width + gap_width
        
    # Final safe platform for NPC
    platforms.append(Platform(level_width - 300, HEIGHT - 40, 500, 40))
    
    # A tall, thick wall at the very end to block the player from passing through
    platforms.append(Platform(level_width, 0, 200, HEIGHT))
    
    # Place NPC at the end
    npc = NPC(level_width - 100, HEIGHT - 80, npc_images[level_number])
    
    return player, platforms, enemies, spikes, npc

async def main():
    global current_level, player, platforms, enemies, spikes, npc, camera_x, game_over, game_won, dialogue_active, dialogue_index, enter_pressed, restart_button_rect, btn_left, btn_right, btn_jump

    # Setup Game
    current_level = 1
    player, platforms, enemies, spikes, npc = load_level(current_level)
    camera_x = 0

    game_over = False
    game_won = False
    dialogue_active = False
    dialogue_index = 0

    # Track key presses to prevent holding ENTER from skipping multiple dialogues
    enter_pressed = False 

    restart_button_rect = pygame.Rect(WIDTH - 50, 10, 40, 40)

    # Touch Controls Rectangles
    btn_left = pygame.Rect(20, HEIGHT - 100, 80, 80)
    btn_right = pygame.Rect(120, HEIGHT - 100, 80, 80)
    btn_jump = pygame.Rect(WIDTH - 120, HEIGHT - 100, 100, 80)

    running = True
    while running:
        # 60 Frames Per Second
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and restart_button_rect.collidepoint(event.pos):
                    player, platforms, enemies, spikes, npc = load_level(current_level)
                    game_over = False
                    dialogue_active = False
                    game_won = False

        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        
        # Touch inputs
        t_left = mouse_pressed and btn_left.collidepoint(mouse_pos)
        t_right = mouse_pressed and btn_right.collidepoint(mouse_pos)
        t_jump = mouse_pressed and btn_jump.collidepoint(mouse_pos)

        # Restart level at any time
        if keys[pygame.K_r]:
            player, platforms, enemies, spikes, npc = load_level(current_level)
            game_over = False
            dialogue_active = False
            game_won = False

        # Handle key press down event for ENTER to advance dialogue
        if (keys[pygame.K_RETURN] or t_jump) and not enter_pressed:
            enter_pressed = True
            
            if dialogue_active:
                dialogue_index += 1
                # If no more dialogue lines, finish the level
                if dialogue_index >= len(level_dialogues.get(current_level, [])):
                    dialogue_active = False
                    if current_level >= 10:
                        game_won = True
                    else:
                        current_level += 1
                        player, platforms, enemies, spikes, npc = load_level(current_level)
            elif game_won:
                current_level = 1
                player, platforms, enemies, spikes, npc = load_level(current_level)
                game_won = False
        elif not keys[pygame.K_RETURN] and not t_jump:
            enter_pressed = False


        if not game_over and not dialogue_active and not game_won:
            # Update logic
            fell_out = player.update(keys, platforms, t_left, t_right, t_jump)
            if fell_out:
                game_over = True
                
            # Update enemies
            for enemy in enemies:
                enemy.update()
                if player.rect.colliderect(enemy.rect):
                    game_over = True
                    
            # Check collision with spikes
            for spike in spikes:
                if player.rect.colliderect(spike.rect):
                    game_over = True

            # Check win condition (trigger dialogue)
            if player.rect.colliderect(npc.rect):
                dialogue_active = True
                dialogue_index = 0

            # Camera follows player
            camera_x = player.rect.x - (WIDTH // 2) + (player.rect.width // 2)
            if camera_x < 0:
                camera_x = 0
                
        else:
            # Handle game over restart
            if game_over and keys[pygame.K_r]:
                player, platforms, enemies, spikes, npc = load_level(current_level)
                game_over = False

        # Draw everything
        try:
            parallax_factor = 0.5
            bg_x = -(camera_x * parallax_factor) % bg_width
            screen.blit(bg_img, (bg_x, 0))
            screen.blit(bg_img, (bg_x - bg_width, 0))
        except NameError:
            screen.fill(SKY_BLUE)
            
        # Level text
        lvl_text = font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(lvl_text, (10, 10))
        
        # Draw Restart Button (Icon)
        screen.blit(restart_icon_img, restart_button_rect.topleft)
        
        for platform in platforms:
            platform.draw(screen, camera_x)
            
        for spike in spikes:
            spike.draw(screen, camera_x)
            
        for enemy in enemies:
            enemy.draw(screen, camera_x)
            
        npc.draw(screen, camera_x)
        player.draw(screen, camera_x)

        # UI Overlays
        if game_over:
            text = font.render("GAME OVER! Press R to Restart", True, RED)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text, text_rect)
        elif dialogue_active:
            # Create a semi-transparent surface for the dialogue box
            box_surface = pygame.Surface((WIDTH - 100, 120))
            box_surface.set_alpha(200) # Transparency
            box_surface.fill(BLACK)
            screen.blit(box_surface, (50, HEIGHT - 150))
            
            # Draw border
            pygame.draw.rect(screen, WHITE, (50, HEIGHT - 150, WIDTH - 100, 120), 3)
            
            lines = level_dialogues.get(current_level, ["..."])
            if dialogue_index < len(lines):
                current_line = lines[dialogue_index]
                text_rect = pygame.Rect(70, HEIGHT - 130, WIDTH - 140, 100)
                draw_text_wrapped(screen, current_line, dialogue_font, WHITE, text_rect)
                
                prompt = dialogue_font.render("Press ENTER to continue...", True, (200, 200, 200))
                prompt_rect = prompt.get_rect()
                prompt_rect.bottomright = (WIDTH - 65, HEIGHT - 45)
                screen.blit(prompt, prompt_rect)
                
        elif game_won:
            text = font.render("YOU SAVED THE GIRL! YOU WIN! Press ENTER to play again", True, GOLD)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text, text_rect)
            
        # Draw Touch Controls
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 100), btn_left, border_radius=10)
        pygame.draw.rect(s, (255, 255, 255, 100), btn_right, border_radius=10)
        pygame.draw.rect(s, (255, 255, 255, 100), btn_jump, border_radius=10)
        # Add text labels
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
