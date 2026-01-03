import pygame
import sys
import random
import math
from enum import Enum

pygame.init()
pygame.mixer.init() 
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GRAVITY = 0.8 
JUMP_FORCE = -16
MAX_SCROLL_X = 9000  # Extended level width
TRANSFORM_TIME = 60  # 1 second transformation

SKY_BLUE = (135, 206, 235)
DAY_SKY = (100, 180, 255)
NIGHT_SKY = (20, 30, 60)
GROUND_GREEN = (76, 175, 80)
PLATFORM_BROWN = (139, 69, 19)
PLAYER_BLUE = (30, 144, 255)
PLAYER_RED = (220, 20, 60)
ENEMY_RED = (200, 0, 0)
ENEMY_YELLOW = (255, 215, 0)
ENEMY_GREEN = (0, 180, 0)
ENEMY_PURPLE = (180, 0, 200)
ENEMY_BROWN = (139, 69, 19)
BOSS_PURPLE = (138, 43, 226)
POWERUP_BLUE = (0, 191, 255)
POWERUP_GREEN = (50, 205, 50)
UI_YELLOW = (255, 255, 0)
UI_ORANGE = (255, 140, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WEB_COLOR = (200, 200, 220, 180)
STICKY_COLOR = (100, 80, 50, 200)

class GameState(Enum):
    MENU = 0
    LEVEL_SELECT = 1
    PLAYING = 2
    GAME_OVER = 3
class GameState:
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4
    INSTRUCTIONS = 5
    TRANSFORMING = 6
    LEVEL_SELECT = 7 

# ================= BASE GAME OBJECT =================
class GameObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

# ================= PARTICLE SYSTEM =================
class Particle:
    def __init__(self, x, y, color, velocity=None, lifespan=60, size=None, particle_type="default"):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity or [random.uniform(-2, 2), random.uniform(-5, -2)]
        self.lifespan = lifespan
        self.size = size or random.randint(2, 6)
        self.age = 0
        self.particle_type = particle_type
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-0.2, 0.2)
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity[1] += 0.1  # Gravity
        
        # Add some air resistance
        self.velocity[0] *= 0.98
        self.velocity[1] *= 0.99
        
        self.age += 1
        self.rotation += self.rotation_speed
        
        # Different decay based on particle type
        if self.particle_type == "sparkle":
            self.size = max(0, self.size - 0.02)
        else:
            self.size = max(0, self.size - 0.05)
        
        return self.age < self.lifespan
    
    def draw(self, screen, scroll_x):
        alpha = 255 * (1 - self.age / self.lifespan)
        
        if self.particle_type == "sparkle":
            # Sparkle particles are brighter and star-shaped
            surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            
            # Draw a star shape
            points = []
            for i in range(5):
                angle = self.rotation + i * math.pi * 2 / 5
                outer_x = math.cos(angle) * self.size * 2
                outer_y = math.sin(angle) * self.size * 2
                points.append((self.size * 2 + outer_x, self.size * 2 + outer_y))
                
                inner_angle = angle + math.pi / 5
                inner_x = math.cos(inner_angle) * self.size
                inner_y = math.sin(inner_angle) * self.size
                points.append((self.size * 2 + inner_x, self.size * 2 + inner_y))
            
            if len(points) >= 3:
                pygame.draw.polygon(surf, (*self.color, int(alpha)), points)
        else:
            # Regular circular particles
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(alpha)), 
                             (self.size, self.size), self.size)
        
        screen.blit(surf, (self.x - scroll_x - self.size * 2, self.y - self.size * 2))

# ================= ENHANCED ASSET MANAGEMENT =================
class Assets:
    @staticmethod
    def create_enemy_bee():
        # The "Phantom Wasp" - Torn wings and glowing soul core
        frames = []
        for i in range(8):
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            # Erratic vibration: twitching every few frames
            twitch = random.randint(-2, 2) if i % 2 == 0 else 0
            
            # 1. Spectral Torn Wings
            for side in [-1, 1]:
                wing_flap = math.sin(i * math.pi / 2) * 25
                points = [
                    (30, 25), 
                    (30 + 35*side, 10 + wing_flap), 
                    (30 + 20*side, 30 + twitch), 
                    (30 + 40*side, 40)
                ]
                # Ghostly Cyan with transparency
                pygame.draw.polygon(surf, (0, 255, 200, 100), points)
                pygame.draw.lines(surf, (150, 255, 255, 200), False, points, 2)

            # 2. Corrupted Body (Black & Purple)
            # Abdomen with glowing "soul segments"
            for j in range(4):
                col = (30, 0, 50) if j % 2 == 0 else (100, 0, 200)
                pygame.draw.ellipse(surf, col, (20, 20 + j*6, 20, 10))
                # Glowing core light
                if j == 2:
                    pygame.draw.circle(surf, (200, 255, 255), (30, 25 + j*6), 4)

            # 3. Head - Menacing glowing eyes
            pygame.draw.circle(surf, (10, 10, 10), (30, 15), 10)
            eye_glow = int(150 + math.sin(i) * 105) # Pulsing eyes
            pygame.draw.circle(surf, (255, 0, 50, eye_glow), (26, 12), 4)
            pygame.draw.circle(surf, (255, 0, 50, eye_glow), (34, 12), 4)
            
            frames.append(surf)
        return frames

    @staticmethod
    def create_enemy_beetle():
        # The "Void Crusher" - Obsidian shell with glowing cracks
        frames = []
        for i in range(8):
            surf = pygame.Surface((80, 60), pygame.SRCALPHA)
            move = math.sin(i * math.pi / 4) * 10
            
            # 1. Jagged Mechanical Legs
            for side in [-1, 1]:
                for j in range(3):
                    # Each leg moves at a slightly different "jerky" rate
                    leg_twitch = math.sin(i + j) * 8
                    start = (40 + 10*side, 30 + j*5)
                    knee = (40 + 30*side + leg_twitch, 20 + j*10)
                    foot = (40 + 25*side + leg_twitch, 50)
                    pygame.draw.lines(surf, (30, 30, 40), False, [start, knee, foot], 4)
                    # Joints
                    pygame.draw.circle(surf, (100, 255, 100), knee, 3)

            # 2. Obsidian Shell with "Soul Cracks"
            pygame.draw.ellipse(surf, (5, 5, 10), (15, 15, 50, 40)) # Base
            # Glowing Cracks (Green energy leaking out)
            for _ in range(3):
                cx, cy = random.randint(20, 50), random.randint(20, 40)
                pygame.draw.line(surf, (0, 255, 50, 150), (cx, cy), (cx+10, cy+5), 2)

            # 3. Giant Pincer/Horn - Twitching
            pygame.draw.polygon(surf, (20, 20, 30), [(55, 30), (75 + move, 15), (70, 30), (75 + move, 45)])
            pygame.draw.line(surf, (0, 255, 100), (60, 30), (70, 30), 3) # Glowing edge
            
            frames.append(surf)
        return frames


    @staticmethod
    def create_enemy_scorpion():
        frames = []
        for i in range(12):
            surf = pygame.Surface((110, 90), pygame.SRCALPHA)
            time_factor = i * (math.pi / 6)

            body_breathe = math.sin(time_factor * 0.5) * 2

            # 1. THE LEGS (Sharper, Jointed, Predatory)
            for leg_pair in range(4):
                phase = time_factor + (leg_pair * 0.6)
                lift = max(0, math.sin(phase) * 14)
                reach = math.cos(phase) * 12

                for side in [-1, 1]:
                    root_x = 48 + (leg_pair * 6)
                    root_y = 58 + body_breathe

                    knee_x = root_x + (22 * side) + (reach * 0.6)
                    knee_y = root_y - 18 - (lift * 0.7)

                    foot_x = knee_x + (14 * side) + reach
                    foot_y = root_y + 12 - lift

                    pygame.draw.line(surf, (10, 10, 15), (root_x, root_y), (knee_x, knee_y), 6)
                    pygame.draw.line(surf, (20, 20, 30), (knee_x, knee_y), (foot_x, foot_y), 4)

                    pygame.draw.circle(surf, (80, 0, 120), (int(knee_x), int(knee_y)), 4)
                    pygame.draw.circle(surf, (120, 0, 180), (int(foot_x), int(foot_y)), 3)

            # 2. THE TAIL (Whip Motion + Venom Pulse)
            segments = 11
            prev_x, prev_y = 32, 50 + body_breathe
            for s in range(segments):
                sway_offset = math.sin(time_factor * 0.9 - (s * 0.35)) * (s * 5)
                curl = math.cos(time_factor * 0.7 - s * 0.4) * 4

                curr_x = 32 - (s * 5) + sway_offset
                curr_y = 50 - (s * 7) + curl

                radius = max(3, 13 - s)
                color_val = max(15, 70 - s * 6)

                pygame.draw.circle(
                    surf,
                    (color_val, 0, color_val + 25),
                    (int(curr_x), int(curr_y)),
                    radius
                )

                pygame.draw.circle(
                    surf,
                    (120, 80, 180),
                    (int(curr_x - 2), int(curr_y - 3)),
                    radius // 2
                )

                if s == segments - 1:
                    glow_size = 9 + math.sin(time_factor * 3) * 3
                    pygame.draw.circle(
                        surf,
                        (0, 255, 200, 120),
                        (int(curr_x), int(curr_y)),
                        glow_size
                    )
                    pygame.draw.circle(
                        surf,
                        (255, 255, 255),
                        (int(curr_x), int(curr_y)),
                        4
                    )
                    pygame.draw.line(
                        surf,
                        (220, 220, 220),
                        (curr_x, curr_y),
                        (curr_x + 18, curr_y - 12),
                        2
                    )

            # 3. THE PINCERS (Heavier, Crushing)
            snap = math.sin(time_factor * 2.2) * 7
            for side in [-1, 1]:
                p_root = (58, 52 + 10 * side + body_breathe)
                p_joint = (80, 48 + 26 * side + snap)

                pygame.draw.line(surf, (15, 15, 20), p_root, p_joint, 8)
                pygame.draw.circle(surf, (20, 20, 30), p_joint, 10)

                pygame.draw.line(
                    surf,
                    (0, 255, 180),
                    p_joint,
                    (p_joint[0] + 20, p_joint[1] - 6 - snap),
                    3
                )
                pygame.draw.line(
                    surf,
                    (0, 255, 180),
                    p_joint,
                    (p_joint[0] + 20, p_joint[1] + 6 + snap),
                    3
                )

            # 4. THE BODY (Layered Chitin + Breathing)
            pygame.draw.ellipse(
                surf,
                (10, 10, 15),
                (25, 40 + body_breathe, 48, 32)
            )

            for p in range(4):
                pygame.draw.ellipse(
                    surf,
                    (35, 35, 55),
                    (30 + p * 9, 46 + body_breathe, 16, 22)
                )

            # 5. EYES (Clustered, Uneven, Watching)
            for e in range(4):
                pygame.draw.circle(
                    surf,
                    (255, 0, 60),
                    (66 + e * 3, 50 + (e % 2) * 4),
                    2
                )
                pygame.draw.circle(
                    surf,
                    (255, 100, 120),
                    (66 + e * 3, 50 + (e % 2) * 4),
                    1
                )

            frames.append(surf)
        return frames

    @staticmethod
    def create_player_frames():
        """Creates a SIDE-VIEW Robot profile"""
        frames = []
        for i in range(8):
            surf = pygame.Surface((60, 90), pygame.SRCALPHA)
            
            # Animation offsets for walking
            leg_swing = math.sin(i * math.pi / 4) * 15
            arm_swing = math.cos(i * math.pi / 4) * 12
            
            # 1. Back Leg
            pygame.draw.rect(surf, (15, 30, 60), (30 - leg_swing//2, 60, 12, 30), border_radius=4)
            
            # 2. Back Arm
            pygame.draw.rect(surf, (20, 80, 180), (35 + arm_swing, 35, 10, 25), border_radius=4)
            
            # 3. Torso (Side view is thinner than front view)
            pygame.draw.rect(surf, (30, 60, 120), (20, 25, 25, 40), border_radius=5)
            # Power Core on back/side
            pygame.draw.rect(surf, (0, 255, 255), (15, 30, 6, 20), border_radius=2)
            
            # 4. Head (Facing right)
            pygame.draw.rect(surf, (40, 40, 60), (25, 5, 25, 22), border_radius=6)
            # Visor (Front facing side)
            pygame.draw.rect(surf, (0, 230, 255), (42, 10, 8, 8), border_radius=2)
            
            # 5. Front Leg
            pygame.draw.rect(surf, (30, 144, 255), (25 + leg_swing//2, 60, 14, 30), border_radius=4)
            
            # 6. Front Arm
            pygame.draw.rect(surf, PLAYER_BLUE, (20 - arm_swing, 35, 12, 30), border_radius=4)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_vehicle_frames():
        frames = []
        for i in range(8):
            surf = pygame.Surface((100, 50), pygame.SRCALPHA)
            
            # Sleek futuristic vehicle
            # Main body
            body_points = [(10, 25), (20, 10), (80, 10), (90, 25), (80, 40), (20, 40)]
            pygame.draw.polygon(surf, (200, 20, 40), body_points)
            
            # Metallic highlights
            highlight_points = [(15, 28), (25, 15), (75, 15), (85, 28)]
            pygame.draw.lines(surf, (255, 100, 100), False, highlight_points, 3)
            
            # Cockpit/Windows
            pygame.draw.ellipse(surf, (100, 200, 255, 200), (40, 12, 20, 15))
            
            # Animated wheels with rotation effect
            wheel_angle = i * 45
            # Front wheel
            wheel_front = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(wheel_front, (30, 30, 30), (12, 12), 12)
            pygame.draw.circle(wheel_front, (60, 60, 60), (12, 12), 8)
            # Wheel spokes
            rotated_front = pygame.transform.rotate(wheel_front, wheel_angle)
            surf.blit(rotated_front, (25, 33))
            
            # Back wheel
            wheel_back = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(wheel_back, (30, 30, 30), (12, 12), 12)
            pygame.draw.circle(wheel_back, (60, 60, 60), (12, 12), 8)
            rotated_back = pygame.transform.rotate(wheel_back, wheel_angle)
            surf.blit(rotated_back, (65, 33))
            
            # Glowing engine exhaust
            exhaust_glow = pygame.Surface((15, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(exhaust_glow, (255, 200, 0, 150), (0, 5, 15, 10))
            surf.blit(exhaust_glow, (85, 25))
            
            # Headlights
            pygame.draw.circle(surf, (255, 255, 200), (15, 20), 6)
            pygame.draw.circle(surf, (255, 255, 200), (15, 30), 6)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_enemy_snail():
        surf = pygame.Surface((50, 40), pygame.SRCALPHA)
        # Detailed shell with spiral pattern
        pygame.draw.ellipse(surf, (180, 60, 60), (15, 5, 30, 30))
        pygame.draw.ellipse(surf, (220, 100, 100), (20, 10, 20, 20))
        
        # Spiral pattern on shell
        for j in range(3):
            angle = j * 120
            x = 30 + math.cos(math.radians(angle)) * 8
            y = 20 + math.sin(math.radians(angle)) * 8
            pygame.draw.circle(surf, (160, 40, 40), (int(x), int(y)), 4)
        
        # Body with texture
        body_points = [(5, 25), (15, 20), (35, 20), (45, 25), (35, 35), (15, 35)]
        pygame.draw.polygon(surf, (160, 100, 100), body_points)
        
        # Eyes on stalks
        pygame.draw.line(surf, (160, 100, 100), (10, 20), (8, 10), 3)
        pygame.draw.line(surf, (160, 100, 100), (15, 20), (17, 8), 3)
        pygame.draw.circle(surf, WHITE, (8, 10), 4)
        pygame.draw.circle(surf, BLACK, (8, 10), 2)
        pygame.draw.circle(surf, WHITE, (17, 8), 4)
        pygame.draw.circle(surf, BLACK, (17, 8), 2)
        
        return surf
    
    @staticmethod
    def create_enemy_caterpillar():
        frames = []
        for i in range(8):
            surf = pygame.Surface((80, 35), pygame.SRCALPHA)
            
            # Segmented body with smooth animation
            segments = 6
            for j in range(segments):
                x = j * 12 + 10
                y = 17 + math.sin(i * math.pi/4 + j * 0.8) * 5
                
                # Segment with gradient
                segment_surf = pygame.Surface((14, 18), pygame.SRCALPHA)
                color_base = (0, 180, 0) if j % 2 == 0 else (0, 150, 0)
                pygame.draw.ellipse(segment_surf, color_base, (0, 0, 14, 18))
                pygame.draw.ellipse(segment_surf, (0, 220, 0, 150), (2, 2, 10, 14))
                
                # Segment spots
                pygame.draw.circle(segment_surf, (255, 255, 100, 200), (7, 9), 3)
                
                surf.blit(segment_surf, (int(x), int(y - 9)))
            
            # Detailed head
            head_rect = pygame.Rect(70, 12, 15, 15)
            pygame.draw.ellipse(surf, (0, 200, 0), head_rect)
            
            # Expressive eyes
            eye_offset = math.sin(i * math.pi/4) * 1.5
            pygame.draw.circle(surf, WHITE, (73, 16), 4)
            pygame.draw.circle(surf, BLACK, (73 + eye_offset, 16), 2)
            pygame.draw.circle(surf, WHITE, (78, 16), 4)
            pygame.draw.circle(surf, BLACK, (78 - eye_offset, 16), 2)
            
            # Antennae
            pygame.draw.line(surf, (0, 200, 0), (75, 12), (72, 5), 2)
            pygame.draw.line(surf, (0, 200, 0), (75, 12), (78, 3), 2)
            pygame.draw.circle(surf, (255, 100, 100), (72, 5), 2)
            pygame.draw.circle(surf, (255, 100, 100), (78, 3), 2)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_enemy_mantis():
        frames = []
        for i in range(8):
            surf = pygame.Surface((60, 80), pygame.SRCALPHA)
            
            # Ninja mantis with sleek design
            # Body segments
            pygame.draw.ellipse(surf, (100, 0, 100), (20, 15, 20, 50))
            pygame.draw.ellipse(surf, (140, 0, 140), (22, 17, 16, 46))
            
            # Head with menacing look
            head_points = [(25, 15), (35, 15), (40, 8), (20, 8)]
            pygame.draw.polygon(surf, (120, 0, 120), head_points)
            
            # Animated eyes
            eye_glow = math.sin(i * math.pi/4) * 2 + 6
            pygame.draw.circle(surf, (255, 50, 50, 200), (28, 12), int(eye_glow))
            pygame.draw.circle(surf, (255, 50, 50, 200), (32, 12), int(eye_glow))
            pygame.draw.circle(surf, (255, 100, 100), (28, 12), 4)
            pygame.draw.circle(surf, (255, 100, 100), (32, 12), 4)
            
            # Ninja-style arms (scythes)
            arm_angle = math.radians(45 + i * 10)
            # Left arm/scythe
            x1 = 15
            y1 = 30
            x2 = x1 + math.cos(arm_angle) * 20
            y2 = y1 + math.sin(arm_angle) * 20
            pygame.draw.line(surf, (160, 0, 160), (x1, y1), (x2, y2), 6)
            # Scythe blade
            blade_points = [(x2, y2), 
                          (x2 + math.cos(arm_angle + 0.5) * 10, y2 + math.sin(arm_angle + 0.5) * 10),
                          (x2 + math.cos(arm_angle - 0.5) * 10, y2 + math.sin(arm_angle - 0.5) * 10)]
            pygame.draw.polygon(surf, (200, 200, 200), blade_points)
            
            # Right arm/scythe
            x1 = 45
            y1 = 30
            x2 = x1 - math.cos(arm_angle) * 20
            y2 = y1 + math.sin(arm_angle) * 20
            pygame.draw.line(surf, (160, 0, 160), (x1, y1), (x2, y2), 6)
            # Scythe blade
            blade_points = [(x2, y2), 
                          (x2 - math.cos(arm_angle + 0.5) * 10, y2 + math.sin(arm_angle + 0.5) * 10),
                          (x2 - math.cos(arm_angle - 0.5) * 10, y2 + math.sin(arm_angle - 0.5) * 10)]
            pygame.draw.polygon(surf, (200, 200, 200), blade_points)
            
            # Legs in ninja stance
            for j in range(2):
                leg_y = 50 + j * 15
                # Left leg
                pygame.draw.line(surf, (140, 0, 140), (25, leg_y), (20, leg_y + 12), 4)
                # Right leg
                pygame.draw.line(surf, (140, 0, 140), (35, leg_y), (40, leg_y + 12), 4)
            
            # Ninja scarf
            scarf_length = 10 + math.sin(i * math.pi/4) * 5
            pygame.draw.line(surf, (255, 50, 50), (30, 20), (30, 20 + scarf_length), 3)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_enemy_spider():
        surf = pygame.Surface((60, 45), pygame.SRCALPHA)
        # Detailed spider body
        # Abdomen
        pygame.draw.ellipse(surf, (80, 60, 40), (15, 10, 30, 25))
        # Cephalothorax
        pygame.draw.ellipse(surf, (100, 80, 50), (20, 5, 20, 15))
        
        # Detailed eyes (8 eyes arranged like real spider)
        eye_positions = [(22, 8), (28, 8),   # Front row
                        (20, 10), (30, 10), # Middle row
                        (18, 12), (32, 12), # Back row
                        (20, 14), (30, 14)] # Bottom row
        
        for pos in eye_positions:
            pygame.draw.circle(surf, (255, 255, 255), pos, 2)
            pygame.draw.circle(surf, (0, 0, 0), pos, 1)
        
        # Jointed legs with detail
        for i in range(8):
            angle = i * math.pi/4 + math.pi/8
            # Upper leg segment
            x1 = 25 + math.cos(angle) * 8
            y1 = 15 + math.sin(angle) * 8
            x2 = x1 + math.cos(angle) * 15
            y2 = y1 + math.sin(angle) * 15
            pygame.draw.line(surf, (120, 90, 60), (x1, y1), (x2, y2), 4)
            
            # Lower leg segment
            x3 = x2 + math.cos(angle) * 12
            y3 = y2 + math.sin(angle) * 12
            pygame.draw.line(surf, (140, 110, 80), (x2, y2), (x3, y3), 3)
            
            # Claw
            pygame.draw.circle(surf, (60, 60, 60), (int(x3), int(y3)), 2)
        
        return surf
    
    @staticmethod
    def create_boss():
        frames = []
        for i in range(12):
            surf = pygame.Surface((250, 200), pygame.SRCALPHA)
            
            # Epic cyborg spider queen
            # Main body core with energy field
            core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pulse = math.sin(i * math.pi / 6) * 15 + 40
            pygame.draw.circle(core_glow, (255, 50, 100, 150), (60, 60), pulse)
            pygame.draw.circle(core_glow, (255, 100, 150, 200), (60, 60), pulse * 0.6)
            surf.blit(core_glow, (65, 40))
            
            # Armored body segments
            body_points = [(50, 80), (200, 80), (180, 140), (70, 140)]
            pygame.draw.polygon(surf, (80, 0, 80), body_points)
            
            # Mechanical plating
            for j in range(4):
                plate_x = 70 + j * 30
                plate_rect = pygame.Rect(plate_x, 85, 20, 40)
                pygame.draw.rect(surf, (100, 20, 100), plate_rect, border_radius=4)
                pygame.draw.rect(surf, (150, 50, 150), plate_rect.inflate(-4, -4), border_radius=3)
                
                # Rivets
                pygame.draw.circle(surf, (200, 200, 200), (plate_x + 5, 95), 2)
                pygame.draw.circle(surf, (200, 200, 200), (plate_x + 15, 95), 2)
            
            # Glowing mechanical eyes with tracking
            eye_glow = math.sin(i * math.pi / 3) * 5 + 15
            # Left eye cluster
            pygame.draw.circle(surf, (255, 200, 0, 200), (90, 70), eye_glow)
            pygame.draw.circle(surf, (255, 255, 100), (90, 70), 10)
            pygame.draw.circle(surf, (100, 50, 0), (90, 70), 6)
            # Right eye cluster
            pygame.draw.circle(surf, (255, 200, 0, 200), (160, 70), eye_glow)
            pygame.draw.circle(surf, (255, 255, 100), (160, 70), 10)
            pygame.draw.circle(surf, (100, 50, 0), (160, 70), 6)
            
            # Animated mechanical legs with joints
            for leg in range(4):
                base_angle = leg * math.pi/2 + i * 0.2
                
                # Upper leg segment
                x1 = 125 + math.cos(base_angle) * 30
                y1 = 100 + math.sin(base_angle) * 30
                pygame.draw.line(surf, (100, 100, 100), (125, 100), (x1, y1), 10)
                
                # Joint
                pygame.draw.circle(surf, (120, 120, 120), (int(x1), int(y1)), 8)
                
                # Lower leg segment
                x2 = x1 + math.cos(base_angle + 0.3) * 40
                y2 = y1 + math.sin(base_angle + 0.3) * 40
                pygame.draw.line(surf, (140, 140, 140), (x1, y1), (x2, y2), 8)
                
                # Foot/claw
                pygame.draw.circle(surf, (80, 80, 80), (int(x2), int(y2)), 10)
                pygame.draw.line(surf, (60, 60, 60), (x2, y2), 
                               (x2 + math.cos(base_angle + 0.5) * 15, 
                                y2 + math.sin(base_angle + 0.5) * 15), 4)
                pygame.draw.line(surf, (60, 60, 60), (x2, y2), 
                               (x2 + math.cos(base_angle - 0.5) * 15, 
                                y2 + math.sin(base_angle - 0.5) * 15), 4)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_powerup(type="weapon"):
        surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Glowing orb base
        pygame.draw.circle(surf, (255, 255, 255, 100), (20, 20), 20)
        
        if type == "weapon":
            # Energy weapon powerup
            inner_glow = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(inner_glow, (0, 150, 255, 200), (16, 16), 16)
            surf.blit(inner_glow, (4, 4))
            
            # Lightning bolt symbol
            bolt_points = [(20, 10), (25, 15), (20, 20), (25, 25), (20, 30), (15, 25), (20, 20), (15, 15)]
            pygame.draw.polygon(surf, (255, 255, 100), bolt_points)
            
            # Sparkle effect
            for angle in [0, 90, 180, 270]:
                x = 20 + math.cos(math.radians(angle)) * 25
                y = 20 + math.sin(math.radians(angle)) * 25
                pygame.draw.line(surf, (100, 200, 255, 150), (20, 20), (x, y), 2)
        
        elif type == "health":
            # Health powerup
            inner_glow = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(inner_glow, (50, 255, 50, 200), (16, 16), 16)
            surf.blit(inner_glow, (4, 4))
            
            # Heart symbol
            heart_points = []
            for angle in range(0, 360, 10):
                rad = math.radians(angle)
                x = 16 * (math.sin(rad) ** 3)
                y = 13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad)
                heart_points.append((20 + x, 20 - y/2))
            if heart_points:
                pygame.draw.polygon(surf, (255, 100, 100), heart_points)
            
            # Pulse effect
            pygame.draw.circle(surf, (100, 255, 100, 100), (20, 20), 25, 3)
        
        return surf
    
    @staticmethod
    def create_tile(with_grass=True):
        surf = pygame.Surface((64, 64))
        if with_grass:
            # Detailed dirt texture
            for i in range(8):
                for j in range(8):
                    shade = random.randint(80, 120)
                    pygame.draw.rect(surf, (shade-20, shade-40, shade-60), 
                                   (i*8, j*8, 8, 8))
            
            # Lush grass top
            grass_surf = pygame.Surface((64, 20), pygame.SRCALPHA)
            pygame.draw.rect(grass_surf, (60, 140, 60), (0, 0, 64, 20))
            
            # Grass blades
            for i in range(15):
                x = i * 4 + 2
                height = random.randint(8, 16)
                color_variation = random.randint(-20, 20)
                blade_color = (80 + color_variation, 180 + color_variation, 80 + color_variation)
                blade_width = random.randint(1, 2)
                
                # Blade with slight curve
                points = []
                for j in range(height):
                    curve = math.sin(j/height * math.pi) * random.randint(-1, 1)
                    points.append((x + curve, 20 - j))
                
                if len(points) > 1:
                    pygame.draw.lines(grass_surf, blade_color, False, points, blade_width)
            
            surf.blit(grass_surf, (0, 0))
            
            # Edge highlight
            pygame.draw.line(surf, (100, 180, 100), (0, 0), (64, 0), 2)
        else:
            # Stone platform texture
            for i in range(8):
                for j in range(8):
                    shade = random.randint(100, 140)
                    pygame.draw.rect(surf, (shade, shade-20, shade-40), 
                                   (i*8, j*8, 8, 8))
            
            # Platform cracks
            for _ in range(3):
                start_x = random.randint(5, 59)
                start_y = random.randint(5, 59)
                length = random.randint(10, 30)
                angle = random.uniform(0, math.pi * 2)
                
                end_x = start_x + math.cos(angle) * length
                end_y = start_y + math.sin(angle) * length
                
                pygame.draw.line(surf, (80, 60, 40), 
                               (start_x, start_y), (end_x, end_y), 2)
        
        return surf
    
    @staticmethod
    def create_projectile(is_player=True):
        if is_player:
            # Player energy bolt
            surf = pygame.Surface((25, 12), pygame.SRCALPHA)
            
            # Main bolt with gradient
            for i in range(25):
                progress = i / 25
                r = int(100 + 155 * progress)
                g = int(150 + 105 * progress)
                b = 255
                alpha = int(255 * (1 - abs(progress - 0.5) * 2))
                pygame.draw.line(surf, (r, g, b, alpha), (i, 0), (i, 12), 1)
            
            # Core
            pygame.draw.ellipse(surf, (255, 255, 200, 200), (8, 2, 9, 8))
            
            # Trailing particles
            for i in range(3):
                particle_x = random.randint(0, 5)
                particle_y = random.randint(0, 12)
                size = random.randint(2, 4)
                pygame.draw.circle(surf, (200, 230, 255, 150), 
                                 (particle_x, particle_y), size)
            
            return surf
        else:
            # Enemy projectile
            size = random.randint(10, 16)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Swirling energy ball
            pygame.draw.circle(surf, (255, 100, 0, 200), (size//2, size//2), size//2)
            
            # Swirl pattern
            for i in range(4):
                angle = i * math.pi / 2 + pygame.time.get_ticks() / 1000
                x1 = size//2 + math.cos(angle) * (size//4)
                y1 = size//2 + math.sin(angle) * (size//4)
                x2 = size//2 + math.cos(angle + math.pi/4) * (size//2 - 2)
                y2 = size//2 + math.sin(angle + math.pi/4) * (size//2 - 2)
                pygame.draw.line(surf, (255, 200, 0, 150), (x1, y1), (x2, y2), 3)
            
            return surf
    
    @staticmethod
    def create_transformation_frames(start_mode, end_mode):
        """Create transformation animation frames between modes"""
        frames = []
        steps = 30  # Half-second transformation at 60 FPS
        
        if start_mode == "hero" and end_mode == "vehicle":
            # Robot to vehicle transformation
            hero_frames = Assets.create_player_frames()
            vehicle_frames = Assets.create_vehicle_frames()
            
            for i in range(steps):
                progress = i / (steps - 1)
                surf = pygame.Surface((100, 90), pygame.SRCALPHA)
                
                # Calculate intermediate size
                width = 60 * (1 - progress) + 100 * progress
                height = 90 * (1 - progress) + 50 * progress
                
                # Draw transformation energy field
                energy_radius = 50 + math.sin(progress * math.pi) * 20
                pygame.draw.circle(surf, (0, 200, 255, 100), 
                                 (50, 45), int(energy_radius))
                
                # Blend between robot and vehicle
                robot_alpha = int(255 * (1 - progress))
                vehicle_alpha = int(255 * progress)
                
                if progress < 0.5:
                    # Still mostly robot
                    robot_frame = hero_frames[i % len(hero_frames)]
                    robot_scaled = pygame.transform.scale(robot_frame, 
                                                        (int(width), int(height)))
                    robot_scaled.set_alpha(robot_alpha)
                    surf.blit(robot_scaled, (50 - width//2, 45 - height//2))
                else:
                    # Transitioning to vehicle
                    vehicle_frame = vehicle_frames[i % len(vehicle_frames)]
                    vehicle_scaled = pygame.transform.scale(vehicle_frame, 
                                                          (int(width), int(height)))
                    vehicle_scaled.set_alpha(vehicle_alpha)
                    surf.blit(vehicle_scaled, (50 - width//2, 45 - height//2))
                
                # Transformation particles
                for j in range(int(progress * 20)):
                    angle = random.uniform(0, math.pi * 2)
                    distance = energy_radius * random.uniform(0.5, 1.0)
                    x = 50 + math.cos(angle) * distance
                    y = 45 + math.sin(angle) * distance
                    size = random.randint(2, 5)
                    color = (0, 255, 255) if random.random() > 0.5 else (255, 100, 100)
                    pygame.draw.circle(surf, (*color, 200), (int(x), int(y)), size)
                
                frames.append(surf)
        
        else:  # Vehicle to robot transformation
            hero_frames = Assets.create_player_frames()
            vehicle_frames = Assets.create_vehicle_frames()
            
            for i in range(steps):
                progress = i / (steps - 1)
                surf = pygame.Surface((100, 90), pygame.SRCALPHA)
                
                # Calculate intermediate size
                width = 100 * (1 - progress) + 60 * progress
                height = 50 * (1 - progress) + 90 * progress
                
                # Draw transformation energy field
                energy_radius = 50 + math.sin(progress * math.pi) * 20
                pygame.draw.circle(surf, (255, 100, 100, 100), 
                                 (50, 45), int(energy_radius))
                
                # Blend between vehicle and robot
                vehicle_alpha = int(255 * (1 - progress))
                robot_alpha = int(255 * progress)
                
                if progress < 0.5:
                    # Still mostly vehicle
                    vehicle_frame = vehicle_frames[i % len(vehicle_frames)]
                    vehicle_scaled = pygame.transform.scale(vehicle_frame, 
                                                          (int(width), int(height)))
                    vehicle_scaled.set_alpha(vehicle_alpha)
                    surf.blit(vehicle_scaled, (50 - width//2, 45 - height//2))
                else:
                    # Transitioning to robot
                    robot_frame = hero_frames[i % len(hero_frames)]
                    robot_scaled = pygame.transform.scale(robot_frame, 
                                                        (int(width), int(height)))
                    robot_scaled.set_alpha(robot_alpha)
                    surf.blit(robot_scaled, (50 - width//2, 45 - height//2))
                
                # Transformation particles
                for j in range(int(progress * 20)):
                    angle = random.uniform(0, math.pi * 2)
                    distance = energy_radius * random.uniform(0.5, 1.0)
                    x = 50 + math.cos(angle) * distance
                    y = 45 + math.sin(angle) * distance
                    size = random.randint(2, 5)
                    color = (255, 100, 100) if random.random() > 0.5 else (0, 255, 255)
                    pygame.draw.circle(surf, (*color, 200), (int(x), int(y)), size)
                
                frames.append(surf)
        
        return frames

# ================= GAME OBJECTS =================
class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 90)
        self.mode = "hero"  # "hero" or "vehicle"
        self.hero_frames = Assets.create_player_frames()
        self.vehicle_frames = Assets.create_vehicle_frames()
        self.current_frame = 0
        self.animation_timer = 0
        self.image = self.hero_frames[0]
        
        self.health = 5
        self.max_health = 5
        self.has_weapon = False
        self.weapon_power = 1
        self.weapon_cooldown = 0
        self.invincible_timer = 0
        self.transform_cooldown = 0
        self.powerup_timer = 0
        self.direction = 1  # 1 = right, -1 = left
        self.dead = False
        self.jump_buffer = 0
        self.coyote_time = 0
        self.update_image()
    
    def update_image(self):
   
        ##
        if self.mode == "hero":
            frames = self.hero_frames
        else:
            frames = self.vehicle_frames
        
        self.image = frames[self.current_frame]
        
        # Flip image based on direction
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        
        # Flash effect when invincible
        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2:
            self.image = self.image.copy()
            self.image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
    
    def update(self, keys, platforms, scroll_x):
        # Handle input
        self.handle_input(keys)
        
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update coyote time
        if self.on_ground:
            self.coyote_time = 6
        elif self.coyote_time > 0:
            self.coyote_time -= 1
        
        # Update jump buffer
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
        
        # Update position
        self.rect.x += self.vel_x
        self.check_horizontal_collisions(platforms)
        
        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_vertical_collisions(platforms)
        
        # Animation
        self.animation_timer += 1
        if abs(self.vel_x) > 0.5:
            if self.animation_timer % 4 == 0:
                frames = self.hero_frames if self.mode == "hero" else self.vehicle_frames
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.update_image()
        elif self.on_ground:
            self.current_frame = 0
            self.update_image()
        
        # Update cooldowns
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer == 0:
                self.update_image()
        if self.transform_cooldown > 0:
            self.transform_cooldown -= 1
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer == 0:
                self.weapon_power = 1
        
        # Screen boundaries
        if self.rect.left < scroll_x:
            self.rect.left = scroll_x
        if self.rect.right > scroll_x + SCREEN_WIDTH:
            self.rect.right = scroll_x + SCREEN_WIDTH
        
        # Prevent falling through bottom
        if self.rect.top > SCREEN_HEIGHT and not self.dead:
            self.dead = True
            self.death_timer = 60
            self.vel_x = 0
            self.vel_y = -10  # small bounce before fall

        return self.rect.midbottom
    
    def check_horizontal_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    self.vel_x = 0
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    self.vel_x = 0
    
    def check_vertical_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
    
    def handle_input(self, keys):
        speed = 6 if self.mode == "hero" else 10
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -speed
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.vel_x = speed
            self.direction = 1
        
        # Jump
        if keys[pygame.K_SPACE]:
            self.jump_buffer = 5
        
        if self.jump_buffer > 0 and (self.on_ground or self.coyote_time > 0) and self.mode == "hero":
            self.vel_y = JUMP_FORCE
            self.jump_buffer = 0
            self.coyote_time = 0
        
        # Shoot
        if keys[pygame.K_x] and self.has_weapon and self.weapon_cooldown == 0:
            return True
        return False
    
    def transform(self):
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx
        
        self.mode = "vehicle" if self.mode == "hero" else "hero"
        self.transform_cooldown = 30  # 0.5 second cooldown
        
        # Adjust size for different modes
        if self.mode == "hero":
            self.rect.height = 90
            self.rect.width = 60
        else:
            self.rect.height = 50
            self.rect.width = 100
        
        # Maintain position
        self.rect.bottom = old_bottom
        self.rect.centerx = old_centerx
        
        self.current_frame = 0
        self.update_image()
    
    def take_damage(self, amount):
        if self.invincible_timer == 0:
            self.health -= amount
            self.invincible_timer = 60  # 1 second invincibility
            self.update_image()
            return True
        return False
    
    def add_health(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def add_powerup(self, type="weapon"):
        if type == "weapon":
            self.has_weapon = True
            self.weapon_power = 2
            self.powerup_timer = 600  # 10 seconds
        elif type == "health":
            self.add_health(2)
    
    def shoot(self):
        if self.has_weapon and self.weapon_cooldown == 0:
            self.weapon_cooldown = 8 if self.weapon_power == 2 else 15
            x = self.rect.centerx + (30 * self.direction)
            y = self.rect.centery - 4


            return Projectile(x, y, self.direction, True, self.weapon_power)
        return None

class Enemy(GameObject):
    def __init__(self, x, y, enemy_type="snail"):
        sizes = {
            "beetle": (70, 50), "scorpion": (80, 60), "bee": (50, 50),
            "caterpillar": (80, 35), "mantis": (60, 80), "spider": (60, 45),
            "snail": (50, 40)
        }
        width, height = sizes.get(enemy_type, (50, 40))
        super().__init__(x, y, width, height)
        self.attack_timer = 0  # We will use this as a jump cooldown
        self.detection_range = 500 # How far the mantis can "see" the hero
        self.is_leaping = False
        self.type = enemy_type
        self.health = 3
        self.animation_timer = 0
        self.current_frame = 0
        self.attack_timer = 0
        self.move_direction = random.choice([-1, 1])        
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 0.5
        self.on_ground = False
        self.jump_cooldown = 0
        
        self.strike_zone = 60 
        # Initialize as None
        self.frames = None
        self.image = None

        # Assign Assets
        if enemy_type == "snail":
            self.base_image = Assets.create_enemy_snail()
            self.speed = 0.6
        elif enemy_type == "caterpillar":
            self.frames = Assets.create_enemy_caterpillar()
            self.speed = 0.8
        elif enemy_type == "scorpion":
            self.frames = Assets.create_enemy_scorpion()
            self.speed = 1.5
        elif enemy_type == "beetle":
            self.frames = Assets.create_enemy_beetle() # Changed to frames for animation
            self.health = 10
            self.speed = 0.7
        elif enemy_type == "mantis":
            self.frames = Assets.create_enemy_mantis()
            self.speed = 0.7  
        elif enemy_type == "spider":
            self.base_image = Assets.create_enemy_spider()
            self.speed = 1
        elif enemy_type == "bee":
            self.frames = Assets.create_enemy_bee()
            self.speed = 0.8
        else:
            self.speed = 1
    
        # SAFE CHECK: Assign image from frames ONLY if frames is a list
        if self.frames is not None: 
            self.image = self.frames[0]
        elif self.image is None:
            # Emergency fallback: magenta square
            self.image = pygame.Surface((width, height))
            self.image.fill((255, 0, 255))
    def handle_gravity_and_collision(self, platforms):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
    ###
    def handle_physics(self, platforms):
    # Apply Gravity
        self.vel_y += 0.8 # Gravity constant
    
    # Vertical Movement & Collision
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    # Horizontal Movement & Collision
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                self.vel_x = 0 # Stop if hitting a wall
    ###
    def handle_movement_and_collision(self, platforms):
        if self.type == "bee":
            self.vel_y = math.sin(pygame.time.get_ticks() * 0.005) * 2
        elif self.type != "spider":
            self.vel_y += GRAVITY
        else:
            self.vel_y = 0

        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        self.vel_x = self.move_direction * self.speed
        self.rect.x += self.vel_x

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.move_direction = -1
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.move_direction = 1

        if self.on_ground and self.type not in ["mantis", "bee"]:
            sensor_x = self.rect.right + 10 if self.move_direction > 0 else self.rect.left - 10
            sensor_rect = pygame.Rect(sensor_x, self.rect.bottom + 5, 2, 2)
            has_ground_ahead = any(sensor_rect.colliderect(p.rect) for p in platforms)
            if not has_ground_ahead:
                self.move_direction *= -1

    def update(self, player_rect, platforms, scroll_x, projectiles, game_objects):
        self.animation_timer += 1
        self.attack_timer += 1

        
        if self.type == "mantis":
            dx = player_rect.centerx - self.rect.centerx
            dist_abs = abs(dx)

        # 1. GROUND LOGIC
            if self.on_ground:
                self.is_leaping = False # Reset leaping state when touching ground
            
            # If too close, stop walking (prevents sticking)
                if dist_abs < self.strike_zone:
                    self.vel_x = 0
                else:
                # Walk toward player
                    self.move_direction = 1 if dx > 0 else -1
                    self.vel_x = self.move_direction * self.speed

            # 2. TRIGGER JUMP (Ninja Attack)
            # Only jump if player is in range (but not too close) and cooldown is 0
                if self.strike_zone < dist_abs < 400 and self.jump_cooldown <= 0:
                    self.vel_y = -15
                    self.vel_x = self.move_direction * 10
                    self.jump_cooldown = 120 
                    self.is_leaping = True

        # 3. AIR LOGIC
            else:
                self.vel_x *= 1.95

        # Apply gravity and update jump cooldown
            if self.jump_cooldown > 0:
                self.jump_cooldown -= 1
            
        # Physics: Move the Mantis
            self.handle_physics(platforms)
            if self.attack_timer % 80 == 0 and dist_abs < 500:
                return "mantis_fire"
        elif self.type == "bee":
            self.rect.y += math.sin(pygame.time.get_ticks() * 0.005) * 2
            self.rect.x += self.move_direction * self.speed
            # Drop honey if above player
            if abs(self.rect.centerx - player_rect.centerx) < 50 and self.attack_timer % 60 == 0:
                return "honey"
        elif self.type == "scorpion":
            self.handle_movement_and_collision(platforms)
            # Fire sting projectile every 100 frames
            if self.attack_timer % 100 == 0:
                return "scorpion_fire"
        elif self.type == "beetle":
            self.handle_movement_and_collision(platforms)
            # Fire heavy blast every 140 frames
            if self.attack_timer % 140 == 0:
                return "beetle_fire"
        
        else:
        # ... keep your other enemies (snail, etc.) as they were ...
            self.handle_movement_and_collision(platforms)
        
        if self.type in ["beetle"]:
            # Every 30 frames, they "freeze" for a split second, then dash
            if (self.animation_timer % 40) < 10:
                actual_speed = 0 # Freeze
            else:
                actual_speed = self.speed * 1 # Dash
        if self.type == "scorpion":
            # Moves in "skittering bursts"
            # Every 60 frames: 40 frames of fast movement, 20 frames of terrifying pause
            cycle = self.animation_timer % 60
            if cycle < 40:
                current_speed = self.speed * 1 
            else:
                current_speed = 0 # The "Stalking" pause
                
        else:
            current_speed = self.speed

        self.handle_movement_and_collision(platforms)
        
        
        if self.frames is not None:
            # Cycle animation
            if self.animation_timer % 6 == 0:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            raw_frame = self.frames[self.current_frame]
        else:
            # For static enemies like Snail/Spider, we need a base_image reference
            # If you haven't defined base_image in __init__, use self.image
            raw_frame = getattr(self, 'base_image', self.image)

        if self.type in ["caterpillar", "scorpion", "beetle"]:
            # These are drawn facing RIGHT. Flip if moving LEFT (-1).
            if self.move_direction == -1:
                self.image = pygame.transform.flip(raw_frame, True, False)
            else:
                self.image = raw_frame
                
        elif self.type == "snail":
            # Snail is drawn facing LEFT. Flip if moving RIGHT (1).
            if self.move_direction == 1:
                self.image = pygame.transform.flip(raw_frame, True, False)
            else:
                self.image = raw_frame
        
        else:
            # Bee, Mantis, Spider: Do not flip, use raw frame directly
            self.image = raw_frame

        # 4. Special Attacks (Caterpillar trails, etc.)
        if self.type == "caterpillar":
            self.handle_movement_and_collision(platforms)
            if self.animation_timer % 60 == 0:
                return "sticky"
        
        else:
            self.handle_movement_and_collision(platforms)
                
        return None
     

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0


class Boss(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 250, 200)
        self.frames = Assets.create_boss()
        self.current_frame = 0
        self.animation_timer = 0
        
        self.health = 100
        self.max_health = 100
        self.attack_timer = 0
        self.phase = 1
        self.move_direction = 1
        self.invincible_timer = 0
        self.image = self.frames[0]
    
    def update(self, player_rect, platforms, scroll_x, projectiles):
        # Animation
        self.animation_timer += 1
        if self.animation_timer % 3 == 0:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        
        # Float up and down
        self.float_offset = self.animation_timer * 0.05
        self.rect.y += math.sin(self.float_offset) * 1
        
        # Move side to side
        self.vel_x = math.sin(self.animation_timer * 0.02) * 2
        self.rect.x += self.vel_x
        
        # Attack patterns
        self.attack_timer -= 1
        new_projectiles = []
        
        if self.attack_timer <= 0:
            if self.phase == 1:
                # Web barrage
                for angle in [-30, -15, 0, 15, 30]:
                    rad = math.radians(angle)
                    web = Projectile(self.rect.centerx, self.rect.centery + 20, 
                                   math.cos(rad), False, 1)
                    web.vel_y = math.sin(rad) * 3
                    web.slow_effect = True
                    new_projectiles.append(web)
                self.attack_timer = 80
            
            elif self.phase == 2:
                # Energy burst
                for _ in range(5):
                    angle = random.uniform(0, math.pi * 2)
                    energy = Projectile(self.rect.centerx, self.rect.centery + 20, 
                                      math.cos(angle), False, 2)
                    energy.vel_y = math.sin(angle) * 2
                    new_projectiles.append(energy)
                self.attack_timer = 60
            
            elif self.phase == 3:
                # Targeted rapid fire
                for _ in range(3):
                    dx = player_rect.centerx - self.rect.centerx
                    dy = player_rect.centery - self.rect.centery
                    dist = max(1, math.sqrt(dx*dx + dy*dy))
                    proj = Projectile(self.rect.centerx, self.rect.centery + 20, 
                                     dx/dist, False, 3)
                    proj.vel_y = dy/dist
                    new_projectiles.append(proj)
                self.attack_timer = 40
            
            # Update phase based on health
            health_percent = self.health / self.max_health
            if health_percent < 0.66 and self.phase == 1:
                self.phase = 2
            elif health_percent < 0.33 and self.phase == 2:
                self.phase = 3
        
        # Update invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        return new_projectiles
    
    def take_damage(self, amount):
        if self.invincible_timer == 0:
            self.health -= amount
            self.invincible_timer = 10
            return True
        return False

class Projectile(GameObject):
    def __init__(self, x, y, direction, is_player=True, damage=1):
        size = (25, 12) if is_player else (12, 12)
        super().__init__(x, y, size[0], size[1])
        self.active = True
        self.is_player = is_player
        self.damage = damage
        self.direction = direction
        self.vel_x = direction * (5 if is_player else 6)
        self.vel_y = 0
        self.image = Assets.create_projectile(is_player)
        self.slow_effect = False  # For web projectiles
        
        if not is_player:
            self.image = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
            proj_color = (255, 100, 0) # Default orange
            pygame.draw.circle(self.image, proj_color, (8, 8), 8)
            # Add a little glow
            pygame.draw.circle(self.image, (255, 255, 255, 150), (8, 8), 4)
        else:
            self.image = Assets.create_projectile(True)
    def update(self, scroll_x):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Remove if off screen
        screen_left = scroll_x - 500
        screen_right = scroll_x + SCREEN_WIDTH + 100
       
        if (self.rect.right < screen_left or 
            self.rect.left > screen_right or
            self.rect.top > SCREEN_HEIGHT + 100 or
            self.rect.bottom < -100):
            return False
        
        return True


class Platform(GameObject):
    def __init__(self, x, y, width=64, height=64, platform_type="ground"):
        super().__init__(x, y, width, height)
        self.platform_type = platform_type
        self.image = Assets.create_tile(platform_type == "ground")
        
        # Different colors for different platforms
        if platform_type == "moving":
            self.image.fill((100, 70, 30))
        elif platform_type == "breakable":
            self.image.fill((150, 100, 50))
            pygame.draw.rect(self.image, (100, 60, 30), (0, 0, 64, 64), 4)

class Powerup(GameObject):
    def __init__(self, x, y, type="weapon"):
        super().__init__(x, y, 40, 40)
        self.type = type
        self.image = Assets.create_powerup(type)
        self.float_offset = random.random() * math.pi * 2
        self.collected = False
    
    def update(self):
        self.float_offset += 0.1
        self.rect.y += math.sin(self.float_offset) * 2

class StickyTrail(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 10)
        self.lifetime = 300  # 5 seconds
        self.damage = 0
        self.surf = pygame.Surface((40, 10), pygame.SRCALPHA)
        # Create sticky goo effect
        pygame.draw.ellipse(self.surf, (120, 100, 60, 200), (0, 0, 40, 10))
        # Bubbles in the goo
        for i in range(3):
            bubble_x = random.randint(5, 35)
            bubble_y = random.randint(2, 8)
            bubble_size = random.randint(2, 4)
            pygame.draw.circle(self.surf, (150, 130, 80, 150), 
                             (bubble_x, bubble_y), bubble_size)
    
    def update(self):
        self.lifetime -= 1
        return self.lifetime > 0
'''
S: Spider (Shoots slowing webs) ......
M: Mantis (Performs leaping ninja attacks) ......
C: Caterpillar (Leaves damaging sticky trails) .....
N: Snail .......
O: Scorpion (Referenced in the extended level data method)
K: Beetle (Referenced in the extended level data method)
B: bee
D: Cyborg Queen
'''
class Level:
    LEVELS = [

# ==================================================
# HORIZONTAL LEVEL 1 – GRASSLAND FLOW
# ==================================================
[
"..................................................................................................................................",
".......................................................................................................................................",
"...............................................................................X........S.....X..........X.....X....................",
".............................XXX...................XS..............X......................X...X...........X.....X.................",
"........................P..................P...................X.......................B.......................X.................",
".......................P.....N........S...P...............X..................................XH...............X.......................",
"............................PP.....X.PP............H.N....................B...............X...X..............X.......................",
"...............PP.........................P........XXX......P.................K......S...X......SX..........X............................",
"................P.......P................NP..................................XXXX............X...X.........X...........................",
"...........N.X..P...N..P.....C...W.X.X..XP.....C....M.....X....H..............C.............X....X....M.M.X.H....C.................",
"XXXXXXXXXXXXXXX.X..XXXXXXXXXXXXXXX.........XXXXXXXXXXXXXXXXXX..X........X..XXXXXXXX..XXXXXXXX.....XXXXXXXXXXXXXXXXXXX.X.X.X.X.X.X.X.XXXXXXX",
"................................................................................................",
],

# ==================================================
# HORIZONTAL LEVEL 2 – ENEMY RHYTHM
# ==================================================
[
"................................................................................................",
".............Q.................Q.................Q.................Q..........................",
".............P.................P.................P.................P..........................",
".............P.................P.................P.................P..........................",
"..................C..................C..................C..................C................",
".............P.................P.................P.................P..........................",
"..................C..................C..................C..................C................",
"....E.................E.................E.................E.................E................",
"XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXX",
"XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
],

# ==================================================
# HORIZONTAL LEVEL 3 – PIPES & PRESSURE
# ==================================================
[
"................................................................................................",
".............Q.................Q.................Q.................Q..........................",
".............P.................P.................P.................P..........................",
"................................................................................................",
".............Q.................Q.................Q.................Q..........................",
".............P.................P.................P.................P..........................",
"..................C..................C..................C..................C................",
"....T...Q..E..............T......E..............T......E..............T......E..............",
"XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXX",
"XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXX..XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
],

# ==================================================
# HORIZONTAL LEVEL 4 – LAVA BUT FAIR
# ==================================================
[
"................................................................................................",
".............Q.................Q.................Q.................Q..........................",
".............P.................P.................P.................P..........................",
"..................C..................C..................C..................C................",
"....E.................E.................E.................E.................E................",
"...................................................................................................",
"...................................................................................................",
"...................................................................................................",
"...................................................................................................",
"...................................................................................................",
"XXXXXXXX....XXXXXXXX..L..XXXXXXXX..L..XXXXXXXX..L..XXXXXXXX..L..XXXXXXXX..L..XXXXXXXX..L..XXXX",
"XXXXXXXX....XXXXXXXX....XXXXXXXX...XXXXXXXX....XXXXXXXX.XXXXXXXX....XXXXXXXX..XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
],

# ==================================================
# HORIZONTAL LEVEL 5 – FAST ENDURANCE RUN
# ==================================================
[
"................................................................................................",
".............Q.................Q.................Q.................Q..........................",
".............P.................P.................P.................P..........................",
"..................C..................C..................C..................C................",
".............P.................P.................P.................P..........................",
"..................C..................C..................C..................C................",
"....E.....E.............E.....E.............E.....E.............E.....E.....................",
"XXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXX",
"XXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
],

]

    def __init__(self, level_num):
        self.level_num = level_num
        self.platforms = []
        self.enemies = []
        self.powerups = []
        self.boss = None
        self.scroll_x = 0
        self.goal_x = MAX_SCROLL_X - 500
        self.particles = []
        self.sticky_trails = []
      
        self.background_objects = []
        
        self.build_level(level_num)
        self.create_background_objects()
        self.dead = False
        self.death_timer = 0

    def create_background_objects(self):
        """Create decorative background objects for each level"""
        if self.level_num == 0:  # Green Hill Zone
            for i in range(60):
                x = random.randint(0, MAX_SCROLL_X)
                y = random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 100)
                size = random.randint(20, 50)
                self.background_objects.append({
                    'type': 'palm_tree',
                    'x': x,
                    'y': y,
                    'size': size
                })
            
            # Add loop-de-loops like Sonic
            for i in range(5):
                loop_x = 800 + i * 1200
                loop_y = SCREEN_HEIGHT - 300
                self.background_objects.append({
                    'type': 'sonic_loop',
                    'x': loop_x,
                    'y': loop_y,
                    'size': 100
                })
            
            # Add springs
            for i in range(10):
                spring_x = 400 + i * 800
                spring_y = SCREEN_HEIGHT - 150
                self.background_objects.append({
                    'type': 'spring',
                    'x': spring_x,
                    'y': spring_y
                })
        
        elif self.level_num == 1:  # Underground Caverns
            for i in range(80):
                x = random.randint(0, MAX_SCROLL_X)
                y = random.randint(100, SCREEN_HEIGHT - 100)
                size = random.randint(10, 30)
                self.background_objects.append({
                    'type': 'stalactite' if y < SCREEN_HEIGHT//2 else 'stalagmite',
                    'x': x,
                    'y': y,
                    'size': size
                })
            
            # Add Mario-style pipes
            for i in range(8):
                pipe_x = 600 + i * 900
                pipe_height = random.randint(80, 150)
                self.background_objects.append({
                    'type': 'pipe',
                    'x': pipe_x,
                    'y': SCREEN_HEIGHT - 100,
                    'height': pipe_height
                })
            
            # Add moving platforms
            for i in range(12):
                platform_x = 300 + i * 600
                platform_y = SCREEN_HEIGHT - 200 - (i % 3) * 100
                self.background_objects.append({
                    'type': 'moving_platform',
                    'x': platform_x,
                    'y': platform_y,
                    'move_range': 100
                })
        
        elif self.level_num == 2:  # Sky Fortress
            for i in range(40):
                x = random.randint(0, MAX_SCROLL_X)
                y = random.randint(50, SCREEN_HEIGHT - 200)
                size = random.randint(30, 60)
                self.background_objects.append({
                    'type': 'floating_island',
                    'x': x,
                    'y': y,
                    'size': size
                })
            
            # Add clouds with platforms
            for i in range(15):
                cloud_x = 200 + i * 800
                cloud_y = 200 + (i % 4) * 100
                cloud_size = random.randint(80, 120)
                self.background_objects.append({
                    'type': 'cloud_platform',
                    'x': cloud_x,
                    'y': cloud_y,
                    'size': cloud_size
                })
            
            # Add cannons like in Sonic
            for i in range(6):
                cannon_x = 500 + i * 1000
                cannon_y = SCREEN_HEIGHT - 250
                self.background_objects.append({
                    'type': 'cannon',
                    'x': cannon_x,
                    'y': cannon_y
                })
        
        elif self.level_num == 3:  # Final Castle
            for i in range(30):
                x = random.randint(0, MAX_SCROLL_X)
                y = random.randint(SCREEN_HEIGHT - 300, SCREEN_HEIGHT - 100)
                size = random.randint(40, 80)
                self.background_objects.append({
                    'type': 'castle_tower',
                    'x': x,
                    'y': y,
                    'size': size
                })
            
            # Add lava pits
            for i in range(10):
                lava_x = 400 + i * 1000
                lava_width = random.randint(100, 200)
                self.background_objects.append({
                    'type': 'lava_pit',
                    'x': lava_x,
                    'y': SCREEN_HEIGHT - 50,
                    'width': lava_width
                })
            
            # Add castle decorations
            for i in range(20):
                flag_x = 200 + i * 600
                flag_y = SCREEN_HEIGHT - 350
                self.background_objects.append({
                    'type': 'castle_flag',
                    'x': flag_x,
                    'y': flag_y
                })
    

    def build_from_level_data(self, level_num):
        level_data = self.LEVELS[level_num]
        tile_size = 64
        
        for y, row in enumerate(level_data):
            for x, char in enumerate(row):
                pos_x = x * tile_size
                pos_y = y * tile_size
                
                if char == 'X':
                    # Ground
                    self.platforms.append(Platform(pos_x, pos_y))
                elif char == 'P':
                    # Platform
                    self.platforms.append(Platform(pos_x, pos_y, platform_type="ground"))
                elif char == 'S':
                    # Spider enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "spider"))
                elif char == 'M':
                    # Mantis enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "mantis"))
                elif char == 'C':
                    # Caterpillar enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "caterpillar"))
                elif char == 'N':
                    # Caterpillar enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "snail"))                    
                elif char == 'O':
                    # Scorpion enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "scorpion"))
                elif char == 'B':
                    # Beetle enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "beetle"))
                elif char == 'K':
                    # Bee enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "bee"))
                elif char == 'D':
                    # Boss
                    self.boss = Boss(pos_x - 125, pos_y - 150)
    
    
    
    
    def create_loop(self, center_x, center_y, radius):
        """Create a Sonic-style loop platform"""
        segments = 16
        for i in range(segments):
            angle = (i / segments) * math.pi  # Half circle
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            platform = Platform(x - 32, y - 16, 64, 32, platform_type="ground")
            platform.is_loop = True
            platform.loop_angle = angle
            self.platforms.append(platform)
    
    def create_slope(self, start_x, start_y, length, height):
        """Create a sloped platform"""
        segments = length // 32
        for i in range(segments):
            x = start_x + i * 32
            y = start_y + (i / segments) * height
            
            platform = Platform(x, y, 32, 32, platform_type="ground")
            platform.is_slope = True
            platform.slope_angle = math.atan2(height, length)
            self.platforms.append(platform)
    
    def create_bridge(self, start_x, start_y, length):
        """Create a bridge over a gap"""
        segments = length // 64
        for i in range(segments):
            x = start_x + i * 64
            platform = Platform(x, start_y, 64, 20, platform_type="ground")
            platform.is_bridge = True
            self.platforms.append(platform)
        
        # Add rope/cable supports
        support_spacing = length // 4
        for i in range(4):
            support_x = start_x + i * support_spacing
            support_height = 100
            # Left support
            self.platforms.append(Platform(support_x - 10, start_y, 20, support_height))
            # Right support
            self.platforms.append(Platform(support_x + 54, start_y, 20, support_height))
    
    def create_background_objects(self):
        """Create decorative background objects for each level"""
        if self.level_num == 0:  # Training Grounds
            for i in range(20):
                x = random.randint(0, MAX_SCROLL_X)
                y = random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 100)
                size = random.randint(20, 50)
                self.background_objects.append({
                    'type': 'tree',
                    'x': x,
                    'y': y,
                    'size': size
                })
        
        elif self.level_num == 1:  # Enemy Forest
            for i in range(30):
                x = random.randint(0, MAX_SCROLL_X)
                y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 50)
                height = random.randint(80, 150)
                self.background_objects.append({
                    'type': 'forest_tree',
                    'x': x,
                    'y': y,
                    'height': height
                })
        
        elif self.level_num == 2:  # Caves
            for i in range(40):
                x = random.randint(0, MAX_SCROLL_X)
                y = random.randint(100, SCREEN_HEIGHT - 100)
                size = random.randint(10, 30)
                self.background_objects.append({
                    'type': 'stalactite' if y < SCREEN_HEIGHT//2 else 'stalagmite',
                    'x': x,
                    'y': y,
                    'size': size
                })
    
    def build_level(self, level_num):
        level_data = self.LEVELS[level_num]
        tile_size = 64
        
        # Calculate where to place powerups (only on accessible platforms)
        powerup_positions = []
        
        for y, row in enumerate(level_data):
            for x, char in enumerate(row):
                pos_x = x * tile_size
                pos_y = y * tile_size
                
                if char == 'X':
                    # Ground
                    self.platforms.append(Platform(pos_x, pos_y))
                elif char == 'P':
                    # Platform
                    self.platforms.append(Platform(pos_x, pos_y, platform_type="ground"))
                    
                elif char == 'S':
                    # Spider enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "spider"))
                
                elif char == 'M':
                    # Mantis enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "mantis"))
                
                elif char == 'C':
                    # Caterpillar enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "caterpillar"))
                elif char == 'BOSS':
                    # Boss
                    self.boss = Boss(pos_x - 125, pos_y - 150)
                elif char == 'N':
                    # Mantis enemy
                    self.enemies.append(Enemy(pos_x, pos_y, "snail"))
                elif char == 'O':
                    self.enemies.append(Enemy(pos_x, pos_y, "scorpion"))
                elif char == 'K':
                    self.enemies.append(Enemy(pos_x, pos_y, "beetle"))
                elif char == 'B':
                    self.enemies.append(Enemy(pos_x, pos_y, "bee"))                        
                elif char == 'W':
                    # Place Weapon Powerup exactly here
                    self.powerups.append(Powerup(pos_x + 12, pos_y + 12, "weapon"))
                elif char == 'H':
                    # Place Health Powerup exactly here
                    self.powerups.append(Powerup(pos_x + 12, pos_y + 12, "health"))    
        if level_num >= 1:
            for i in range(3):
                x = 500 + i * 800
                y = SCREEN_HEIGHT - 200 - i * 100
                moving_platform = Platform(x, y, platform_type="moving")
                moving_platform.move_direction = 1
                moving_platform.move_speed = 2
                moving_platform.move_range = 200
                moving_platform.start_x = x
                self.platforms.append(moving_platform)
    
    def update(self, player, keys):
        # Update scroll based on player position (smooth Mario-style camera)
        target_scroll = player.rect.centerx - SCREEN_WIDTH // 2
        self.scroll_x += (target_scroll - self.scroll_x) * 0.08
        self.scroll_x = max(0, min(self.scroll_x, MAX_SCROLL_X - SCREEN_WIDTH))
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update sticky trails
        self.sticky_trails = [t for t in self.sticky_trails if t.update()]
        
        # Update moving platforms
        for platform in self.platforms:
            if hasattr(platform, 'move_direction'):
                platform.rect.x += platform.move_speed * platform.move_direction
                if abs(platform.rect.x - platform.start_x) > platform.move_range:
                    platform.move_direction *= -1
        
        # Collect powerups
        collected_powerups = []
        for powerup in self.powerups[:]:
            if not powerup.collected and player.rect.colliderect(powerup.rect):
                player.add_powerup(powerup.type)
                powerup.collected = True
                collected_powerups.append(powerup)
                
                # Add collection particles
                for _ in range(30):
                    color = POWERUP_BLUE if powerup.type == "weapon" else POWERUP_GREEN
                    self.particles.append(Particle(
                        powerup.rect.centerx, powerup.rect.centery,
                        color,
                        [random.uniform(-4, 4), random.uniform(-6, -3)],
                        50
                    ))
        
        for powerup in collected_powerups:
            self.powerups.remove(powerup)
        
        # Update powerups
        for powerup in self.powerups:
            powerup.update()
        
        # Check for sticky trail collisions
        for trail in self.sticky_trails:
            if player.rect.colliderect(trail.rect) and player.mode == "hero":
                player.vel_x *= 0.3  # Slow down significantly in sticky trails
                if random.random() < 0.1:  # Occasionally take damage
                    player.take_damage(1)
        
        # Check for level completion
        if player.rect.centerx >= self.goal_x:
            if self.boss is not None:
                if self.boss.health <= 0:
                    return "COMPLETE"
            else:
                return "COMPLETE"
        
        return "PLAYING"
    
    def draw_background(self, screen):
        # Draw background with gradient based on level
        if self.level_num == 3:  # Boss level - dark cave
            for y in range(SCREEN_HEIGHT):
                progress = y / SCREEN_HEIGHT
                r = int(15 * (1 - progress) + 5 * progress)
                g = int(20 * (1 - progress) + 5 * progress)
                b = int(40 * (1 - progress) + 10 * progress)
                pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
            # Cave details with parallax
            for obj in self.background_objects:
                if obj['type'] == 'stalactite':
                    parallax_x = obj['x'] - self.scroll_x * 0.3
                    if -100 < parallax_x < SCREEN_WIDTH + 100:
                        size = obj['size']
                        points = [
                            (parallax_x, obj['y']),
                            (parallax_x - size//2, obj['y'] + size * 2),
                            (parallax_x + size//2, obj['y'] + size * 2)
                        ]
                        pygame.draw.polygon(screen, (80, 70, 60), points)
                        pygame.draw.polygon(screen, (100, 90, 70), points, 2)
                
                elif obj['type'] == 'stalagmite':
                    parallax_x = obj['x'] - self.scroll_x * 0.3
                    if -100 < parallax_x < SCREEN_WIDTH + 100:
                        size = obj['size']
                        points = [
                            (parallax_x, obj['y']),
                            (parallax_x - size//2, obj['y'] - size * 2),
                            (parallax_x + size//2, obj['y'] - size * 2)
                        ]
                        pygame.draw.polygon(screen, (80, 70, 60), points)
                        pygame.draw.polygon(screen, (100, 90, 70), points, 2)
            
            # Glowing crystals
            for i in range(10):
                crystal_x = (i * 400 - self.scroll_x * 0.2) % (SCREEN_WIDTH + 800) - 400
                crystal_y = 100 + (i * 120) % 400
                
                # Crystal glow
                crystal_surf = pygame.Surface((40, 60), pygame.SRCALPHA)
                for j in range(5):
                    alpha = 100 - j * 20
                    pygame.draw.polygon(crystal_surf, (100, 200, 255, alpha),
                                      [(20, 0), (0, 60), (40, 60)])
                screen.blit(crystal_surf, (crystal_x, crystal_y))
        
        else:  # Outdoor levels
            # Gradient sky
            sky_colors = [
                ((100, 150, 255), (150, 220, 255)),  # Level 1: Day
                ((80, 120, 200), (120, 180, 240)),   # Level 2: Evening
                ((60, 80, 120), (100, 130, 180))     # Level 3: Dusk
            ][min(self.level_num, 2)]
            
            for y in range(SCREEN_HEIGHT):
                progress = y / SCREEN_HEIGHT
                r = int(sky_colors[0][0] * (1 - progress) + sky_colors[1][0] * progress)
                g = int(sky_colors[0][1] * (1 - progress) + sky_colors[1][1] * progress)
                b = int(sky_colors[0][2] * (1 - progress) + sky_colors[1][2] * progress)
                pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
            # Draw clouds with parallax
            for i in range(8):
                cloud_x = (i * 450 - self.scroll_x * 0.15) % (SCREEN_WIDTH + 900) - 450
                cloud_y = 50 + (i * 60) % 150
                self.draw_cloud(screen, cloud_x, cloud_y, i % 3)
            
            # Draw background objects with parallax
            for obj in self.background_objects:
                parallax_x = obj['x'] - self.scroll_x * 0.5
                
                if obj['type'] == 'tree' and -200 < parallax_x < SCREEN_WIDTH + 200:
                    # Simple tree
                    trunk_height = obj['size']
                    trunk_width = trunk_height // 4
                    pygame.draw.rect(screen, (100, 70, 40),
                                   (parallax_x - trunk_width//2, obj['y'] - trunk_height,
                                    trunk_width, trunk_height))
                    
                    foliage_size = trunk_height
                    pygame.draw.circle(screen, (60, 120, 60),
                                     (parallax_x, obj['y'] - trunk_height - foliage_size//2),
                                     foliage_size//2)
                
                elif obj['type'] == 'forest_tree' and -300 < parallax_x < SCREEN_WIDTH + 300:
                    # Forest tree
                    trunk_height = obj['height']
                    trunk_width = trunk_height // 6
                    pygame.draw.rect(screen, (80, 50, 30),
                                   (parallax_x - trunk_width//2, obj['y'] - trunk_height,
                                    trunk_width, trunk_height))
                    
                    # Layered foliage
                    for j in range(3):
                        layer_size = trunk_height * (0.8 - j * 0.2)
                        layer_y = obj['y'] - trunk_height - j * (layer_size//3)
                        color_shade = 40 - j * 10
                        pygame.draw.circle(screen, (40 + color_shade, 100 + color_shade, 40),
                                         (parallax_x, layer_y), layer_size//2)
    
    def draw_cloud(self, screen, x, y, cloud_type):
        cloud_surf = pygame.Surface((180, 80), pygame.SRCALPHA)
        
        if cloud_type == 0:  # Fluffy cloud
            pygame.draw.ellipse(cloud_surf, (255, 255, 255, 220), (0, 40, 100, 30))
            pygame.draw.ellipse(cloud_surf, (255, 255, 255, 220), (40, 30, 120, 40))
            pygame.draw.ellipse(cloud_surf, (255, 255, 255, 220), (80, 40, 100, 30))
        
        elif cloud_type == 1:  # Wispy cloud
            for i in range(5):
                offset = i * 25
                width = 60 + random.randint(-10, 10)
                height = 20 + random.randint(-5, 5)
                alpha = 180 + random.randint(-30, 30)
                pygame.draw.ellipse(cloud_surf, (255, 255, 255, alpha),
                                  (offset, 30 + i * 8, width, height))
        
        else:  # Storm cloud
            pygame.draw.ellipse(cloud_surf, (150, 150, 170, 200), (0, 30, 160, 50))
            pygame.draw.ellipse(cloud_surf, (130, 130, 150, 180), (20, 40, 140, 40))
        
        screen.blit(cloud_surf, (x, y))
    
    def draw(self, screen, player):
        # Draw background
        self.draw_background(screen)
        
        # Draw platforms
        for platform in self.platforms:
            if platform.rect.right > self.scroll_x - 100 and platform.rect.left < self.scroll_x + SCREEN_WIDTH + 100:
                screen.blit(platform.image, (platform.rect.x - self.scroll_x, platform.rect.y))
        
        # Draw sticky trails
        for trail in self.sticky_trails:
            screen.blit(trail.surf, (trail.rect.x - self.scroll_x, trail.rect.y))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen, self.scroll_x)
        
        # Draw powerups
        for powerup in self.powerups:
            if powerup.rect.right > self.scroll_x - 50 and powerup.rect.left < self.scroll_x + SCREEN_WIDTH + 50:
                screen.blit(powerup.image, (powerup.rect.x - self.scroll_x, powerup.rect.y))
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.rect.right > self.scroll_x - 100 and enemy.rect.left < self.scroll_x + SCREEN_WIDTH + 100:
                screen.blit(enemy.image, (enemy.rect.x - self.scroll_x, enemy.rect.y))
        
        # Draw boss
        if self.boss and self.boss.rect.right > self.scroll_x - 200 and self.boss.rect.left < self.scroll_x + SCREEN_WIDTH + 200:
            screen.blit(self.boss.image, (self.boss.rect.x - self.scroll_x, self.boss.rect.y))

# ================= UI RENDERER =================
class UIRenderer:
    @staticmethod
    def draw_hud(screen, player, level_num, scroll_x, lives, score):
        # Health bar (Mario-style)
        bar_width = 200
        bar_height = 25
        bar_x = 20
        bar_y = 20
        
        # Background
        pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        
        # Health fill with gradient
        health_percent = player.health / player.max_health
        health_width = int(bar_width * health_percent)
        
        health_surf = pygame.Surface((health_width, bar_height))
        for x in range(health_width):
            color_progress = x / health_width
            if health_percent > 0.7:
                r = int(0 * (1 - color_progress) + 100 * color_progress)
                g = int(255 * (1 - color_progress) + 200 * color_progress)
                b = 0
            elif health_percent > 0.3:
                r = 255
                g = 255
                b = 0
            else:
                r = 255
                g = int(255 * color_progress)
                b = 0
            pygame.draw.line(health_surf, (r, g, b), (x, 0), (x, bar_height))
        
        screen.blit(health_surf, (bar_x, bar_y))
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)
        
        # Health text
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"ENERGY: {player.health}/{player.max_health}", True, WHITE)
        screen.blit(health_text, (bar_x + 10, bar_y + 3))
        
        # Mode indicator with icon
        mode_color = PLAYER_BLUE if player.mode == "hero" else PLAYER_RED
        mode_icon = "🤖" if player.mode == "hero" else "🚗"
        mode_text = font.render(f"{mode_icon} {player.mode.upper()}", True, mode_color)
        screen.blit(mode_text, (bar_x + 220, bar_y))
        
        # Weapon status
        if player.has_weapon:
            if player.weapon_power > 1:
                weapon_text = "⚡ POWER SHOT"
                weapon_color = UI_YELLOW
                timer_color = (255, 200, 0)
            else:
                weapon_text = "🔫 BASIC SHOT"
                weapon_color = (200, 200, 200)
                timer_color = (150, 150, 150)
            
            weapon_surf = font.render(weapon_text, True, weapon_color)
            screen.blit(weapon_surf, (bar_x + 220, bar_y + 25))
            
            # Powerup timer bar
            if player.powerup_timer > 0:
                timer_width = 150
                timer_height = 8
                timer_x = bar_x + 220
                timer_y = bar_y + 50
                
                pygame.draw.rect(screen, (50, 50, 50), (timer_x, timer_y, timer_width, timer_height), border_radius=4)
                power_width = (player.powerup_timer / 600) * timer_width
                pygame.draw.rect(screen, timer_color, (timer_x, timer_y, power_width, timer_height), border_radius=4)
        
        # Lives and score (Mario-style)
        lives_text = font.render(f"LIVES: {lives}", True, (255, 255, 100))
        screen.blit(lives_text, (SCREEN_WIDTH - 200, bar_y))
        
        score_text = font.render(f"SCORE: {score}", True, (200, 200, 255))
        screen.blit(score_text, (SCREEN_WIDTH - 200, bar_y + 25))
        
        # Level indicator
        level_text = font.render(f"WORLD {level_num + 1}-{min(level_num + 1, 4)}", True, UI_ORANGE)
        screen.blit(level_text, (SCREEN_WIDTH - 200, bar_y + 50))
        
        # Progress bar (Super Mario World style)
        progress = scroll_x / (MAX_SCROLL_X - 500)
        prog_width = 300
        prog_height = 12
        prog_x = SCREEN_WIDTH // 2 - prog_width // 2
        prog_y = SCREEN_HEIGHT - 30
        
        pygame.draw.rect(screen, (40, 40, 40), (prog_x, prog_y, prog_width, prog_height), border_radius=6)
        pygame.draw.rect(screen, (0, 200, 0), (prog_x, prog_y, progress * prog_width, prog_height), border_radius=6)
        pygame.draw.rect(screen, WHITE, (prog_x, prog_y, prog_width, prog_height), 2, border_radius=6)
        
        # Flag at end of progress bar
        flag_x = prog_x + prog_width - 5
        pygame.draw.line(screen, UI_YELLOW, (flag_x, prog_y - 10), (flag_x, prog_y + prog_height + 10), 3)
        pygame.draw.polygon(screen, PLAYER_RED, [
            (flag_x, prog_y - 10),
            (flag_x + 20, prog_y),
            (flag_x, prog_y + 10)
        ])
        
        # Controls hint (fades out after 10 seconds)
        controls_font = pygame.font.Font(None, 20)
        controls = [
            ""
        ]
        
        for i, control in enumerate(controls):
            control_text = controls_font.render(control, True, (220, 220, 220, 180))
            screen.blit(control_text, (SCREEN_WIDTH // 2 - control_text.get_width() // 2, SCREEN_HEIGHT - 60))
    ###
    @staticmethod
    def draw_level_select(screen, current_selection):
        screen.fill((10, 10, 40)) # Dark Blue background
        font_title = pygame.font.Font(None, 80)
        font_opt = pygame.font.Font(None, 50)
    
        title = font_title.render("SELECT MISSION", True, UI_YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    # List of levels (matched to your LEVEL.LEVELS list)
        levels = ["WORLD 1: GRASSLANDS", "WORLD 2: ENEMY RHYTHM", "WORLD 3: PIPES & PRESSURE", "WORLD 4: LAVA PITS", "WORLD 5: ENDURANCE RUN"]
    
        for i, name in enumerate(levels):
            color = WHITE if i == current_selection else (100, 100, 150)
            prefix = ">> " if i == current_selection else "   "
            lvl_img = font_opt.render(f"{prefix}{name}", True, color)
            screen.blit(lvl_img, (SCREEN_WIDTH//2 - 250, 250 + i * 70))
        
        hint = pygame.font.Font(None, 30).render("Press ENTER to Deploy or ESC to go back", True, (200, 200, 200))
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 100))
    ###
    @staticmethod
    def draw_boss_health(screen, boss):
        if not boss or boss.health <= 0:
            return
        
        bar_width = 500
        bar_height = 30
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 10
        
        # Background with metal texture
        pygame.draw.rect(screen, (20, 20, 20), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        
        # Health fill with pulsing effect
        health_percent = boss.health / boss.max_health
        health_width = int(bar_width * health_percent)
        
        # Create gradient health bar
        health_surf = pygame.Surface((health_width, bar_height))
        for x in range(health_width):
            color_progress = x / health_width
            r = int(255 * (1 - color_progress) + 138 * color_progress)
            g = int(0 * (1 - color_progress) + 43 * color_progress)
            b = int(0 * (1 - color_progress) + 226 * color_progress)
            pygame.draw.line(health_surf, (r, g, b), (x, 0), (x, bar_height))
        
        screen.blit(health_surf, (bar_x, bar_y))
        
        # Glowing border
        pygame.draw.rect(screen, (255, 100, 255), (bar_x, bar_y, bar_width, bar_height), 3, border_radius=5)
        pygame.draw.rect(screen, (255, 200, 255, 100), (bar_x-2, bar_y-2, bar_width+4, bar_height+4), 1, border_radius=7)
        
        # Boss name with glow
        font = pygame.font.Font(None, 36)
        name_text = font.render("CYBORG QUEEN", True, (255, 100, 255))
        glow_text = font.render("CYBORG QUEEN", True, (255, 200, 255, 100))
        
        screen.blit(glow_text, (bar_x + bar_width // 2 - glow_text.get_width() // 2 + 2, bar_y + 35 + 2))
        screen.blit(name_text, (bar_x + bar_width // 2 - name_text.get_width() // 2, bar_y + 35))
    
    @staticmethod
    def draw_game_over(screen, score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 82)
        font_medium = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 32)
        
        game_over = font_large.render("MISSION FAILED", True, (255, 50, 50))
        score_text = font_medium.render(f"Final Score: {score}", True, (255, 255, 100))
        restart = font_small.render("Press R to restart or ESC for menu", True, WHITE)
        
        screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 10))
        screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 40))
    
    @staticmethod
    def draw_level_complete(screen, level_num, score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        if level_num == 3:
            overlay.fill((100, 0, 100, 150))
        else:
            overlay.fill((0, 50, 0, 150))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 82)
        font_medium = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 32)
        
        
        title = font_large.render(f"WORLD {level_num + 1} CLEAR!", True, (255, 255, 100))
        subtitle = font_medium.render(f"Score: {score}", True, (200, 255, 200))
        
        continue_text = font_small.render("Press ENTER to continue", True, (255, 255, 150))
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 60))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    
    @staticmethod
    def draw_main_menu(screen):
        # Animated background with parallax stars
        time = pygame.time.get_ticks() / 1000
        screen.fill((10, 10, 40))
        
        # Parallax star layers
        for layer in range(3):
            star_count = 50 // (layer + 1)
            star_speed = 0.2 * (layer + 1)
            star_size = layer + 1
            
            for i in range(star_count):
                x = (i * 37 * (layer + 2) + time * star_speed * 50) % (SCREEN_WIDTH + 400) - 200
                y = (i * 23 * (layer + 1)) % SCREEN_HEIGHT
                
                # Twinkling effect
                twinkle = math.sin(time * 3 + i) * 0.5 + 0.5
                brightness = 100 + int(twinkle * 155)
                
                pygame.draw.circle(screen, (brightness, brightness, brightness), 
                                 (int(x), int(y)), star_size)
        
        # Title with animated glow
        font_title = pygame.font.Font(None, 96)
        font_subtitle = pygame.font.Font(None, 36)
        font_option = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 28)
        
        title_glow = math.sin(time * 2) * 0.3 + 0.7
        
        # Title text with multiple glow layers
        title_text = "TRANSFORMER ADVENTURE"
        for glow_size in range(10, 0, -1):
            glow_alpha = int(30 * (glow_size / 10) * title_glow)
            glow_surf = font_title.render(title_text, True, (0, 100 + glow_size * 15, 200, glow_alpha))
            screen.blit(glow_surf, (SCREEN_WIDTH//2 - glow_surf.get_width()//2 + glow_size//2, 
                                       100 + glow_size//2))
        
        title = font_title.render(title_text, True, (0, 200, 255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = font_subtitle.render("ROBOT • VEHICLE • BATTLE", True, (100, 200, 255))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 180))
        
        # Animated character showcase
        showcase_time = time * 2
        showcase_x = SCREEN_WIDTH // 2
        showcase_y = SCREEN_HEIGHT // 2 - 50
        
        # Robot showcase
        if math.sin(showcase_time) > 0:
            robot_frame = Assets.create_player_frames()[int(showcase_time * 5) % 8]
            robot_scaled = pygame.transform.scale(robot_frame, (80, 120))
            self.screen.blit(robot_scaled, (showcase_x - 150, showcase_y))
            
            # Robot label
            robot_label = font_small.render("ROBOT MODE", True, (100, 200, 255))
            self.screen.blit(robot_label, (showcase_x - 150 - robot_label.get_width()//2 + 40, showcase_y + 130))
        else:
            vehicle_frame = Assets.create_vehicle_frames()[int(showcase_time * 5) % 8]
            vehicle_scaled = pygame.transform.scale(vehicle_frame, (120, 60))
            self.screen.blit(vehicle_scaled, (showcase_x - 60, showcase_y + 30))
            
            # Vehicle label
            vehicle_label = font_small.render("VEHICLE MODE", True, (255, 100, 100))
            self.screen.blit(vehicle_label, (showcase_x - 150 - vehicle_label.get_width()//2 + 40, showcase_y + 130))
        
        # Transformation arrow animation
        arrow_x = showcase_x - 50
        arrow_y = showcase_y + 50
        arrow_pulse = math.sin(time * 3) * 5
        
        for i in range(3):
            arrow_offset = i * 20 + arrow_pulse
            pygame.draw.polygon(self.screen, (255, 255, 100), [
                (arrow_x + arrow_offset, arrow_y),
                (arrow_x + arrow_offset + 20, arrow_y + 10),
                (arrow_x + arrow_offset, arrow_y + 20)
            ])
        
        # Menu options with selection animation
        options = ["START MISSION", "SELECT LEVEl", "HOW TO PLAY", "QUIT GAME"]
        for i, option in enumerate(options):
            y_pos = 400 + i * 80
            
            # Selection indicator
            if i == self.menu_selection:
                # Animated selection glow
                selection_glow = math.sin(time * 5) * 0.3 + 0.7
                glow_surf = pygame.Surface((400, 60), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (0, 100, 200, int(100 * selection_glow)), 
                               (0, 0, 400, 60), border_radius=10)
                self.screen.blit(glow_surf, (SCREEN_WIDTH//2 - 200, y_pos - 10))
                
                color = (255, 255, 0)
                indicator = "» "
            else:
                color = (200, 200, 255)
                indicator = "  "
            
            option_text = font_option.render(f"{indicator}{option}", True, color)
            self.screen.blit(option_text, (SCREEN_WIDTH//2 - option_text.get_width()//2, y_pos))
        
        # Game features with icons
        features = [
            ("⚡", "Transform between Robot and Vehicle"),
            ("⚔️", "Battle unique biomechanical enemies"),
            ("✨", "Collect power-ups for enhanced abilities"),
            ("👑", "Defeat the Cyborg Queen in epic boss battles")
        ]
        
        for i, (icon, feature) in enumerate(features):
            feature_text = font_small.render(f"{icon}  {feature}", True, (180, 220, 255))
            self.screen.blit(feature_text, (SCREEN_WIDTH//2 - feature_text.get_width()//2, 650 + i * 35))
        
        # Controls hint
        controls_text = font_small.render("Use UP/DOWN arrows to navigate • ENTER to select • ESC to quit", 
                                         True, (150, 200, 255))
        self.screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 40))
        
        # Version info
        version_text = font_small.render("Enhanced Edition v2.0", True, (100, 150, 200))
        self.screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 20, SCREEN_HEIGHT - 30))
    
    @staticmethod
    def draw_instructions(screen):
        screen.fill((0, 0, 40))
        
        font_title = pygame.font.Font(None, 64)
        font_section = pygame.font.Font(None, 36)
        font_text = pygame.font.Font(None, 28)
        
        # Title
        title = font_title.render("OPERATION MANUAL", True, (255, 255, 100))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))
        
        # Controls section
        controls_title = font_section.render("CONTROLS", True, (100, 200, 255))
        screen.blit(controls_title, (100, 120))
        
        controls = [
            "← → : Move Left/Right",
            "SPACE : Jump (Robot mode only)",
            "X : Fire Energy Blast (when powered)",
            "T : Transform Robot ⇄ Vehicle (1 sec animation)",
            "ESC : Pause/Return to Menu"
        ]
        
        for i, control in enumerate(controls):
            control_text = font_text.render(control, True, (220, 220, 220))
            screen.blit(control_text, (120, 170 + i * 35))
        
        # Enemies section
        enemies_title = font_section.render("ENEMIES", True, (255, 100, 100))
        screen.blit(enemies_title, (SCREEN_WIDTH//2 + 100, 120))
        
        enemies = [
            "🐌 SNAIL : Slow but tough",
            "🐛 CATERPILLAR : Leaves sticky trails (damage!)",
            "🦗 MANTIS : Leaps with ninja attacks",
            "🕷️ SPIDER : Shoots slowing webs",
            "👑 CYBORG QUEEN : Final boss with 3 phases"
        ]
        
        for i, enemy in enumerate(enemies):
            enemy_text = font_text.render(enemy, True, (220, 220, 220))
            screen.blit(enemy_text, (SCREEN_WIDTH//2 + 120, 170 + i * 35))
        
        # Tips section
        tips_title = font_section.render("COMBAT TIPS", True, (100, 255, 100))
        screen.blit(tips_title, (100, 350))
        
        tips = [
            "• Robot mode can jump",
            "• Vehicle is faster",
            "• Shoot enemies from a distance",
            "• Avoid sticky trails and webs",
            "• Collect blue orbs for weapons",
            "• Collect green hearts for health",
            "• Use transformation strategically"
        ]
        
        for i, tip in enumerate(tips):
            tip_text = font_text.render(tip, True, (220, 220, 220))
            screen.blit(tip_text, (120, 400 + i * 30))
        
        # Power-ups visualization
        powerup_x = SCREEN_WIDTH//2 + 100
        powerup_y = 350
        
        # Weapon power-up
        weapon_surf = Assets.create_powerup("weapon")
        screen.blit(weapon_surf, (powerup_x, powerup_y))
        weapon_text = font_text.render("= Energy Blast (10 sec)", True, (100, 200, 255))
        screen.blit(weapon_text, (powerup_x + 50, powerup_y + 10))
        
        # Health power-up
        health_surf = Assets.create_powerup("health")
        screen.blit(health_surf, (powerup_x, powerup_y + 60))
        health_text = font_text.render("= Restore 2 Health", True, (100, 255, 100))
        screen.blit(health_text, (powerup_x + 50, powerup_y + 70))
        
        # Return instruction
        return_text = font_text.render("Press ESC to return to command center", True, (255, 200, 100))
        screen.blit(return_text, (SCREEN_WIDTH//2 - return_text.get_width()//2, SCREEN_HEIGHT - 50))

# ================= MAIN GAME CLASS =================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Transformer Robot Adventure - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.current_level = 0
        self.player = None
        self.level = None
        self.projectiles = []
        self.running = True
        
    
        # Menu selection
        self.menu_selection = 0
      
        
        # Transformation state
        self.transforming = False
        self.transformation_frames = []
        self.transformation_index = 0
        self.transformation_start_mode = ""
        
        # Game state tracking
        self.score = 0
        self.lives = 3
        
    
    def reset_game(self):
        self.player = Player(200, SCREEN_HEIGHT - 300)
        self.level = Level(self.current_level)
        self.projectiles = []
        self.state = GameState.PLAYING
        self.transforming = False
    
    def start_transformation(self):
        if not self.transforming and self.player.transform_cooldown == 0:
            self.transforming = True
            self.transformation_start_mode = self.player.mode
            self.transformation_frames = Assets.create_transformation_frames(
                self.player.mode,
                "vehicle" if self.player.mode == "hero" else "hero"
            )
            self.transformation_index = 0
            self.state = GameState.TRANSFORMING
    
    def update_transformation(self):
        self.transformation_index += 1
        
        if self.transformation_index >= len(self.transformation_frames):
            # Transformation complete
            self.transforming = False
            self.player.transform()  # This handles the actual mode switch
            self.state = GameState.PLAYING
            self.transformation_frames = []
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:
                            self.current_level = 0
                            self.score = 0
                            self.lives = 3
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif self.menu_selection == 1: # GO TO LEVEL SELECT
                            self.state = GameState.LEVEL_SELECT
                            self.level_select_index = 0    
                        elif self.menu_selection == 2:
                            self.state = GameState.INSTRUCTIONS
                        elif self.menu_selection == 3:
                            self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                ###
                # 2. ADD THIS BLOCK: Controls for the LEVEL SELECT SCREEN
                elif self.state == GameState.LEVEL_SELECT:
                    if event.key == pygame.K_UP:
                        # Move selection up (limit to 5 levels)
                        self.level_select_index = (self.level_select_index - 1) % 5
                    elif event.key == pygame.K_DOWN:
                        # Move selection down
                        self.level_select_index = (self.level_select_index + 1) % 5
                    elif event.key == pygame.K_RETURN:
                        # Confirm selection and start that level
                        self.current_level = self.level_select_index
                        self.score = 0
                        self.lives = 3
                        self.reset_game()
                        # The reset_game method sets state to PLAYING automatically
                    elif event.key == pygame.K_ESCAPE:
                        # Go back to the main menu
                        self.state = GameState.MENU    
                ###
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                    elif event.key == pygame.K_t:
                        self.start_transformation()
                
                elif self.state == GameState.TRANSFORMING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.current_level = 0
                        self.score = 0
                        self.lives = 3
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        if self.current_level == 3:
                            self.state = GameState.MENU
                            self.current_level = 0
                        else:
                            self.current_level += 1
                            self.reset_game()
                            self.state = GameState.PLAYING
                
                elif self.state == GameState.INSTRUCTIONS:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
    
    def update(self):
        if self.state == GameState.TRANSFORMING:
            self.update_transformation()
            return
        
        if self.state != GameState.PLAYING:
            return
        
        keys = pygame.key.get_pressed()
        
        self.projectiles = [p for p in self.projectiles if p.update(self.level.scroll_x)]
        for projectile in self.projectiles:
            for platform in self.level.platforms:
                if projectile.rect.colliderect(platform.rect):
                    # Create small impact particles when hitting a wall
                    for _ in range(5):
                        impact_color = WHITE if projectile.is_player else (255, 165, 0)
                        self.level.particles.append(Particle(
                            projectile.rect.centerx, projectile.rect.centery,
                            impact_color,
                            [random.uniform(-3, 3), random.uniform(-3, 3)],
                            15, size=2
                        ))
                    
                    # Setting vel_x to 0 marks it for removal in your existing cleanup logic
                    projectile.vel_x = 0 
                    break        
        # Update player (but don't allow transformation during transformation animation)
        if not keys[pygame.K_t] or self.player.transform_cooldown > 0:
            self.player.update(keys, self.level.platforms, self.level.scroll_x)
       
        # Check if player died (health or falling)
        if self.player.health <= 0 or self.player.dead:
            self.lives -= 1
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                self.reset_game() # Respawn at beginning of level
            return
        
        # Player shooting
        if keys[pygame.K_x]:
            projectile = self.player.shoot()
            if projectile:
                self.projectiles.append(projectile)
                self.score += 5
        
        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.update(self.level.scroll_x)]
        
        # Update enemies
        for enemy in self.level.enemies[:]:
            # Enemy behavior
            result = enemy.update(self.player.rect, self.level.platforms, 
                                 self.level.scroll_x, self.projectiles, 
                                 self.level.sticky_trails)
            
            if result == "sticky":
                # Caterpillar leaves sticky trail
                trail = StickyTrail(enemy.rect.centerx - 20, enemy.rect.bottom)
                trail.damage = 1  # Sticky trails now deal damage
                self.level.sticky_trails.append(trail)
            ###
            if result == "honey":
                # Drops straight down
                drop = Projectile(enemy.rect.centerx, enemy.rect.bottom, 0, False, 1)
                drop.vel_x = 0
                drop.vel_y = 5
                # Custom Honey Look
                drop.image = pygame.Surface((15, 20), pygame.SRCALPHA)
                pygame.draw.ellipse(drop.image, (255, 220, 0), (0, 0, 15, 20)) # Golden Yellow
                pygame.draw.circle(drop.image, (255, 255, 255, 150), (5, 5), 3) # Highlight
                self.projectiles.append(drop)

            elif result == "mantis_fire":
                # Fast horizontal sonic wave
                wave = Projectile(enemy.rect.centerx, enemy.rect.centery, enemy.move_direction, False, 1)
                wave.vel_x = enemy.move_direction * 12
                # Green energy blade look
                wave.image = pygame.Surface((30, 40), pygame.SRCALPHA)
                pygame.draw.ellipse(wave.image, (0, 255, 100, 180), (0, 0, 10, 40))
                self.projectiles.append(wave)

            elif result == "scorpion_fire":
                # Tail sting shot
                sting = Projectile(enemy.rect.centerx, enemy.rect.top, enemy.move_direction, False, 1)
                sting.vel_x = enemy.move_direction * 8
                # Purple venom look
                sting.image = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.circle(sting.image, (180, 0, 255), (6, 6), 6)
                self.projectiles.append(sting)

            elif result == "beetle_fire":
                # Slow, heavy obsidian blast
                blast = Projectile(enemy.rect.centerx, enemy.rect.centery, enemy.move_direction, False, 2)
                blast.vel_x = enemy.move_direction * 4
                # Large red/black blast
                blast.image = pygame.Surface((25, 25), pygame.SRCALPHA)
                pygame.draw.circle(blast.image, (50, 0, 0), (12, 12), 12)
                pygame.draw.circle(blast.image, (255, 0, 0), (12, 12), 8)
                self.projectiles.append(blast)

            ###
            # Check enemy collisions with player projectiles
            for projectile in self.projectiles[:]:
                if projectile.is_player and enemy.rect.colliderect(projectile.rect):
                    if enemy.take_damage(projectile.damage):
                        self.level.enemies.remove(enemy)
                        self.score += 100
                        # Enhanced death particles
                        for _ in range(25):
                            if enemy.type == "snail":
                                color = (random.randint(180, 220), random.randint(60, 100), random.randint(60, 100))
                            elif enemy.type == "caterpillar":
                                color = (random.randint(0, 50), random.randint(150, 200), random.randint(0, 50))
                            elif enemy.type == "mantis":
                                color = (random.randint(140, 180), 0, random.randint(140, 180))
                            else:  # spider
                                color = (random.randint(100, 140), random.randint(80, 120), random.randint(40, 80))
                            
                            self.level.particles.append(Particle(
                                enemy.rect.centerx, enemy.rect.centery,
                                color,
                                [random.uniform(-6, 6), random.uniform(-8, -3)],
                                random.randint(40, 80)
                            ))
                    projectile.vel_x = 0  # Mark for removal
            
            # Check enemy collisions with player
            if enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(1):
                    self.score -= 50
        
        # Update boss
        if self.level.boss:
            boss_projectiles = self.level.boss.update(self.player.rect, self.level.platforms,
                                                    self.level.scroll_x, self.projectiles)
            if boss_projectiles:
                self.projectiles.extend(boss_projectiles)
            
            # Check boss collisions with player projectiles
            for projectile in self.projectiles[:]:
                if projectile.is_player and self.level.boss.rect.colliderect(projectile.rect):
                    if self.level.boss.take_damage(projectile.damage):
                        self.score += 50
                        # Boss hit particles
                        for _ in range(10):
                            self.level.particles.append(Particle(
                                projectile.rect.centerx, projectile.rect.centery,
                                (255, 100, 100),
                                [random.uniform(-3, 3), random.uniform(-3, 3)],
                                random.randint(20, 40)
                            ))
                    projectile.vel_x = 0
        
        # Check player collisions with enemy projectiles
        for projectile in self.projectiles[:]:
            if not projectile.is_player and self.player.rect.colliderect(projectile.rect):
                if self.player.take_damage(projectile.damage):
                    self.score -= 25
                    # Slow effect from web projectiles
                    if hasattr(projectile, 'slow_effect') and projectile.slow_effect:
                        self.player.vel_x *= 0.3
                projectile.vel_x = 0
        
        # Clean up projectiles marked for removal
        self.projectiles = [p for p in self.projectiles if p.vel_x != 0]
        
        # Update level
        level_status = self.level.update(self.player, keys)
        
        # Check game state
        if self.player.health <= 0:
            self.lives -= 1
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                self.reset_game()
        
        elif level_status == "COMPLETE":
            self.score += 1000 * (self.current_level + 1)
            self.state = GameState.LEVEL_COMPLETE
    
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_main_menu()
        elif self.state == GameState.LEVEL_SELECT:
        # Call the new renderer method
            UIRenderer.draw_level_select(self.screen, self.level_select_index)
        elif self.state == GameState.PLAYING or self.state == GameState.TRANSFORMING:
            # Draw level
            self.level.draw(self.screen, self.player)
            
            if self.state == GameState.TRANSFORMING:
                # Draw transformation animation
                if self.transformation_index < len(self.transformation_frames):
                    transform_surf = self.transformation_frames[self.transformation_index]
                    self.screen.blit(transform_surf,
                                   (self.player.rect.centerx - self.level.scroll_x - 50,
                                    self.player.rect.centery - 45))
            else:
                # Draw player
                self.screen.blit(self.player.image, 
                               (self.player.rect.x - self.level.scroll_x, self.player.rect.y))
            
            # Draw projectiles
            for projectile in self.projectiles:
                self.screen.blit(projectile.image,
                               (projectile.rect.x - self.level.scroll_x, projectile.rect.y))
            
            # Draw UI
            UIRenderer.draw_hud(self.screen, self.player, self.current_level, 
                              self.level.scroll_x, self.lives, self.score)
            
            if self.level.boss and self.level.boss.health > 0:
                UIRenderer.draw_boss_health(self.screen, self.level.boss)
            
            # Show transformation in progress text
            if self.state == GameState.TRANSFORMING:
                font = pygame.font.Font(None, 36)
                transform_text = font.render("TRANSFORMING...", True, (255, 255, 100))
                self.screen.blit(transform_text,
                               (SCREEN_WIDTH//2 - transform_text.get_width()//2,
                                SCREEN_HEIGHT - 100))
        
        elif self.state == GameState.GAME_OVER:
            self.level.draw(self.screen, self.player)
            self.screen.blit(self.player.image, 
                           (self.player.rect.x - self.level.scroll_x, self.player.rect.y))
            UIRenderer.draw_game_over(self.screen, self.score)
        
        elif self.state == GameState.LEVEL_COMPLETE:
            self.level.draw(self.screen, self.player)
            self.screen.blit(self.player.image, 
                           (self.player.rect.x - self.level.scroll_x, self.player.rect.y))
            UIRenderer.draw_level_complete(self.screen, self.current_level, self.score)
        
        elif self.state == GameState.INSTRUCTIONS:
            UIRenderer.draw_instructions(self.screen)
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        # Animated background with parallax stars
        time = pygame.time.get_ticks() / 1000
        self.screen.fill((10, 10, 40))
        
        # Parallax star layers
        for layer in range(3):
            star_count = 50 // (layer + 1)
            star_speed = 0.2 * (layer + 1)
            star_size = layer + 1
            
            for i in range(star_count):
                x = (i * 37 * (layer + 2) + time * star_speed * 50) % (SCREEN_WIDTH + 400) - 200
                y = (i * 23 * (layer + 1)) % SCREEN_HEIGHT
                
                # Twinkling effect
                twinkle = math.sin(time * 3 + i) * 0.5 + 0.5
                brightness = 100 + int(twinkle * 155)
                
                pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                                 (int(x), int(y)), star_size)
        
        # Title with animated glow
        font_title = pygame.font.Font(None, 96)
        font_subtitle = pygame.font.Font(None, 36)
        font_option = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 28)
        
        title_glow = math.sin(time * 2) * 0.3 + 0.7
        
        # Title text with multiple glow layers
        title_text = "TRANSFORMER ADVENTURE"
        for glow_size in range(10, 0, -1):
            glow_alpha = int(30 * (glow_size / 10) * title_glow)
            glow_surf = font_title.render(title_text, True, (0, 100 + glow_size * 15, 200, glow_alpha))
            self.screen.blit(glow_surf, (SCREEN_WIDTH//2 - glow_surf.get_width()//2 + glow_size//2, 
                                       100 + glow_size//2))
        
        title = font_title.render(title_text, True, (0, 200, 255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = font_subtitle.render("ROBOT • VEHICLE • BATTLE", True, (100, 200, 255))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 180))
        
        # Animated character showcase
        showcase_time = time * 2
        showcase_x = SCREEN_WIDTH // 2
        showcase_y = SCREEN_HEIGHT // 2 - 50
        
        # Robot showcase
        if math.sin(showcase_time) > 0:
            robot_frame = Assets.create_player_frames()[int(showcase_time * 5) % 8]
            robot_scaled = pygame.transform.scale(robot_frame, (80, 120))
            self.screen.blit(robot_scaled, (showcase_x - 150, showcase_y))
            
            # Robot label
            robot_label = font_small.render("ROBOT MODE", True, (100, 200, 255))
            self.screen.blit(robot_label, (showcase_x - 150 - robot_label.get_width()//2 + 40, showcase_y + 130))
        else:
            vehicle_frame = Assets.create_vehicle_frames()[int(showcase_time * 5) % 8]
            vehicle_scaled = pygame.transform.scale(vehicle_frame, (120, 60))
            self.screen.blit(vehicle_scaled, (showcase_x - 60, showcase_y + 30))
            
            # Vehicle label
            vehicle_label = font_small.render("VEHICLE MODE", True, (255, 100, 100))
            self.screen.blit(vehicle_label, (showcase_x - 150 - vehicle_label.get_width()//2 + 40, showcase_y + 130))
        
        # Transformation arrow animation
        arrow_x = showcase_x - 50
        arrow_y = showcase_y + 50
        arrow_pulse = math.sin(time * 3) * 5
        
        for i in range(3):
            arrow_offset = i * 20 + arrow_pulse
            pygame.draw.polygon(self.screen, (255, 255, 100), [
                (arrow_x + arrow_offset, arrow_y),
                (arrow_x + arrow_offset + 20, arrow_y + 10),
                (arrow_x + arrow_offset, arrow_y + 20)
            ])
        
        # Menu options with selection animation
        options = ["START MISSION","SELECT LEVEL", "HOW TO PLAY", "QUIT GAME"]
        for i, option in enumerate(options):
            y_pos = 400 + i * 80
            
            # Selection indicator
            if i == self.menu_selection:
                # Animated selection glow
                selection_glow = math.sin(time * 5) * 0.3 + 0.7
                glow_surf = pygame.Surface((400, 60), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (0, 100, 200, int(100 * selection_glow)), 
                               (0, 0, 400, 60), border_radius=10)
                self.screen.blit(glow_surf, (SCREEN_WIDTH//2 - 200, y_pos - 10))
                
                color = (255, 255, 0)
                indicator = "» "
            else:
                color = (200, 200, 255)
                indicator = "  "
            
            option_text = font_option.render(f"{indicator}{option}", True, color)
            self.screen.blit(option_text, (SCREEN_WIDTH//2 - option_text.get_width()//2, y_pos))
        
        # Game features with icons
        features = [
            ("⚡", "Transform between Robot and Vehicle"),
            ("⚔️", "Battle unique biomechanical enemies"),
            ("✨", "Collect power-ups for enhanced abilities"),
            ("👑", "Defeat the Cyborg Queen in epic boss battles")
        ]
        
        for i, (icon, feature) in enumerate(features):
            feature_text = font_small.render(f"{icon}  {feature}", True, (180, 220, 255))
            self.screen.blit(feature_text, (SCREEN_WIDTH//2 - feature_text.get_width()//2, 650 + i * 35))
        
        # Controls hint
        controls_text = font_small.render("Use UP/DOWN arrows to navigate • ENTER to select • ESC to quit", 
                                         True, (150, 200, 255))
        self.screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 40))
        
        # Version info
        version_text = font_small.render("Enhanced Edition v2.0", True, (100, 150, 200))
        self.screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 20, SCREEN_HEIGHT - 30))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# ================= MAIN ENTRY POINT =================
if __name__ == "__main__":

    game = Game()
    game.run()