import pygame
import sys
import random
import math
import heapq
from collections import deque
import os
from itertools import product
from images import *
from sounds import *

pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1280, 720 
ROWS, COLS = 16, 16
CELL_SIZE = min(WIDTH, HEIGHT) // 16
VIEW_RADIUS = 3

# Tạo bề mặt sương mù
fog_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
for x in range(CELL_SIZE):
    for y in range(CELL_SIZE):
        dist = math.sqrt((x - CELL_SIZE//2)**2 + (y - CELL_SIZE//2)**2)
        alpha = min(255, int(255 * (dist / (CELL_SIZE / 2))))
        fog_surface.set_at((x, y), (50, 50, 50, alpha))

fog_animation_time = 0

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
FOG_COLOR = (50, 50, 50)
GOLD_LIGHT = (255, 223, 0)
GOLD_DARK = (184, 134, 11)
BUTTON_HOVER_COLOR = (100, 100, 100)
BUTTON_SHADOW = (30, 30, 30)
TEXT_SHADOW = (50, 50, 50)
PANEL_COLOR = (40, 40, 40)

# Khởi tạo màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rescue the Princess - Horror Maze")

# Fonts
font = pygame.font.SysFont("Arial", 24)
title_font = pygame.font.SysFont("Arial", 48)
button_font = pygame.font.SysFont("Arial", 36)

# Lấy đường dẫn tuyệt đối tới thư mục gốc của dự án
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Load images
try:
    knight_img = pygame.image.load(os.path.join(PROJECT_ROOT, "images", "knight.png")).convert_alpha()
    knight_img = pygame.transform.scale(knight_img, (CELL_SIZE, CELL_SIZE))
    ghost_img = pygame.image.load(os.path.join(PROJECT_ROOT, "images", "ghost.png")).convert_alpha()
    ghost_img = pygame.transform.scale(ghost_img, (CELL_SIZE, CELL_SIZE))
    princess_img = pygame.image.load(os.path.join(PROJECT_ROOT, "images", "princess.png")).convert_alpha()
    princess_img = pygame.transform.scale(princess_img, (CELL_SIZE, CELL_SIZE))
    wall_img = pygame.image.load(os.path.join(PROJECT_ROOT, "images", "stone_wall.png")).convert()
    wall_img = pygame.transform.scale(wall_img, (CELL_SIZE, CELL_SIZE))
    floor_img = pygame.image.load(os.path.join(PROJECT_ROOT, "images", "floor.png")).convert()
    floor_img = pygame.transform.scale(floor_img, (CELL_SIZE, CELL_SIZE))
    background_img = pygame.image.load(os.path.join(PROJECT_ROOT, "images", "background.png")).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Error loading images: {e}")
    knight_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    knight_img.fill((0, 0, 255))
    ghost_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    ghost_img.fill((255, 0, 0))
    princess_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    princess_img.fill((255, 192, 203))
    wall_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    wall_img.fill((100, 100, 100))
    floor_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    floor_img.fill((200, 200, 200))
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((50, 50, 50))

# Load sounds
try:
    button_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "sounds", "button_click.wav"))
    victory_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "sounds", "victory.wav"))
    defeat_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "sounds", "defeat.wav"))
    move_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "sounds", "footstep.wav"))
    princess_found_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "sounds", "rescue.wav"))
    ghost_spawn_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "sounds", "ghost.wav"))
except Exception as e:
    print(f"Error loading sounds: {e}")
    button_sound = pygame.mixer.Sound(buffer=bytearray(0))
    victory_sound = pygame.mixer.Sound(buffer=bytearray(0))
    defeat_sound = pygame.mixer.Sound(buffer=bytearray(0))
    move_sound = pygame.mixer.Sound(buffer=bytearray(0))
    princess_found_sound = pygame.mixer.Sound(buffer=bytearray(0))
    ghost_spawn_sound = pygame.mixer.Sound(buffer=bytearray(0))


# Animation frames
knight_frames = []
princess_frames = []
ghost_frame = []
animation_speed = 0.2
current_frame = 0

def load_animation_frames():
    global knight_frames, princess_frames, ghost_frame
    
    try:
        for i in range(1, 5):
            if os.path.exists(f"knight{i}.png"):
                frame = pygame.image.load(f"knight{i}.png").convert_alpha()
                frame = pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE))
                knight_frames.append(frame)
        
        for i in range(1, 5):
            if os.path.exists(f"princess{i}.png"):
                frame = pygame.image.load(f"princess{i}.png").convert_alpha()
                frame = pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE))
                princess_frames.append(frame)
                
        for i in range(1, 5):
            if os.path.exists(f"ghost{i}.png"):
                frame = pygame.image.load(f"ghost{i}.png").convert_alpha()
                frame = pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE))
                ghost_frame.append(frame)
                
        if not knight_frames:
            knight_frames = [knight_img]
        if not princess_frames:
            princess_frames = [princess_img]
        if not ghost_frame:
            ghost_frame = [ghost_img]
            
    except Exception as e:
        print(f"Lỗi khi tải animation: {e}")
        knight_frames = [knight_img]
        princess_frames = [princess_img]
        ghost_frame = [ghost_img]

def load_scoreboard():
    player_scores_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "player_scores.txt")
    scores = []
    if os.path.exists(player_scores_file):
        with open(player_scores_file, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    map_name = parts[0]
                    steps = parts[1]
                    time = parts[2]
                    rescued = "1" if len(parts) > 3 and parts[3] == "1" else "0"
                    difficulty = parts[4] if len(parts) > 4 else "EASY"
                    scores.append([steps, time, rescued, map_name, difficulty]) 
    return scores


def bfs(maze, start, end):
    queue = deque([start])
    visited = {start: None}
    while queue:
        current = queue.popleft()
        if current == end:
            break
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS:
                # Xem xét cả ô đường đi (0), công chúa (2) và cổng thoát (3)
                if maze[neighbor[0]][neighbor[1]] in [0, 2, 3] and neighbor not in visited:
                    queue.append(neighbor)
                    visited[neighbor] = current
    path = []
    if end in visited:
        current = end
        while current != start:
            path.append(current)
            current = visited[current]
        path.reverse()
    return path

def update_fog_effect():
    global fog_animation_time
    fog_animation_time += 0.01
    
    # Tạo hiệu ứng sương mù động
    for x in range(CELL_SIZE):
        for y in range(CELL_SIZE):
            dist = math.sqrt((x - CELL_SIZE//2)**2 + (y - CELL_SIZE//2)**2)
            wave = math.sin(fog_animation_time + dist/10) * 20
            alpha = min(255, max(0, int(200 + wave * (dist / (CELL_SIZE / 2)))))
            fog_surface.set_at((x, y), (50, 50, 50, alpha))

def draw_maze(maze, visible, offset_x, offset_y, player_pos, use_fog=True, ai_mode=False, selected_algorithm=None, ai_knowledge=None):
    global fog_animation_time
    fog_animation_time += 0.05  # Tăng thời gian để tạo hiệu ứng động nhẹ

    # Kiểm tra xem AI có đang sử dụng thuật toán PO không
    is_po_algorithm = ai_mode and selected_algorithm == "Partially Observable"
    
    # Nếu đang sử dụng thuật toán PO, lấy cài đặt sương mù từ ai_knowledge
    if is_po_algorithm and ai_knowledge:
        use_fog = ai_knowledge.get("fog_enabled", True)

    for row in range(ROWS):
        for col in range(COLS):
            screen_x = (col - offset_x) * CELL_SIZE
            screen_y = (row - offset_y) * CELL_SIZE
            
            # Kiểm tra nếu ô nằm trong vùng hiển thị của màn hình
            if 0 <= screen_x < WIDTH and 0 <= screen_y < HEIGHT:
                # Phần 1: Vẽ các ô có thể nhìn thấy
                if visible[row][col]:
                    # Vẽ nền (sàn hoặc tường)
                    if maze[row][col] == 1:
                        screen.blit(wall_img, (screen_x, screen_y))
                    else:
                        screen.blit(floor_img, (screen_x, screen_y))
                
                # Phần 2: Vẽ sương mù cho các ô không nhìn thấy
                elif use_fog:
                    # Tính khoảng cách từ người chơi để điều chỉnh độ mờ
                    distance = math.sqrt((row - player_pos[0]) ** 2 + (col - player_pos[1]) ** 2)
                    fog_alpha = min(255, max(100, int(255 * (distance / VIEW_RADIUS))))
                    
                    # Tạo hiệu ứng động nhẹ
                    pulse = int(math.sin(fog_animation_time) * 10 + 245)
                    animated_fog = fog_surface.copy()
                    animated_fog.fill((50, 50, 50, fog_alpha), special_flags=pygame.BLEND_RGBA_MULT)
                    
                    screen.blit(animated_fog, (screen_x, screen_y))
                
                # Phần 3: Nếu không sử dụng sương mù, vẽ dấu hỏi hoặc ô thông thường
                else:
                    # Chế độ hiển thị khi không có sương mù
                    if is_po_algorithm:
                        # Trong chế độ PO không sương mù, vẽ dấu ? cho các ô chưa khám phá
                        screen.blit(floor_img, (screen_x, screen_y))
                        question_mark = font.render("?", True, (100, 100, 100))
                        screen.blit(question_mark, (screen_x + CELL_SIZE//2 - question_mark.get_width()//2, 
                                                  screen_y + CELL_SIZE//2 - question_mark.get_height()//2))
                    else:
                        # Trong chế độ thông thường không sương mù, hiển thị toàn bộ map
                        if maze[row][col] == 1:
                            screen.blit(wall_img, (screen_x, screen_y))
                        else:
                            screen.blit(floor_img, (screen_x, screen_y))

def draw_entities(player_pos, princess_pos, ghost_pos, target_pos, visible, offset_x, offset_y):
    global current_frame
    
    if visible[player_pos[0]][player_pos[1]]:
        current_knight = knight_frames[current_frame] if knight_frames else knight_img
        screen.blit(current_knight, ((player_pos[1] - offset_x) * CELL_SIZE, (player_pos[0] - offset_y) * CELL_SIZE))
    
    if visible[princess_pos[0]][princess_pos[1]]:
        current_princess = princess_frames[current_frame] if princess_frames else princess_img
        screen.blit(current_princess, ((princess_pos[1] - offset_x) * CELL_SIZE, (princess_pos[0] - offset_y) * CELL_SIZE))
    
    if ghost_pos and visible[ghost_pos[0]][ghost_pos[1]]:
        current_ghost = ghost_frame[current_frame] if ghost_frame else ghost_img
        screen.blit(current_ghost, ((ghost_pos[1] - offset_x) * CELL_SIZE, (ghost_pos[0] - offset_y) * CELL_SIZE))
    
    if visible[target_pos[0]][target_pos[1]]:
        pygame.draw.circle(screen, (0, 255, 0), ((target_pos[1] - offset_x) * CELL_SIZE + CELL_SIZE // 2, 
                                              (target_pos[0] - offset_y) * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

def update_visible_area(visible, player_pos, radius=VIEW_RADIUS):
    for row in range(ROWS):
        for col in range(COLS):
            distance = math.sqrt((row - player_pos[0]) ** 2 + (col - player_pos[1]) ** 2)
            if distance <= radius:
                visible[row][col] = True

def draw_beautiful_button(rect, text, font, base_color=GOLD_DARK, hover_color=GOLD_LIGHT, 
                         text_color=WHITE, shadow_color=BUTTON_SHADOW, text_shadow=TEXT_SHADOW):
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)
    
    shadow_rect = rect.move(5, 5)
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=10)
    
    color = hover_color if hovered else base_color
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    
    text_surface = font.render(text, True, text_shadow)
    text_rect = text_surface.get_rect(center=(rect.centerx+2, rect.centery+2))
    screen.blit(text_surface, text_rect)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    return hovered

def draw_difficulty_selection():
    screen.blit(background_img, (0, 0))
    
    # Sử dụng hiệu ứng nhấp nhô cho tiêu đề
    draw_animated_title("Select Difficulty", HEIGHT//4)

    easy_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 300, 70)
    hard_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 70)
    back_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 120, 300, 70)

    easy_hovered = draw_beautiful_button(easy_button, "EASY", button_font)
    hard_hovered = draw_beautiful_button(hard_button, "HARD", button_font)
    back_hovered = draw_beautiful_button(back_button, "BACK", button_font)

    # Hiển thị thông tin mô tả về mỗi chế độ chơi
    if easy_hovered:
        info_text = font.render("No fog of war, Ghost moves slower", True, GOLD_LIGHT)
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 - 10))
    
    if hard_hovered:
        info_text = font.render("Fog of war enabled, Ghost moves faster", True, GOLD_LIGHT)
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 90))

    pygame.display.flip()
    return easy_button, hard_button, back_button, easy_hovered, hard_hovered, back_hovered

def draw_animated_title(text, y_pos):
    # Hiệu ứng title nhấp nhô
    offset = math.sin(pygame.time.get_ticks() * 0.002) * 10
    
    # Vẽ bóng
    title_shadow = title_font.render(text, True, TEXT_SHADOW)
    screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 5, y_pos + 5 + offset))
    
    # Vẽ text chính với màu gradient từ vàng sang cam
    progress = 0.5 + math.sin(pygame.time.get_ticks() * 0.001) * 0.5
    color_start = (255, 215, 0)  # Gold
    color_end = (255, 165, 0)    # Orange
    
    title_color = (
        int(color_start[0] * (1-progress) + color_end[0] * progress),
        int(color_start[1] * (1-progress) + color_end[1] * progress),
        int(color_start[2] * (1-progress) + color_end[2] * progress)
    )
    
    title_text = title_font.render(text, True, title_color)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, y_pos + offset))

def draw_main_menu():
    screen.blit(background_img, (0, 0))
    
    # Sử dụng hiệu ứng nhấp nhô cho tiêu đề
    draw_animated_title("Rescue the Princess", HEIGHT//8)

    play_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 220, 300, 70)
    create_map_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 70)
    manage_maps_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 20, 300, 70)
    ai_stats_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 300, 70)
    tutorial_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 180, 300, 70)
    exit_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 280, 300, 70)

    play_hovered = draw_beautiful_button(play_button, "PLAY", button_font)
    create_map_hovered = draw_beautiful_button(create_map_button, "CREATE MAP", button_font)
    manage_maps_hovered = draw_beautiful_button(manage_maps_button, "MANAGE MAPS", button_font)
    ai_stats_hovered = draw_beautiful_button(ai_stats_button, "AI STATS", button_font)
    tutorial_hovered = draw_beautiful_button(tutorial_button, "TUTORIAL", button_font)
    exit_hovered = draw_beautiful_button(exit_button, "EXIT", button_font)

    pygame.display.flip()
    return play_button, create_map_button, manage_maps_button, ai_stats_button, tutorial_button, exit_button, play_hovered, create_map_hovered, manage_maps_hovered, ai_stats_hovered, tutorial_hovered, exit_hovered

def draw_map_management_menu(maps, scroll_offset=0, max_visible=6):
    screen.blit(background_img, (0, 0))
    draw_animated_title("Manage Maps", HEIGHT//10)
    map_buttons = []
    delete_buttons = []
    edit_buttons = []
    map_names = list(maps.keys())
    total_maps = len(map_names)
    visible_maps = map_names[scroll_offset:scroll_offset+max_visible]
    start_y = HEIGHT//4
    for i, map_name in enumerate(visible_maps):
        y_offset = start_y + i * 100
        map_button = pygame.Rect(WIDTH // 2 - 200, y_offset, 300, 50)
        delete_button = pygame.Rect(WIDTH // 2 + 120, y_offset, 100, 50)
        edit_button = pygame.Rect(WIDTH // 2 - 320, y_offset, 100, 50)
        draw_beautiful_button(map_button, map_name, font)
        draw_beautiful_button(delete_button, "DELETE", font, base_color=(200, 50, 50), hover_color=(255, 70, 70))
        draw_beautiful_button(edit_button, "EDIT", font, base_color=(50, 150, 50), hover_color=(70, 200, 70))
        map_buttons.append((map_button, map_name))
        delete_buttons.append((delete_button, map_name))
        edit_buttons.append((edit_button, map_name))
    back_button = pygame.Rect(50, HEIGHT - 100, 200, 60)
    draw_beautiful_button(back_button, "BACK", font, base_color=(70, 70, 70), hover_color=(100, 100, 100))
    if total_maps > max_visible:
        bar_height = max(60, int(max_visible/total_maps * 600))
        bar_y = start_y + int(scroll_offset/total_maps * 600)
        bar_x = WIDTH//2 + 270
        pygame.draw.rect(screen, (60,60,60), (bar_x, start_y, 20, 600), border_radius=10)
        pygame.draw.rect(screen, GOLD_DARK, (bar_x, bar_y, 20, bar_height), border_radius=10)
    pygame.display.flip()
    return map_buttons, delete_buttons, edit_buttons, back_button

def draw_map_selection(maps, scroll_offset=0, max_visible=6):
    screen.blit(background_img, (0, 0))
    draw_animated_title("Select Map", HEIGHT//10)
    map_buttons = []
    hover_states = []
    map_names = list(maps.keys())
    total_maps = len(map_names)
    visible_maps = map_names[scroll_offset:scroll_offset+max_visible]
    start_y = HEIGHT//4
    for i, map_name in enumerate(visible_maps):
        button = pygame.Rect(WIDTH//2 - 150, start_y + i * 100, 300, 80)
        hovered = draw_beautiful_button(button, map_name, button_font)
        map_buttons.append((button, map_name))
        hover_states.append(hovered)
    back_button = pygame.Rect(50, HEIGHT - 100, 200, 60)
    back_hovered = draw_beautiful_button(back_button, "BACK", font, base_color=(70, 70, 70), hover_color=(100, 100, 100))
    if total_maps > max_visible:
        bar_height = max(60, int(max_visible/total_maps * 600))
        bar_y = start_y + int(scroll_offset/total_maps * 600)
        bar_x = WIDTH//2 + 170
        pygame.draw.rect(screen, (60,60,60), (bar_x, start_y, 20, 600), border_radius=10)
        pygame.draw.rect(screen, GOLD_DARK, (bar_x, bar_y, 20, bar_height), border_radius=10)
    pygame.display.flip()
    return map_buttons, back_button, hover_states, back_hovered

"""TÍNH NĂNG AI CHƠI"""
def draw_play_mode_selection():
    screen.blit(background_img, (0, 0))
    
    # Sử dụng hiệu ứng nhấp nhô cho tiêu đề
    draw_animated_title("Select Play Mode", HEIGHT//4)

    manual_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 300, 70)
    ai_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 70)
    back_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 120, 300, 70)

    manual_hovered = draw_beautiful_button(manual_button, "MANUAL PLAY", button_font)
    ai_hovered = draw_beautiful_button(ai_button, "AI PLAY", button_font)
    back_hovered = draw_beautiful_button(back_button, "BACK", button_font)

    pygame.display.flip()
    return manual_button, ai_button, back_button, manual_hovered, ai_hovered, back_hovered
def draw_ai_algorithm_selection():
    screen.blit(background_img, (0, 0))
    draw_animated_title("Select AI Algorithm", HEIGHT//10)
    algorithms = ["BFS", "A*", "Simple Hill Climbing", "Partially Observable", "Min Conflicts", "Q-Learning"]
    # 7 sắc cầu vồng (đỏ, cam, vàng, lục, lam, chàm, tím)
    rainbow_colors = [
        (255, 60, 60),    # Red
        (255, 140, 0),    # Orange
        (255, 215, 0),    # Yellow
        (60, 200, 60),    # Green
        (60, 120, 255),   # Blue
        (120, 60, 255),   # Indigo
        (200, 60, 255)    # Violet
    ]
    algorithm_buttons = []
    hover_states = []
    for i, algo_name in enumerate(algorithms):
        button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150 + i * 60, 300, 50)
        color = rainbow_colors[i % len(rainbow_colors)]
        hovered = draw_beautiful_button(button, algo_name, font, base_color=color, hover_color=(min(color[0]+40,255), min(color[1]+40,255), min(color[2]+40,255)))
        algorithm_buttons.append((button, algo_name))
        hover_states.append(hovered)
    back_button = pygame.Rect(50, HEIGHT - 100, 200, 60)
    back_hovered = draw_beautiful_button(back_button, "BACK", font, base_color=(70, 70, 70), hover_color=(100, 100, 100))
    pygame.display.flip()
    return algorithm_buttons, back_button, hover_states, back_hovered
# PHAN VIỆT TUẤN
# BFS 
def bfs_algorithm(maze, player_pos, princess_pos, target_pos, visible, knowledge=None):
    if knowledge is None:
        knowledge = {
            "princess_rescued": False,
            "visited": set(),
            "path": [],
            "current_path_index": 0
        }
    
    if player_pos == princess_pos and not knowledge["princess_rescued"]:
        knowledge["princess_rescued"] = True
        knowledge["path"] = []
        knowledge["current_path_index"] = 0
    
    goal = princess_pos if not knowledge["princess_rescued"] else target_pos
    
    # Thêm vị trí hiện tại vào tập đã thăm
    knowledge["visited"].add(player_pos)
    
    # Nếu đang có đường đi và chưa đi hết
    if knowledge["path"] and knowledge["current_path_index"] < len(knowledge["path"]):
        next_pos = knowledge["path"][knowledge["current_path_index"]]
        knowledge["current_path_index"] += 1
        return next_pos, knowledge
    
    # Nếu không có đường đi hoặc đã đi hết, tìm đường đi mới
    queue = deque([player_pos])
    visited = {player_pos}
    parent = {player_pos: None}
    
    while queue:
        current = queue.popleft()
        
        if current == goal:
            path = []
            while current != player_pos:
                path.append(current)
                current = parent[current]
            path.reverse()
            knowledge["path"] = path
            knowledge["current_path_index"] = 0
            if path:
                return path[0], knowledge
            break
        
        # Thêm các bước đi có thể vào queue
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (current[0] + dx, current[1] + dy)
            if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS:
                if maze[new_pos[0]][new_pos[1]] != 1 and new_pos not in visited:
                    queue.append(new_pos)
                    visited.add(new_pos)
                    parent[new_pos] = current
    
    # Nếu không tìm được đường đi, tìm bước đi ngẫu nhiên
    possible_moves = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_pos = (player_pos[0] + dx, player_pos[1] + dy)
        if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS:
            if maze[new_pos[0]][new_pos[1]] != 1:
                possible_moves.append(new_pos)
    
    if possible_moves:
        return random.choice(possible_moves), knowledge
    
    return player_pos, knowledge

# A* Algorithm
def astar_algorithm(maze, player_pos, princess_pos, target_pos, visible, knowledge=None):
    if knowledge is None:
        knowledge = {
            "princess_rescued": False
        }
    
    if player_pos == princess_pos and not knowledge["princess_rescued"]:
        knowledge["princess_rescued"] = True
    
    goal = princess_pos if not knowledge["princess_rescued"] else target_pos
    
    path = astar_search(maze, player_pos, goal)
    
    if path and len(path) > 0:
        return path[0], knowledge
    else:
        # Nếu không tìm được đường đi, tìm các ô có thể di chuyển
        possible_moves = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (player_pos[0] + dx, player_pos[1] + dy)
            if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and maze[new_pos[0]][new_pos[1]] != 1:
                possible_moves.append(new_pos)
        
        if possible_moves:
            return random.choice(possible_moves), knowledge
        
        # Nếu không có bước đi nào khả thi, đứng yên
        return player_pos, knowledge

# A* Search với Manhattan Distance Heuristic
def astar_search(maze, start, goal):
    open_set = []
    closed_set = set()
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}
    parent = {start: None}
    
    heapq.heappush(open_set, (f_score[start], start))
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            path = []
            while current and current != start:
                path.append(current)
                current = parent[current]
            return path[::-1] 
        
        closed_set.add(current)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if not (0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS) or maze[neighbor[0]][neighbor[1]] == 1:
                continue
            
            if neighbor in closed_set:
                continue
            
            tentative_g = g_score[current] + 1

            in_open_set = False
            for _, node in open_set:
                if node == neighbor:
                    in_open_set = True
                    break
                    
            if not in_open_set or tentative_g < g_score.get(neighbor, float('inf')):
                parent[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, goal)
                
                if not in_open_set:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return []

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
# NGUYỄN LÂM HUY
#  Simple Hill Climbing Algorithm
def simple_hill_climbing_algorithm(maze, player_pos, princess_pos, target_pos, visible, knowledge=None):
    if knowledge is None:
        knowledge = {
            "princess_rescued": False,
            "visited": set(),
            "local_minima_count": 0,
            "restart_count": 0,
            "max_restarts": 3
        }
    
    if player_pos == princess_pos and not knowledge["princess_rescued"]:
        knowledge["princess_rescued"] = True
    
    goal = princess_pos if not knowledge["princess_rescued"] else target_pos
    
    # Thêm vị trí hiện tại vào tập đã thăm
    knowledge["visited"].add(player_pos)
    
    # Tính khoảng cách hiện tại đến mục tiêu
    current_distance = manhattan_distance(player_pos, goal)
    
    # Tìm các bước đi có thể
    possible_moves = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_pos = (player_pos[0] + dx, player_pos[1] + dy)
        if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS:
            # Kiểm tra ô có phải là tường không
            if maze[new_pos[0]][new_pos[1]] != 1:
                # Tính khoảng cách mới đến mục tiêu
                new_distance = manhattan_distance(new_pos, goal)
                
                # Chọn ngay bước đi đầu tiên cải thiện khoảng cách
                if new_distance < current_distance:
                    return new_pos, knowledge
                
                # Thêm vào danh sách với khoảng cách (để dùng khi bị kẹt)
                possible_moves.append((new_pos, new_distance))
    
    # Nếu không tìm được bước đi nào tốt hơn
    if possible_moves:
        knowledge["local_minima_count"] += 1
        
        # Nếu bị kẹt ở local maxima quá nhiều lần
        if knowledge["local_minima_count"] >= 5:
            knowledge["local_minima_count"] = 0
            knowledge["restart_count"] += 1

            # Nếu đã restart quá nhiều lần, chọn bước đi ngẫu nhiên
            if knowledge["restart_count"] >= knowledge["max_restarts"]:
                return random.choice(possible_moves)[0], knowledge
            
            # Chọn bước đi ngẫu nhiên để thoát khỏi local maxima
            return random.choice(possible_moves)[0], knowledge
        
        # Chọn bước đi có khoảng cách nhỏ nhất trong trường hợp mắc kẹt
        possible_moves.sort(key=lambda x: x[1])
        return possible_moves[0][0], knowledge
    
    # Nếu không có bước đi nào, đứng yên
    return player_pos, knowledge

# Partially Observable 
def partially_observable_algorithm(maze, player_pos, princess_pos, target_pos, visible, knowledge=None):
    # Khởi tạo kiến thức
    if knowledge is None:
        knowledge = {
            "maze": [[None for _ in range(COLS)] for _ in range(ROWS)],
            "probability": [[0.5 for _ in range(COLS)] for _ in range(ROWS)],
            "visited": set(),
            "frontier": set(),
            "princess_found": False,
            "exit_found": False,
            "princess_pos": None,
            "exit_pos": None,
            "princess_rescued": False,
            "exploration_bias": 0.3,
            "visibility_percentage": 50,  # Mặc định 50%
            "fog_enabled": True           # Mặc định bật sương mù
        }
    
    # Reset ma trận visible dựa vào tỷ lệ nhìn thấy
    reset_visible = True
    
    # Nếu không bật fog, hiển thị toàn bộ bản đồ
    if not knowledge.get("fog_enabled", True):
        for row in range(ROWS):
            for col in range(COLS):
                visible[row][col] = True
        reset_visible = False
    
    # Nếu reset_visible vẫn là True, thì thiết lập lại ma trận visible
    if reset_visible:
        # Đầu tiên đặt tất cả các ô về False
        for row in range(ROWS):
            for col in range(COLS):
                visible[row][col] = False
        
        # Luôn hiển thị khu vực xung quanh người chơi
        for dr in range(-VIEW_RADIUS, VIEW_RADIUS+1):
            for dc in range(-VIEW_RADIUS, VIEW_RADIUS+1):
                r, c = player_pos[0] + dr, player_pos[1] + dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    distance = math.sqrt(dr*dr + dc*dc)
                    if distance <= VIEW_RADIUS:
                        visible[r][c] = True
        
        # Tính số ô có thể nhìn thấy dựa vào visibility_percentage
        total_cells = ROWS * COLS
        visible_cells_count = int((knowledge.get("visibility_percentage", 50) / 100) * total_cells)
        current_visible = sum(sum(row) for row in visible)
        
        
        # Thêm các ô ngẫu nhiên nếu chưa đủ số ô cần hiển thị
        if current_visible < visible_cells_count:
            cells_to_add = visible_cells_count - current_visible
            
            # Tạo danh sách các ô chưa nhìn thấy
            invisible_cells = [(r, c) for r in range(ROWS) for c in range(COLS) if not visible[r][c]]
            
            # Nếu cần thêm các ô nhìn thấy và còn ô chưa nhìn thấy
            if cells_to_add > 0 and invisible_cells:
                # Chọn ngẫu nhiên các ô để hiển thị
                random.shuffle(invisible_cells)
                for i in range(min(cells_to_add, len(invisible_cells))):
                    r, c = invisible_cells[i]
                    visible[r][c] = True
        
        # Thống kê sau khi cập nhật
        updated_visible = sum(sum(row) for row in visible)
        print(f"Updated visible cells: {updated_visible}")
    
    # Cập nhật kiến thức dựa trên vùng nhìn thấy
    for row in range(ROWS):
        for col in range(COLS):
            if visible[row][col]:
                knowledge["maze"][row][col] = maze[row][col]
                
                if maze[row][col] == 1:
                    knowledge["probability"][row][col] = 0.0
                else:
                    knowledge["probability"][row][col] = 1.0

                if maze[row][col] == 2:
                    knowledge["princess_found"] = True
                    knowledge["princess_pos"] = (row, col)
                elif maze[row][col] == 3:
                    knowledge["exit_found"] = True
                    knowledge["exit_pos"] = (row, col)
    
    # Cập nhật tập biên (frontier) - các ô đã biết giáp với ô chưa khám phá
    knowledge["frontier"] = set()
    for row in range(ROWS):
        for col in range(COLS):
            if knowledge["maze"][row][col] is not None and knowledge["maze"][row][col] != 1:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = row + dx, col + dy
                    if 0 <= nx < ROWS and 0 <= ny < COLS and knowledge["maze"][nx][ny] is None:
                        knowledge["frontier"].add((row, col))
                        break

    # Cập nhật trạng thái công chúa
    if player_pos == princess_pos and not knowledge["princess_rescued"]:
        knowledge["princess_rescued"] = True

    # Thêm vị trí hiện tại vào tập đã thăm
    knowledge["visited"].add(player_pos)
    
    next_move = None

    # Phase 1: Nếu đã tìm thấy công chúa và chưa giải cứu, di chuyển đến công chúa
    if knowledge["princess_found"] and not knowledge["princess_rescued"]:
        # Tạo bản đồ tạm để tìm đường đi
        temp_maze = [[1 if knowledge["maze"][r][c] == 1 else 0 for c in range(COLS)] for r in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                # Coi các ô chưa khám phá là tường để tránh
                if knowledge["maze"][r][c] is None:
                    temp_maze[r][c] = 1
        
        # Tìm đường đi đến công chúa bằng A*
        path = astar_search(temp_maze, player_pos, knowledge["princess_pos"])
        if path and len(path) > 0:
            next_move = path[0]

    # Phase 2: Nếu đã giải cứu công chúa và đã tìm thấy cổng thoát, di chuyển đến cổng
    elif knowledge["princess_rescued"] and knowledge["exit_found"]:
        temp_maze = [[1 if knowledge["maze"][r][c] == 1 else 0 for c in range(COLS)] for r in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                # Coi các ô chưa khám phá là tường để tránh
                if knowledge["maze"][r][c] is None:
                    temp_maze[r][c] = 1
        
        # Tìm đường đi đến cổng thoát bằng A*
        path = astar_search(temp_maze, player_pos, knowledge["exit_pos"])
        if path and len(path) > 0:
            next_move = path[0]
    
    # Phase 3: Nếu chưa có hướng đi cụ thể, khám phá dựa trên độ hữu ích của mỗi ô
    if next_move is None:
        possible_moves = []
        move_utilities = {}
        
        # Đánh giá độ hữu ích của các ô lân cận
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (player_pos[0] + dx, player_pos[1] + dy)
            if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS:
                # Bỏ qua các ô đã biết là tường
                if knowledge["maze"][new_pos[0]][new_pos[1]] == 1:
                    continue
                
                utility = 0
                
                # Điểm cho ô nằm ở biên - có thể dẫn đến ô chưa khám phá
                if new_pos in knowledge["frontier"]:
                    utility += (1 - knowledge["exploration_bias"]) * 10
                
                # Điểm cho ô chưa khám phá
                if knowledge["maze"][new_pos[0]][new_pos[1]] is None:
                    utility += knowledge["exploration_bias"] * 15
                
                # Điểm cho ô chưa từng thăm
                if new_pos not in knowledge["visited"]:
                    utility += 8

                # Thêm yếu tố ngẫu nhiên nhỏ để tránh bị kẹt
                utility += random.random()
                
                # Lưu lại ô và độ hữu ích của nó
                possible_moves.append(new_pos)
                move_utilities[new_pos] = utility

        # Chọn ô có độ hữu ích cao nhất
        if possible_moves:
            next_move = max(possible_moves, key=lambda pos: move_utilities[pos])
    
    # Phase 4: Nếu không có hướng đi khả thi, chọn ngẫu nhiên một ô lân cận không phải tường
    if next_move is None:
        possible_moves = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (player_pos[0] + dx, player_pos[1] + dy)
            if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS:
                # Nếu biết là tường thì bỏ qua, nếu không biết hoặc biết không phải tường thì thêm vào
                if knowledge["maze"][new_pos[0]][new_pos[1]] != 1:
                    possible_moves.append(new_pos)
        
        if possible_moves:
            next_move = random.choice(possible_moves)
        else:  # Không có bước đi khả thi, đứng yên
            next_move = player_pos
    
    return next_move, knowledge

def draw_po_visibility_selection():
    """Hiển thị cửa sổ chọn tầm nhìn cho thuật toán PO"""
    
    # Lưu màn hình hiện tại để làm nền mờ
    background = screen.copy()
    
    # Tạo lớp mờ
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt
    screen.blit(overlay, (0, 0))
    
    # Vẽ panel chính
    panel_width, panel_height = 500, 300
    panel_rect = pygame.Rect(WIDTH//2 - panel_width//2, HEIGHT//2 - panel_height//2, 
                           panel_width, panel_height)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=15)
    pygame.draw.rect(screen, GOLD_DARK, panel_rect, 3, border_radius=15)
    
    # Tiêu đề
    title_text = button_font.render("Partially Observable Settings", True, GOLD_LIGHT)
    screen.blit(title_text, (panel_rect.centerx - title_text.get_width()//2, panel_rect.y + 20))
    
    # Chữ hướng dẫn
    instruction_text = font.render("Select visibility percentage:", True, WHITE)
    screen.blit(instruction_text, (panel_rect.centerx - instruction_text.get_width()//2, panel_rect.y + 80))
    
    # Vẽ thanh trượt
    slider_width, slider_height = 350, 8
    slider_rect = pygame.Rect(panel_rect.centerx - slider_width//2, panel_rect.y + 130, 
                            slider_width, slider_height)
    pygame.draw.rect(screen, (60, 60, 70), slider_rect, border_radius=4)
    
    # Giá trị và vị trí hiện tại của trượt
    visibility_value = getattr(draw_po_visibility_selection, 'visibility_value', 50)
    draw_po_visibility_selection.visibility_value = visibility_value
    
    slider_position = slider_rect.x + int((visibility_value / 100) * slider_width)
    handle_rect = pygame.Rect(slider_position - 7, slider_rect.y - 11, 14, 30)
    glow_intensity = int(127 + 128 * math.sin(pygame.time.get_ticks() * 0.004))
    glow_color = (glow_intensity, glow_intensity//2, 0)
    
    pygame.draw.rect(screen, GOLD_DARK, handle_rect, border_radius=7)
    pygame.draw.rect(screen, glow_color, handle_rect, 2, border_radius=7)
    
    # Hiển thị giá trị
    value_text = button_font.render(f"{visibility_value}%", True, GOLD_LIGHT)
    screen.blit(value_text, (panel_rect.centerx - value_text.get_width()//2, slider_rect.y + 30))
    
    # Nút xác nhận và hủy
    confirm_button = pygame.Rect(panel_rect.centerx - 140, panel_rect.y + 200, 120, 50)
    cancel_button = pygame.Rect(panel_rect.centerx + 20, panel_rect.y + 200, 120, 50)
    
    confirm_hovered = draw_beautiful_button(confirm_button, "CONFIRM", font, base_color=(50, 150, 50))
    cancel_hovered = draw_beautiful_button(cancel_button, "CANCEL", font, base_color=(150, 50, 50))
    
    # Thêm tùy chọn sương mù
    fog_enabled = getattr(draw_po_visibility_selection, 'fog_enabled', True)
    draw_po_visibility_selection.fog_enabled = fog_enabled
    
    fog_checkbox_rect = pygame.Rect(panel_rect.centerx - 100, panel_rect.y + 170, 20, 20)
    pygame.draw.rect(screen, (60, 60, 70), fog_checkbox_rect, border_radius=3)
    if fog_enabled:
        pygame.draw.rect(screen, GOLD_LIGHT, fog_checkbox_rect, border_radius=3)
    pygame.draw.rect(screen, WHITE, fog_checkbox_rect, 1, border_radius=3)
    
    fog_text = font.render("Enable fog of war", True, WHITE)
    screen.blit(fog_text, (panel_rect.centerx - 70, panel_rect.y + 170))
    
    pygame.display.flip()
    return slider_rect, handle_rect, confirm_button, cancel_button, fog_checkbox_rect, visibility_value, fog_enabled
# BÙI PHÚC NHÂN
# Min-Conflicts Algorithm - Constraint Satisfaction Problems
def min_conflicts_algorithm(maze, player_pos, princess_pos, target_pos, visible, knowledge=None):
    if knowledge is None:
        knowledge = {
            "maze": [[None for _ in range(COLS)] for _ in range(ROWS)],
            "visited": set(),
            "deadends": set(),
            "conflicts": {},
            "princess_found": False,
            "exit_found": False,
            "princess_pos": None,
            "exit_pos": None,
            "princess_rescued": False
        }
    
    # Cập nhật kiến thức về bản đồ dựa trên vùng nhìn thấy
    for row in range(ROWS):
        for col in range(COLS):
            if visible[row][col]:
                knowledge["maze"][row][col] = maze[row][col]
                if maze[row][col] == 2: # Tìm thấy công chúa
                    knowledge["princess_found"] = True
                    knowledge["princess_pos"] = (row, col)
                elif maze[row][col] == 3: # Tìm thấy cổng thoát
                    knowledge["exit_found"] = True
                    knowledge["exit_pos"] = (row, col)

    # Kiểm tra nếu đã cứu công chúa
    if player_pos == princess_pos and not knowledge["princess_rescued"]:
        knowledge["princess_rescued"] = True

    # Đánh dấu ô hiện tại đã được thăm
    knowledge["visited"].add(player_pos)
    
    neighbors = []
    knowledge["conflicts"] = {} # Reset conflicts cho mỗi bước để tính toán lại

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # Các hướng di chuyển có thể
        new_pos = (player_pos[0] + dx, player_pos[1] + dy)
        
        # Kiểm tra xem ô mới có nằm trong bản đồ và không phải là tường đã biết
        if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and \
           (knowledge["maze"][new_pos[0]][new_pos[1]] is None or knowledge["maze"][new_pos[0]][new_pos[1]] != 1):
            
            neighbors.append(new_pos)
            conflicts = 0

            # Xung đột nếu ô đã được thăm
            if new_pos in knowledge["visited"]:
                conflicts += 10

            # Xung đột lớn nếu ô là ngõ cụt
            if new_pos in knowledge["deadends"]:
                conflicts += 50
            
            # Giảm xung đột nếu ô gần công chúa hơn (nếu đã tìm thấy và chưa cứu)
            if knowledge["princess_found"] and not knowledge["princess_rescued"] and knowledge["princess_pos"]:
                dist_to_princess = manhattan_distance(new_pos, knowledge["princess_pos"])
                # Càng gần công chúa, điểm trừ càng lớn (xung đột càng thấp)
                conflicts -= 20 * (1 / (dist_to_princess + 1)) 
            
            # Giảm xung đột nếu ô gần cổng thoát hơn (nếu đã cứu công chúa và tìm thấy cổng)
            if knowledge["princess_rescued"] and knowledge["exit_found"] and knowledge["exit_pos"]:
                dist_to_exit = manhattan_distance(new_pos, knowledge["exit_pos"])
                # Càng gần cổng thoát, điểm trừ càng lớn
                conflicts -= 20 * (1 / (dist_to_exit + 1)) 
            
            knowledge["conflicts"][new_pos] = conflicts
    
    next_move = None

    # Chọn bước đi có xung đột thấp nhất
    if neighbors:
        # Sắp xếp các ô lân cận theo điểm xung đột tăng dần
        # Ưu tiên các ô chưa được thăm nếu điểm xung đột bằng nhau
        sorted_neighbors = sorted(neighbors, key=lambda pos: (knowledge["conflicts"].get(pos, float('inf')), pos in knowledge["visited"]))
        if sorted_neighbors:
            next_move = sorted_neighbors[0]

    # Đánh dấu ngõ cụt: nếu chỉ có một lối đi và đó không phải là mục tiêu
    # và vị trí hiện tại không phải là mục tiêu
    if len(neighbors) == 1 and next_move:
        is_current_goal = False
        if knowledge["princess_found"] and not knowledge["princess_rescued"] and player_pos == knowledge["princess_pos"]:
            is_current_goal = True
        if knowledge["princess_rescued"] and knowledge["exit_found"] and player_pos == knowledge["exit_pos"]:
            is_current_goal = True
        
        if not is_current_goal:
             # Nếu lối đi duy nhất là quay lại ô vừa đi qua, và ô đó không phải mục tiêu
            if len(knowledge["visited"]) > 1 and neighbors[0] in knowledge["visited"]:
                 # Kiểm tra xem có phải đang bị kẹt giữa 2 ô không
                is_stuck = True
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    check_pos = (player_pos[0] + dx, player_pos[1] + dy)
                    if 0 <= check_pos[0] < ROWS and 0 <= check_pos[1] < COLS and \
                       (knowledge["maze"][check_pos[0]][check_pos[1]] is None or \
                        knowledge["maze"][check_pos[0]][check_pos[1]] != 1) and \
                       check_pos not in knowledge["deadends"] and check_pos != neighbors[0]:
                        is_stuck = False
                        break
                if is_stuck:
                    knowledge["deadends"].add(player_pos)


    # Nếu không có bước đi nào được chọn (ví dụ: bị chặn hoàn toàn hoặc lỗi logic)
    if next_move is None:
        if neighbors: # Nếu vẫn còn ô lân cận, chọn đại một ô
            next_move = random.choice(neighbors)
        else: # Không còn đường đi, đứng yên
            next_move = player_pos
    
    return next_move, knowledge

# Q-Learning Algorithm - Reinforcement Learning
def q_learning_algorithm(maze, player_pos, princess_pos, target_pos, visible, knowledge=None):
    if knowledge is None:
        knowledge = {
            "q_table": {},
            "maze": [[None for _ in range(COLS)] for _ in range(ROWS)], # Bản đồ AI biết
            "visited_in_episode": set(), # Các ô đã thăm trong lượt chơi này (để tính reward khám phá)
            "princess_found": False,
            "exit_found": False,
            "princess_pos": None,
            "exit_pos": None,
            "princess_rescued": False,
            "last_state": None,
            "last_action": None,
            "previous_player_pos": None, # Theo dõi vị trí ngay trước đó
            "learning_rate": 0.1,      # Alpha
            "discount_factor": 0.9,    # Gamma
            "max_exploration_rate": 0.8, 
            "min_exploration_rate": 0.01,
            "exploration_decay_rate": 0.998, # Tốc độ giảm epsilon
        }
        knowledge["exploration_rate"] = knowledge["max_exploration_rate"]


    # Cập nhật kiến thức về bản đồ dựa trên vùng nhìn thấy
    for row in range(ROWS):
        for col in range(COLS):
            if visible[row][col]:
                knowledge["maze"][row][col] = maze[row][col]
                if maze[row][col] == 2: # Tìm thấy công chúa
                    knowledge["princess_found"] = True
                    knowledge["princess_pos"] = (row, col)
                elif maze[row][col] == 3: # Tìm thấy cổng thoát
                    knowledge["exit_found"] = True
                    knowledge["exit_pos"] = (row, col)
    
    # Kiểm tra nếu đã cứu công chúa
    just_rescued_princess = False
    if player_pos == knowledge.get("princess_pos") and knowledge["princess_found"] and not knowledge["princess_rescued"]:
        knowledge["princess_rescued"] = True
        just_rescued_princess = True
        knowledge["visited_in_episode"] = set() # QUAN TRỌNG: Reset để khuyến khích tìm đường ra mới

    # Trạng thái hiện tại
    current_state = (player_pos, knowledge["princess_rescued"], knowledge["princess_found"], knowledge["exit_found"])

    # Cập nhật Q-value từ bước trước (nếu có)
    if knowledge["last_state"] is not None and knowledge["last_action"] is not None:
        reward = 0
        
        if just_rescued_princess:
            reward += 200 # Phần thưởng lớn khi vừa cứu công chúa
        
        if knowledge["princess_rescued"] and player_pos == knowledge.get("exit_pos") and knowledge["exit_found"]:
            reward += 300 # Phần thưởng lớn khi đến cổng thoát

        if 0 <= player_pos[0] < ROWS and 0 <= player_pos[1] < COLS:
            if knowledge["maze"][player_pos[0]][player_pos[1]] == 1: # Đi vào tường
                 reward -= 100 
        
        if player_pos not in knowledge["visited_in_episode"]:
            reward += 10 # Phần thưởng khám phá ô mới
        else:
            reward -= 3 # Phạt đi lại ô đã thăm trong episode này
        
        # Phạt nặng hơn nếu quay lại ô ngay trước đó
        if knowledge.get("previous_player_pos") and player_pos == knowledge["previous_player_pos"]:
            reward -= 25 

        # Phần thưởng/Phạt khi tiến gần/xa mục tiêu (TĂNG CƯỜNG)
        if not knowledge["princess_rescued"] and knowledge["princess_found"] and knowledge["princess_pos"]:
            dist_now = manhattan_distance(player_pos, knowledge["princess_pos"])
            if knowledge["last_state"] and isinstance(knowledge["last_state"], tuple) and len(knowledge["last_state"]) > 0 and \
               isinstance(knowledge["last_state"][0], tuple) and len(knowledge["last_state"][0]) == 2:
                 prev_pos_for_dist_calc = knowledge["last_state"][0]
                 dist_prev = manhattan_distance(prev_pos_for_dist_calc, knowledge["princess_pos"])
                 if dist_now < dist_prev: reward += 15 # Tăng phần thưởng
                 elif dist_now > dist_prev: reward -= 15 # Tăng hình phạt
        elif knowledge["princess_rescued"] and knowledge["exit_found"] and knowledge["exit_pos"]:
            dist_now = manhattan_distance(player_pos, knowledge["exit_pos"])
            if knowledge["last_state"] and isinstance(knowledge["last_state"], tuple) and len(knowledge["last_state"]) > 0 and \
               isinstance(knowledge["last_state"][0], tuple) and len(knowledge["last_state"][0]) == 2:
                prev_pos_for_dist_calc = knowledge["last_state"][0]
                dist_prev = manhattan_distance(prev_pos_for_dist_calc, knowledge["exit_pos"])
                if dist_now < dist_prev: reward += 15 # Tăng phần thưởng
                elif dist_now > dist_prev: reward -= 15 # Tăng hình phạt

        if knowledge["last_state"] not in knowledge["q_table"]:
            knowledge["q_table"][knowledge["last_state"]] = {}
        if knowledge["last_action"] not in knowledge["q_table"][knowledge["last_state"]]:
            knowledge["q_table"][knowledge["last_state"]][knowledge["last_action"]] = 0

        max_future_q = 0
        if current_state in knowledge["q_table"] and knowledge["q_table"][current_state]:
            max_future_q = max(knowledge["q_table"][current_state].values())
        
        old_q_value = knowledge["q_table"][knowledge["last_state"]][knowledge["last_action"]]
        knowledge["q_table"][knowledge["last_state"]][knowledge["last_action"]] = old_q_value + \
            knowledge["learning_rate"] * (reward + knowledge["discount_factor"] * max_future_q - old_q_value)

    knowledge["visited_in_episode"].add(player_pos) # Thêm vị trí hiện tại vào tập đã thăm của episode này

    possible_actions = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_pos = (player_pos[0] + dx, player_pos[1] + dy)
        if 0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and \
           (knowledge["maze"][new_pos[0]][new_pos[1]] is None or knowledge["maze"][new_pos[0]][new_pos[1]] != 1):
            possible_actions.append(new_pos)
    
    next_move = None

    if possible_actions:
        if current_state not in knowledge["q_table"]:
            knowledge["q_table"][current_state] = {}

        if random.random() < knowledge["exploration_rate"]:
            # Thăm dò: cố gắng không quay lại ô trước đó nếu có lựa chọn khác
            non_previous_actions = [a for a in possible_actions if a != knowledge.get("previous_player_pos")]
            if non_previous_actions:
                next_move = random.choice(non_previous_actions)
            else: # Nếu tất cả các hành động đều là quay lại (ví dụ: ngõ cụt)
                next_move = random.choice(possible_actions)
        else:
            # Khai thác: chọn hành động có Q-value cao nhất
            best_q_value = float('-inf')
            candidate_actions = [] # Các hành động có Q-value cao nhất
            
            for action in possible_actions:
                q_value = knowledge["q_table"][current_state].get(action, 0)
                if q_value > best_q_value:
                    best_q_value = q_value
                    candidate_actions = [action]
                elif q_value == best_q_value:
                    candidate_actions.append(action)
            
            if candidate_actions:
                # Từ các ứng viên tốt nhất, cố gắng chọn một hành động không phải là quay lui
                preferred_actions = [a for a in candidate_actions if a != knowledge.get("previous_player_pos")]
                if preferred_actions:
                    next_move = random.choice(preferred_actions)
                else: # Tất cả các hành động tốt nhất đều là quay lui, hoặc chỉ có một hành động tốt nhất là quay lui
                    next_move = random.choice(candidate_actions) 
            else: # Fallback nếu không có candidate_actions (không nên xảy ra nếu possible_actions có phần tử)
                non_previous_actions = [a for a in possible_actions if a != knowledge.get("previous_player_pos")]
                if non_previous_actions:
                    next_move = random.choice(non_previous_actions)
                else:
                    next_move = random.choice(possible_actions)
    
    if next_move is None: 
        if possible_actions:
             next_move = random.choice(possible_actions) 
        else:
            next_move = player_pos # Đứng yên nếu bị kẹt hoàn toàn

    knowledge["previous_player_pos"] = player_pos # Lưu vị trí hiện tại làm vị trí trước đó cho lần gọi sau
    
    knowledge["last_state"] = current_state
    knowledge["last_action"] = next_move 

    knowledge["exploration_rate"] = max(knowledge["min_exploration_rate"], 
                                        knowledge["exploration_rate"] * knowledge["exploration_decay_rate"])
    
    return next_move, knowledge

def draw_ai_scoreboard(algorithm, steps):
    panel_width = 300
    panel_height = 120
    x = (WIDTH - panel_width) // 2
    y = (HEIGHT - panel_height) // 2
    scoreboard_panel = pygame.Rect(x, y, panel_width, panel_height)
    pygame.draw.rect(screen, PANEL_COLOR, scoreboard_panel, border_radius=10)
    pygame.draw.rect(screen, GOLD_DARK, scoreboard_panel, 2, border_radius=10)
    
    texts = [
        (f"AI: {algorithm}", GOLD_LIGHT, 20),
        (f"Steps: {steps}", WHITE, 60)
    ]
    for text, color, y_offset in texts:
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x + 20, y + y_offset))

def draw_ai_victory_screen(algorithm, steps, time, map_name, difficulty, rescued):
    screen.blit(background_img, (0, 0))
    draw_animated_title("AI RESULT", HEIGHT//5)
    panel_rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 200, 600, 400)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=15)
    glow_time = pygame.time.get_ticks() * 0.001
    glow_intensity = int(127 + 128 * math.sin(glow_time))
    glow_color = (glow_intensity, glow_intensity//2, 0)
    pygame.draw.rect(screen, glow_color, panel_rect, 3, border_radius=15)
    current_game_title = font.render("AI RESULT", True, GOLD_LIGHT)
    map_name_text = font.render(f"Map: {map_name}", True, WHITE)
    algo_text = font.render(f"Algorithm: {algorithm}", True, WHITE)
    diff_text = font.render(f"Difficulty: {difficulty}", True, WHITE)
    rescued_text = font.render(f"Rescued: {'Yes' if rescued else 'No'}", True, GOLD_LIGHT if rescued else (255,50,50))
    score_text = font.render(f"Steps: {steps}", True, WHITE)
    time_text = font.render(f"Time: {time}s", True, WHITE)
    restart_text = font.render("Press SPACE to Restart", True, GOLD_LIGHT)
    y = panel_rect.y + 20
    for t in [current_game_title, map_name_text, algo_text, diff_text, rescued_text, score_text, time_text]:
        screen.blit(t, (panel_rect.centerx - t.get_width()//2, y))
        y += 40
    screen.blit(restart_text, (panel_rect.centerx - restart_text.get_width()//2, panel_rect.bottom - 40))
    pygame.display.flip()

def draw_ai_stats_screen():
    screen.blit(background_img, (0, 0))

    draw_animated_title("AI Statistics", HEIGHT//5)

    panel_rect = pygame.Rect(WIDTH//2 - 480, HEIGHT//2 - 250, 960, 500)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=15)
    glow_time = pygame.time.get_ticks() * 0.001
    glow_intensity = int(127 + 128 * math.sin(glow_time))
    glow_color = (glow_intensity, glow_intensity//2, 0)
    pygame.draw.rect(screen, glow_color, panel_rect, 4, border_radius=15)

    ai_score_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_score.txt")
    ai_stats = []
    unique_entries = set()

    if os.path.exists(ai_score_file):
        with open(ai_score_file, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 6:
                    map_name, algo, diff, steps, time, rescued = parts

                    entry_id = f"{map_name},{algo},{diff},{rescued}"
                    if entry_id in unique_entries:
                        continue
                    unique_entries.add(entry_id)
                    ai_stats.append({
                        "map": map_name,
                        "algo": algo,
                        "steps": int(steps),
                        "time": int(time),
                        "rescued": rescued == "1"
                    })

                    ai_stats.sort(key=lambda x: (x["steps"], x["time"]))
    
    def sort_key(x):
        return (x["algo"], x["map"])
    
    ai_stats.sort(key=sort_key)

    stats_title = button_font.render("AI PERFORMANCE", True, GOLD_LIGHT)
    screen.blit(stats_title, (panel_rect.centerx - stats_title.get_width()//2, panel_rect.y + 25))

    table_container = pygame.Rect(panel_rect.x + 30, panel_rect.y + 80, panel_rect.width - 60, 340)
    pygame.draw.rect(screen, (25, 25, 30), table_container, border_radius=10)
    pygame.draw.rect(screen, GOLD_DARK, table_container, 2, border_radius=10)

    header_bg = pygame.Rect(table_container.x + 10, table_container.y + 10, table_container.width - 20, 50)
    pygame.draw.rect(screen, (60, 60, 80), header_bg, border_radius=7)
    pygame.draw.rect(screen, GOLD_DARK, header_bg, 1, border_radius=7)

    column_widths = [280, 250, 100, 100, 120]
    column_names = ["Map", "Algorithm", "Steps", "Time", "Rescued"]
    header_x = header_bg.x + 20
    
    for i, (name, width) in enumerate(zip(column_names, column_widths)):
        header_text = font.render(name, True, GOLD_LIGHT)
        screen.blit(header_text, (header_x, header_bg.y + 18))
        header_x += width

    max_visible = 5
    scroll_offset = min(len(ai_stats) - max_visible, max(0, getattr(draw_ai_stats_screen, 'scroll_offset', 0)))
    draw_ai_stats_screen.scroll_offset = scroll_offset

    visible_stats = ai_stats[scroll_offset:scroll_offset + max_visible]
    for i, stat in enumerate(visible_stats):
        row_bg = pygame.Rect(table_container.x + 10, table_container.y + 65 + i * 52, 
                           table_container.width - 20, 48)
        pygame.draw.rect(screen, (45, 45, 55) if i % 2 == 0 else (35, 35, 45), row_bg, border_radius=7)
        pygame.draw.rect(screen, (60, 60, 70), row_bg, 1, border_radius=7)

        rescued_rect = pygame.Rect(row_bg.right - 60, row_bg.y + 9, 30, 30)
        if stat["rescued"]:
            pygame.draw.rect(screen, (0, 150, 0), rescued_rect, border_radius=5)
            check = font.render("V", True, WHITE)
            screen.blit(check, (rescued_rect.x + 8, rescued_rect.y + 5))
        else:
            pygame.draw.rect(screen, (150, 0, 0), rescued_rect, border_radius=5)
            x_mark = font.render("X", True, WHITE)
            screen.blit(x_mark, (rescued_rect.x + 8, rescued_rect.y + 5))

        col_x = row_bg.x + 20
        col_data = [stat["map"], stat["algo"], str(stat["steps"]), str(stat["time"])]
        
        for j, (data, width) in enumerate(zip(col_data, column_widths[:-1])):
            text = font.render(data, True, WHITE)
            screen.blit(text, (col_x, row_bg.y + 16))
            col_x += width

    if len(ai_stats) > max_visible:
        scrollbar_bg = pygame.Rect(table_container.right - 25, table_container.y + 65, 
                                 18, table_container.height - 75)
        pygame.draw.rect(screen, (60, 60, 70), scrollbar_bg, border_radius=9)
        
        thumb_height = max(30, int(max_visible / len(ai_stats) * scrollbar_bg.height))
        max_scroll = len(ai_stats) - max_visible
        scroll_progress = scroll_offset / max_scroll if max_scroll > 0 else 0
        thumb_pos = scrollbar_bg.y + (scrollbar_bg.height - thumb_height) * scroll_progress
        
        thumb = pygame.Rect(scrollbar_bg.x, thumb_pos, scrollbar_bg.width, thumb_height)
        pygame.draw.rect(screen, GOLD_DARK, thumb, border_radius=9)
        
        glow_intensity = int(127 + 128 * math.sin(pygame.time.get_ticks() * 0.002))
        pygame.draw.rect(screen, (glow_intensity, glow_intensity//2, 0), thumb, 2, border_radius=9)
    
    back_button = pygame.Rect(panel_rect.centerx - 100, panel_rect.bottom - 60, 200, 50)
    draw_beautiful_button(back_button, "BACK", button_font)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN] and scroll_offset < len(ai_stats) - max_visible:
        draw_ai_stats_screen.scroll_offset = scroll_offset + 1
    if keys[pygame.K_UP] and scroll_offset > 0:
        draw_ai_stats_screen.scroll_offset = scroll_offset - 1

    pygame.display.flip()
    return back_button

def draw_end_screen(result, score, time, scoreboard, map_name):
    screen.blit(background_img, (0, 0))

    draw_animated_title(result, HEIGHT//5)

    panel_rect = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 230, 700, 460)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=15)
    glow_time = pygame.time.get_ticks() * 0.001
    glow_intensity = int(127 + 128 * math.sin(glow_time))
    glow_color = (glow_intensity, glow_intensity//2, 0)
    pygame.draw.rect(screen, glow_color, panel_rect, 4, border_radius=15)

    current_game_title = font.render("YOUR RESULT", True, GOLD_LIGHT)
    map_name_text = font.render(f"Map: {map_name}", True, WHITE)
    score_text = font.render(f"Steps: {score}", True, WHITE)
    time_text = font.render(f"Time: {time}s", True, WHITE)
    restart_text = font.render("Press SPACE to Restart", True, GOLD_LIGHT)

    screen.blit(current_game_title, (panel_rect.centerx - current_game_title.get_width()//2, panel_rect.y + 25))
    screen.blit(map_name_text, (panel_rect.centerx - map_name_text.get_width()//2, panel_rect.y + 65))
    screen.blit(score_text, (panel_rect.centerx - score_text.get_width()//2, panel_rect.y + 95))
    screen.blit(time_text, (panel_rect.centerx - time_text.get_width()//2, panel_rect.y + 125))

    sb_title = button_font.render("LEADERBOARD", True, GOLD_LIGHT)
    screen.blit(sb_title, (panel_rect.centerx - sb_title.get_width()//2, panel_rect.y + 170))

    leaderboard_container = pygame.Rect(panel_rect.x + 30, panel_rect.y + 215, panel_rect.width - 60, 180)
    pygame.draw.rect(screen, (25, 25, 30), leaderboard_container, border_radius=10)
    pygame.draw.rect(screen, GOLD_DARK, leaderboard_container, 2, border_radius=10)

    valid_scores = [x for x in scoreboard if x[0].strip()]
    try:
        sorted_scores = sorted(valid_scores, key=lambda x: (0 if len(x) > 2 and x[2] == "1" else 1, int(x[0])))
    except (ValueError, IndexError):
        sorted_scores = []

    max_visible = 3
    scroll_offset = min(len(sorted_scores) - max_visible, max(0, getattr(draw_end_screen, 'scroll_offset', 0)))
    draw_end_screen.scroll_offset = scroll_offset

    visible_scores = sorted_scores[scroll_offset:scroll_offset + max_visible]
    for i, score_entry in enumerate(visible_scores):
        s, t = score_entry[0], score_entry[1]
        rescued = "Yes" if len(score_entry) > 2 and score_entry[2] == "1" else "No"
        rescued_color = GOLD_LIGHT if rescued == "Yes" else (200, 50, 50)
        
        # Thêm thông tin map và độ khó
        score_map = score_entry[3] if len(score_entry) > 3 else "Unknown"
        difficulty = score_entry[4] if len(score_entry) > 4 else "EASY"
        diff_color = GOLD_LIGHT if difficulty == "HARD" else (100, 255, 100)

        entry_bg = pygame.Rect(leaderboard_container.x + 10, leaderboard_container.y + 10 + i * 55, 
                              leaderboard_container.width - 40, 50)
        pygame.draw.rect(screen, (45, 45, 55) if i % 2 == 0 else (35, 35, 45), entry_bg, border_radius=7)
        pygame.draw.rect(screen, (60, 60, 70), entry_bg, 1, border_radius=7)

        # Icon hiển thị trạng thái cứu công chúa
        icon_rect = pygame.Rect(entry_bg.x + 10, entry_bg.y + 10, 30, 30)
        if rescued == "Yes":
            pygame.draw.rect(screen, (0, 150, 0), icon_rect, border_radius=5)
            check = button_font.render("V", True, WHITE)
            screen.blit(check, (icon_rect.x + 8, icon_rect.y + 2))
        else:
            pygame.draw.rect(screen, (150, 0, 0), icon_rect, border_radius=5)
            x_mark = button_font.render("X", True, WHITE)
            screen.blit(x_mark, (icon_rect.x + 8, icon_rect.y + 2))

        # Vị trí trong bảng
        pos_text = font.render(f"{i + scroll_offset + 1}.", True, WHITE)
        screen.blit(pos_text, (entry_bg.x + 50, entry_bg.y + 8))

        # Map và độ khó
        map_text = font.render(score_map, True, WHITE)
        screen.blit(map_text, (entry_bg.x + 70, entry_bg.y + 8))

        # Độ khó
        diff_text = font.render(difficulty, True, diff_color)
        screen.blit(diff_text, (entry_bg.x + 70, entry_bg.y + 28))

        # Số bước và thời gian
        steps_text = font.render(f"Steps: {s}", True, WHITE)
        screen.blit(steps_text, (entry_bg.x + 280, entry_bg.y + 8))

        time_text = font.render(f"Time: {t}s", True, WHITE)
        screen.blit(time_text, (entry_bg.x + 280, entry_bg.y + 28))

    if len(sorted_scores) > max_visible:
        scrollbar_bg = pygame.Rect(leaderboard_container.right - 25, leaderboard_container.y + 5, 
                                 18, leaderboard_container.height - 10)
        pygame.draw.rect(screen, (60, 60, 70), scrollbar_bg, border_radius=9)

        thumb_height = max(30, int(max_visible / len(sorted_scores) * scrollbar_bg.height))
        max_scroll = len(sorted_scores) - max_visible
        scroll_progress = scroll_offset / max_scroll if max_scroll > 0 else 0
        thumb_pos = scrollbar_bg.y + (scrollbar_bg.height - thumb_height) * scroll_progress
        
        thumb = pygame.Rect(scrollbar_bg.x, thumb_pos, scrollbar_bg.width, thumb_height)
        pygame.draw.rect(screen, GOLD_DARK, thumb, border_radius=9)

        glow_intensity = int(127 + 128 * math.sin(pygame.time.get_ticks() * 0.002))
        pygame.draw.rect(screen, (glow_intensity, glow_intensity//2, 0), thumb, 2, border_radius=9)

    screen.blit(restart_text, (panel_rect.centerx - restart_text.get_width()//2, panel_rect.bottom - 40))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN] and scroll_offset < len(sorted_scores) - max_visible:
        draw_end_screen.scroll_offset = scroll_offset + 1
    if keys[pygame.K_UP] and scroll_offset > 0:
        draw_end_screen.scroll_offset = scroll_offset - 1

    pygame.display.flip()

def draw_game_tutorial():
    screen.blit(background_img, (0, 0))
    draw_animated_title("Game Tutorial", 50)
    instructions = [
        "Goal: Find the princess and bring her to the exit gate",
        "Movement: Use the arrow keys to move",
        "Princess: Find and touch her to rescue",
        "Ghost: Appears after 20 steps",
        "Ghost will chase you or the princess after rescue",
        "Ghost speed increases every 20 seconds",
        "Win by bringing the princess safely to the exit gate"
    ]
    panel_rect = pygame.Rect(WIDTH//2 - 350, 130, 700, 400)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=15)
    pygame.draw.rect(screen, GOLD_DARK, panel_rect, 3, border_radius=15)
    y_pos = 170
    for i, line in enumerate(instructions):
        text = font.render(line, True, WHITE)
        shadow = font.render(line, True, TEXT_SHADOW)
        offset = math.sin(pygame.time.get_ticks() * 0.001 + i * 0.5) * 3
        screen.blit(shadow, (WIDTH//2 - text.get_width()//2 + 2, y_pos + 2 + offset))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos + offset))
        y_pos += 50
    back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
    draw_beautiful_button(back_button, "BACK", button_font)
    pygame.display.flip()
    return back_button

def create_map_editor(existing_map=None, map_name=None):
    """Tính năng tạo map bằng cách kéo thả."""
    global WIDTH, HEIGHT, screen, maps
    old_width, old_height = WIDTH, HEIGHT
    WIDTH, HEIGHT = 1200, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Khởi tạo biến
    map_size = 16
    
    # Nếu có map hiện có, sử dụng nó. Nếu không, tạo map mới
    if existing_map:
        editing_map = [row[:] for row in existing_map]  # Copy map hiện có
        original_map = [row[:] for row in existing_map]  # Lưu bản sao để so sánh thay đổi
    else:
        editing_map = [[0 for _ in range(map_size)] for _ in range(map_size)]
        original_map = [[0 for _ in range(map_size)] for _ in range(map_size)]
    
    # Biến để kiểm tra xem map đã được thay đổi chưa
    map_changed = False

    EDITOR_SIZE = 600
    EDITOR_X = 50
    EDITOR_Y = 100
    CELL_SIZE_EDITOR = EDITOR_SIZE // map_size
    
    # Công cụ và mô tả
    tools = {
        "Wall": wall_img,
        "Princess": princess_img,
        "Exit": pygame.Surface((CELL_SIZE, CELL_SIZE))
    }
    tools["Exit"].fill((0, 255, 0))

    tool_descriptions = {
        "Wall": "Tạo tường chắn đường đi",
        "Princess": "Đặt vị trí công chúa (chỉ 1)",
        "Exit": "Đặt cổng thoát (chỉ 1)"
    }

    selected_tool = None
    running = True
    input_active = False
    input_text = map_name if map_name else ""
    error_message = ""
    error_time = 0
    created_map = None
    
    # Biến theo dõi thời gian double click
    last_click_time = 0
    last_click_pos = None
    double_click_delay = 300  # milliseconds

    while running:
        screen.fill((30, 30, 40))

        # Vẽ tiêu đề
        mode_title = "Edit Map: " + map_name if map_name else "Create New Map"
        draw_animated_title(mode_title, 30)

        # Vẽ khung chứa map
        editor_rect = pygame.Rect(EDITOR_X-10, EDITOR_Y-10, 
                                EDITOR_SIZE+20, EDITOR_SIZE+20)
        pygame.draw.rect(screen, (50, 50, 60), editor_rect, border_radius=15)
        pygame.draw.rect(screen, GOLD_DARK, editor_rect, 3, border_radius=15)

        # Vẽ lưới và map
        for row in range(map_size):
            for col in range(map_size):
                x = EDITOR_X + col * CELL_SIZE_EDITOR
                y = EDITOR_Y + row * CELL_SIZE_EDITOR
                cell_rect = pygame.Rect(x, y, CELL_SIZE_EDITOR, CELL_SIZE_EDITOR)

                if editing_map[row][col] == 0:
                    screen.blit(pygame.transform.scale(floor_img, (CELL_SIZE_EDITOR, CELL_SIZE_EDITOR)), (x, y))
                elif editing_map[row][col] == 1:
                    screen.blit(pygame.transform.scale(wall_img, (CELL_SIZE_EDITOR, CELL_SIZE_EDITOR)), (x, y))
                elif editing_map[row][col] == 2:
                    screen.blit(pygame.transform.scale(princess_img, (CELL_SIZE_EDITOR, CELL_SIZE_EDITOR)), (x, y))
                elif editing_map[row][col] == 3:
                    pygame.draw.rect(screen, (0, 255, 0), cell_rect)

                pygame.draw.rect(screen, GRAY, cell_rect, 1)

        panel_rect = pygame.Rect(WIDTH - 300, 50, 250, HEIGHT - 100)
        gradient_rect(screen, panel_rect, (40,40,50), (30,30,35))
        pygame.draw.rect(screen, GOLD_DARK, panel_rect, 2, border_radius=10)

        panel_title = font.render("Tools", True, GOLD_LIGHT)
        screen.blit(panel_title, (panel_rect.centerx - panel_title.get_width()//2, 70))

        # Vẽ hướng dẫn double click
        hint_text = font.render("Double click to clear a cell", True, WHITE)
        screen.blit(hint_text, (panel_rect.centerx - hint_text.get_width()//2, panel_rect.bottom - 220))

        spacing = 60
        start_y = 120
        for i, (tool_name, tool_img) in enumerate(tools.items()):
            tool_rect = pygame.Rect(WIDTH - 270, start_y + i * (CELL_SIZE*2 + spacing), CELL_SIZE*2, CELL_SIZE*2)
            tool_bg = pygame.Rect(tool_rect.x-5, tool_rect.y-5, tool_rect.width+10, tool_rect.height+10)
            if selected_tool == tool_name:
                pygame.draw.rect(screen, GOLD_LIGHT, tool_bg, border_radius=10)
            pygame.draw.rect(screen, (50,50,60), tool_bg, 2, border_radius=10)
            screen.blit(pygame.transform.scale(tool_img, (CELL_SIZE*2, CELL_SIZE*2)), tool_rect)
            name_text = font.render(tool_name, True, WHITE)
            screen.blit(name_text, (tool_rect.right + 20, tool_rect.centery - name_text.get_height()//2))

        buttons = [
            ("SAVE", (WIDTH - 270, HEIGHT-160)),
            ("BACK", (WIDTH - 270, HEIGHT-90))
        ]
        for text, pos in buttons:
            button = pygame.Rect(pos[0], pos[1], 220, 60)
            draw_beautiful_button(button, text, button_font)

        # Hiển thị thông báo lỗi
        if error_message and pygame.time.get_ticks() - error_time < 3000:
            error_rect = pygame.Rect(WIDTH//2 - 200, 50, 400, 40)
            pygame.draw.rect(screen, (200, 50, 50), error_rect, border_radius=10)
            error_text = font.render(error_message, True, WHITE)
            screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, 60))

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Hiển thị cảnh báo nếu có thay đổi chưa lưu
                if map_changed:
                    confirmation = show_unsaved_changes_warning()
                    if confirmation == "SAVE":
                        # Lưu thay đổi trước khi thoát
                        if map_name:
                            success = save_map_to_file(editing_map, map_name, overwrite=True)
                            if success:
                                maps[map_name] = editing_map.copy()
                                created_map = editing_map.copy()
                        else:
                            # Yêu cầu đặt tên trước khi lưu
                            input_active = True
                            continue
                    elif confirmation == "CANCEL":
                        continue
                pygame.quit()
                sys.exit()

            if input_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ok_button = pygame.Rect(dialog_rect.centerx - 110,
                                        dialog_rect.y + dialog_height - 60, 100, 40)
                    cancel_button = pygame.Rect(dialog_rect.centerx + 10,
                                            dialog_rect.y + dialog_height - 60, 100, 40)
                    
                    if ok_button.collidepoint(event.pos):
                        button_sound.play()
                        if input_text.strip():
                            if not any(2 in row for row in editing_map) or not any(3 in row for row in editing_map):
                                error_message = "Map phải có cả công chúa và cổng thoát!"
                                error_time = pygame.time.get_ticks()
                            else:
                                success = save_map_to_file(editing_map, input_text)
                                if success:
                                    maps[input_text] = editing_map.copy()
                                    created_map = editing_map.copy()
                                    running = False
                                else:
                                    error_message = "Lỗi khi lưu map!"
                                    error_time = pygame.time.get_ticks()
                        input_active = False
                        
                    elif cancel_button.collidepoint(event.pos):
                        button_sound.play()
                        input_active = False
                        input_text = map_name if map_name else ""
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip():
                            if not any(2 in row for row in editing_map) or not any(3 in row for row in editing_map):
                                error_message = "Map phải có cả công chúa và cổng thoát!"
                                error_time = pygame.time.get_ticks()
                                input_active = False
                            else:
                                success = save_map_to_file(editing_map, input_text)
                                if success:
                                    maps[input_text] = editing_map.copy()
                                    created_map = editing_map.copy()
                                    running = False
                                else:
                                    error_message = "Lỗi khi lưu map!"
                                    error_time = pygame.time.get_ticks()
                                input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        input_active = False
                    else:
                        if len(input_text) < 20:  # Giới hạn độ dài tên
                            input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                current_time = pygame.time.get_ticks()

                # Xử lý click vào công cụ
                spacing = 60
                start_y = 120
                for i, (tool_name, tool_img) in enumerate(tools.items()):
                    tool_rect = pygame.Rect(WIDTH - 270, start_y + i * (CELL_SIZE*2 + spacing), CELL_SIZE*2, CELL_SIZE*2)
                    if tool_rect.collidepoint(x, y):
                        selected_tool = tool_name
                        button_sound.play()

                # Xử lý click vào nút
                for text, pos in buttons:
                    button = pygame.Rect(pos[0], pos[1], 220, 60)
                    if button.collidepoint(x, y):
                        button_sound.play()
                        if text == "SAVE":
                            if not any(2 in row for row in editing_map) or not any(3 in row for row in editing_map):
                                error_message = "Map phải có cả công chúa và cổng thoát!"
                                error_time = pygame.time.get_ticks()
                            else:
                                if map_name:  # Nếu đã có tên (đang edit map)
                                    success = save_map_to_file(editing_map, map_name, overwrite=True)
                                    if success:
                                        maps[map_name] = editing_map.copy()
                                        created_map = editing_map.copy()
                                        map_changed = False  # Reset trạng thái thay đổi sau khi lưu
                                        running = False
                                    else:
                                        error_message = "Lỗi khi lưu map!"
                                        error_time = pygame.time.get_ticks()
                                else:  # Map mới, cần nhập tên
                                    input_active = True
                                    input_text = ""
                        elif text == "BACK":
                            if map_changed:
                                # Hiển thị cảnh báo khi có thay đổi chưa lưu
                                confirmation = show_unsaved_changes_warning()
                                if confirmation == "SAVE":
                                    if map_name:  # Nếu đã có tên (đang edit map)
                                        success = save_map_to_file(editing_map, map_name, overwrite=True)
                                        if success:
                                            maps[map_name] = editing_map.copy()
                                            created_map = editing_map.copy()
                                            running = False
                                        else:
                                            error_message = "Lỗi khi lưu map!"
                                            error_time = pygame.time.get_ticks()
                                            continue  # Không thoát nếu lưu không thành công
                                    else:  # Map mới, cần nhập tên
                                        input_active = True
                                        input_text = ""
                                        continue  # Không thoát cho đến khi lưu
                                elif confirmation == "DISCARD":
                                    running = False
                                # Nếu CANCEL, không làm gì cả và tiếp tục edit
                            else:
                                running = False

                # Xử lý click vào map
                if EDITOR_X <= x < EDITOR_X + EDITOR_SIZE and EDITOR_Y <= y < EDITOR_Y + EDITOR_SIZE:
                    col = (x - EDITOR_X) // CELL_SIZE_EDITOR
                    row = (y - EDITOR_Y) // CELL_SIZE_EDITOR
                    
                    # Giá trị hiện tại của ô trước khi thay đổi
                    current_cell_value = editing_map[row][col]
                    
                    # Kiểm tra double click
                    is_double_click = False
                    if last_click_pos and last_click_pos == (row, col) and current_time - last_click_time < double_click_delay:
                        # Double click - xóa ô
                        if editing_map[row][col] != 0:
                            editing_map[row][col] = 0
                            map_changed = True  # Đánh dấu map đã thay đổi
                        is_double_click = True
                    
                    # Cập nhật thời gian click và vị trí
                    last_click_time = current_time
                    last_click_pos = (row, col)
                    
                    # Nếu không phải double click và đã chọn công cụ, đặt vật thể
                    if not is_double_click and selected_tool:
                        new_value = None
                        if selected_tool == "Wall":
                            new_value = 1
                        elif selected_tool == "Princess":
                            # Xóa công chúa cũ nếu có
                            for r in range(map_size):
                                for c in range(map_size):
                                    if editing_map[r][c] == 2:
                                        editing_map[r][c] = 0
                            new_value = 2
                        elif selected_tool == "Exit":
                            # Xóa cổng thoát cũ nếu có
                            for r in range(map_size):
                                for c in range(map_size):
                                    if editing_map[r][c] == 3:
                                        editing_map[r][c] = 0
                            new_value = 3
                            
                        # Chỉ đánh dấu thay đổi nếu giá trị thực sự thay đổi
                        if new_value is not None and current_cell_value != new_value:
                            editing_map[row][col] = new_value
                            map_changed = True

        # Kiểm tra xem map có thay đổi so với bản gốc không (cho trường hợp edit map có sẵn)
        if not map_changed and existing_map:
            map_changed = not all(original_map[i][j] == editing_map[i][j] 
                               for i in range(map_size) for j in range(map_size))

        # Vẽ hộp thoại nhập tên map
        if input_active:
            dialog_width, dialog_height = 400, 200
            dialog_rect = pygame.Rect(WIDTH//2 - dialog_width//2, 
                                    HEIGHT//2 - dialog_height//2,
                                    dialog_width, dialog_height)
            pygame.draw.rect(screen, PANEL_COLOR, dialog_rect, border_radius=15)
            pygame.draw.rect(screen, GOLD_DARK, dialog_rect, 3, border_radius=15)

            title = font.render("Enter Map Name:", True, WHITE)
            screen.blit(title, (dialog_rect.centerx - title.get_width()//2, 
                               dialog_rect.y + 30))

            input_box = pygame.Rect(dialog_rect.centerx - 150,
                                  dialog_rect.centery - 20, 300, 40)
            pygame.draw.rect(screen, WHITE, input_box, border_radius=5)

            input_surface = font.render(input_text, True, BLACK)
            screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))

            ok_button = pygame.Rect(dialog_rect.centerx - 110,
                                  dialog_rect.y + dialog_height - 60, 100, 40)
            cancel_button = pygame.Rect(dialog_rect.centerx + 10,
                                      dialog_rect.y + dialog_height - 60, 100, 40)
            draw_beautiful_button(ok_button, "OK", font, base_color=(50, 150, 50))
            draw_beautiful_button(cancel_button, "Cancel", font, base_color=(150, 50, 50))

        pygame.display.flip()

    WIDTH, HEIGHT = old_width, old_height
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    return created_map

def show_unsaved_changes_warning():
    """Hiển thị cảnh báo khi có thay đổi chưa lưu."""
    original_screen = screen.copy()
    
    # Tạo lớp overlay mờ
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt
    screen.blit(overlay, (0, 0))
    
    # Vẽ hộp thoại xác nhận
    dialog_width, dialog_height = 500, 220
    dialog_rect = pygame.Rect(WIDTH//2 - dialog_width//2, HEIGHT//2 - dialog_height//2,
                            dialog_width, dialog_height)
    pygame.draw.rect(screen, PANEL_COLOR, dialog_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 50, 50), dialog_rect, 3, border_radius=15)
    
    # Tiêu đề và nội dung
    title = button_font.render("UNSAVED CHANGES", True, (255, 100, 100))
    message = font.render("You have unsaved changes. What do you want to do?", True, WHITE)
    
    screen.blit(title, (dialog_rect.centerx - title.get_width()//2, dialog_rect.y + 30))
    screen.blit(message, (dialog_rect.centerx - message.get_width()//2, dialog_rect.y + 80))
    
    # Các nút
    save_button = pygame.Rect(dialog_rect.x + 30, dialog_rect.bottom - 70, 140, 50)
    discard_button = pygame.Rect(dialog_rect.centerx - 70, dialog_rect.bottom - 70, 140, 50)
    cancel_button = pygame.Rect(dialog_rect.right - 170, dialog_rect.bottom - 70, 140, 50)
    
    result = None
    
    # Loop cho hộp thoại xác nhận
    while result is None:
        save_hovered = draw_beautiful_button(save_button, "SAVE", font, base_color=(50, 150, 50))
        discard_hovered = draw_beautiful_button(discard_button, "DISCARD", font, base_color=(150, 50, 50))
        cancel_hovered = draw_beautiful_button(cancel_button, "CANCEL", font)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_button.collidepoint(event.pos):
                    button_sound.play()
                    result = "SAVE"
                elif discard_button.collidepoint(event.pos):
                    button_sound.play()
                    result = "DISCARD"
                elif cancel_button.collidepoint(event.pos):
                    button_sound.play()
                    result = "CANCEL"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = "CANCEL"
        
        pygame.display.flip()
        pygame.time.delay(10)
    
    # Khôi phục màn hình gốc nếu hủy
    if result == "CANCEL":
        screen.blit(original_screen, (0, 0))
        pygame.display.flip()
    
    return result

def gradient_rect(surface, rect, color1, color2):
    """Vẽ hình chữ nhật với màu gradient."""
    for i in range(rect.height):
        ratio = i / rect.height
        color = (
            int(color1[0] * (1-ratio) + color2[0] * ratio),
            int(color1[1] * (1-ratio) + color2[1] * ratio),
            int(color1[2] * (1-ratio) + color2[2] * ratio)
        )
        pygame.draw.line(surface, color, (rect.x, rect.y + i), 
                        (rect.right, rect.y + i))

def draw_gradient_button(rect, text, font, 
                        color1=(70,70,80), color2=(50,50,60)):
    """Vẽ nút với gradient và hiệu ứng hover."""
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)
    
    if hovered:
        color1 = tuple(min(x + 20, 255) for x in color1)
        color2 = tuple(min(x + 20, 255) for x in color2)
    
    gradient_rect(screen, rect, color1, color2)
    pygame.draw.rect(screen, GOLD_DARK, rect, 2, border_radius=5)
    
    text_surface = font.render(text, True, GOLD_LIGHT if hovered else WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def save_map_to_file(map_data, map_name, overwrite=False):
    """Lưu map vào file maps.txt với tên map."""
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps.txt")
        print(f"Đang lưu map '{map_name}' vào: {file_path}")
        
        if overwrite:
            # Đọc tất cả các map hiện tại
            maps_data = {}
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    lines = file.readlines()
                    current_map = []
                    current_name = None
                    for line in lines:
                        line = line.strip()
                        if not line:
                            if current_map and current_name:
                                maps_data[current_name] = current_map
                                current_map = []
                                current_name = None
                        elif current_name is None:
                            current_name = line
                        else:
                            try:
                                current_map.append(line)
                            except:
                                current_map = []
                                current_name = None
                    if current_map and current_name:
                        maps_data[current_name] = current_map
            
            # Cập nhật map cần ghi đè
            maps_data[map_name] = [",".join(map(str, row)) for row in map_data]
            
            # Ghi lại tất cả các map
            with open(file_path, "w") as file:
                for name, map_rows in maps_data.items():
                    file.write(f"{name}\n")
                    for row in map_rows:
                        file.write(f"{row}\n")
                    file.write("\n")
            
        else:
            # Thêm map mới vào cuối file
            with open(file_path, "a") as file:
                file.write(f"{map_name}\n")
                for row in map_data:
                    file.write(",".join(map(str, row)) + "\n")
                file.write("\n")
        
        print(f"Đã lưu map '{map_name}' thành công!")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu map: {e}")
        return False

def load_maps_from_file():
    """Tải các map từ file maps.txt."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps.txt")
    if not os.path.exists(file_path):
        print("File maps.txt không tồn tại. Không có map nào được tải.")
        return {}
    
    maps = {}
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            current_map = []
            current_name = None
            for line in lines:
                line = line.strip()
                if not line:
                    if current_map and current_name:
                        maps[current_name] = current_map
                        current_map = []
                        current_name = None
                elif current_name is None:
                    current_name = line
                else:
                    try:
                        current_map.append(list(map(int, line.split(","))))
                    except ValueError:
                        print(f"Dòng không hợp lệ trong map '{current_name}': {line}")
                        current_map = []
                        current_name = None
            if current_map and current_name:
                maps[current_name] = current_map
    except Exception as e:
        print(f"Lỗi khi tải maps: {e}")
    return maps

def draw_map_creation_menu():
    """Menu chọn chế độ tạo map."""
    screen.fill(BLACK)
    draw_animated_title("Map Creation", HEIGHT//4)

    create_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 70)
    auto_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 70)
    back_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 130, 300, 70)

    create_hovered = draw_beautiful_button(create_button, "CREATE MAP", button_font)
    auto_hovered = draw_beautiful_button(auto_button, "AUTO GENERATE", button_font)
    back_hovered = draw_beautiful_button(back_button, "BACK", button_font)

    pygame.display.flip()
    return create_button, auto_button, back_button, create_hovered, auto_hovered, back_hovered

def auto_generate_map(rows, cols):
    """Tự động tạo map với ít nhất 1 đường đi đến công chúa và đến đích."""
    # Tạo một ma trận toàn là đường đi trước
    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Thêm một số tường ngẫu nhiên (khoảng 30% map)
    for _ in range(int(rows * cols * 0.3)):
        r, c = random.randint(1, rows-2), random.randint(1, cols-2)
        maze[r][c] = 1
    
    # Đảm bảo điểm bắt đầu và kết thúc không phải là tường
    maze[1][1] = 0
    maze[rows - 2][cols - 2] = 0
    
    # Đặt công chúa ở vị trí ngẫu nhiên
    princess_pos = None
    while not princess_pos:
        r, c = random.randint(2, rows-3), random.randint(2, cols-3)
        if maze[r][c] == 0:
            princess_pos = (r, c)
            maze[r][c] = 2
            
    # Đặt cổng thoát ở vị trí cạnh điểm kết thúc
    exit_pos = None
    while not exit_pos:
        r, c = random.randint(rows-3, rows-1), random.randint(cols-3, cols-1)
        if maze[r][c] == 0:
            exit_pos = (r, c)
            maze[r][c] = 3
    
    temp_maze = [[maze[i][j] for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if temp_maze[i][j] == 2:
                temp_maze[i][j] = 0
            elif temp_maze[i][j] == 3:
                temp_maze[i][j] = 0

    path_to_princess = bfs(temp_maze, (1, 1), princess_pos)
    
    path_to_exit = bfs(temp_maze, princess_pos, exit_pos)

    if not path_to_princess:
        current = (1, 1)
        while current != princess_pos:
            next_r = current[0] + (1 if current[0] < princess_pos[0] else -1 if current[0] > princess_pos[0] else 0)
            next_c = current[1] + (1 if current[1] < princess_pos[1] else -1 if current[1] > princess_pos[1] else 0)
            current = (next_r, next_c)
            if maze[current[0]][current[1]] == 1:
                maze[current[0]][current[1]] = 0
    
    if not path_to_exit:
        current = princess_pos
        while current != exit_pos:
            next_r = current[0] + (1 if current[0] < exit_pos[0] else -1 if current[0] > exit_pos[0] else 0)
            next_c = current[1] + (1 if current[1] < exit_pos[1] else -1 if current[1] > exit_pos[1] else 0)
            current = (next_r, next_c)
            if maze[current[0]][current[1]] == 1:
                maze[current[0]][current[1]] = 0
    
    return maze

def delete_and_create_empty_maps_file():
    """Xóa file maps.txt và tạo lại file trống."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps.txt")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w") as file:
            file.write("")
        print("Đã xóa và tạo lại file maps.txt trống.")
    except Exception as e:
        print(f"Lỗi khi xóa và tạo lại file maps.txt: {e}")

def save_all_maps_to_file():
    """Lưu toàn bộ maps vào file maps.txt."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps.txt")
    try:
        with open(file_path, "w") as file:
            for map_name, map_data in maps.items():
                file.write(f"{map_name}\n")
                for row in map_data:
                    file.write(",".join(map(str, row)) + "\n")
                file.write("\n")
        print("Đã lưu toàn bộ maps vào file maps.txt.")
    except Exception as e:
        print(f"Lỗi khi lưu maps: {e}")

def save_player_score(steps, time, map_name, rescued=True, difficulty="EASY"):
    player_scores_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "player_scores.txt")
    try:
        rescued_value = "1" if rescued else "0"
        with open(player_scores_file, "a") as file:
            file.write(f"{map_name},{steps},{time},{rescued_value},{difficulty}\n")
    except Exception as e:
        print(f"Lỗi khi lưu điểm người chơi: {e}")

def save_ai_score(map_name, algorithm, difficulty, steps, time, rescued):
    ai_score_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_score.txt")
    
    existing_entries = set()
    if os.path.exists(ai_score_file):
        with open(ai_score_file, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 6:
                    entry_id = f"{parts[0]},{parts[1]},{parts[2]},{parts[5]}"
                    existing_entries.add(entry_id)
    
    new_entry_id = f"{map_name},{algorithm},{difficulty},{rescued}"
    
    if new_entry_id not in existing_entries:
        try:
            with open(ai_score_file, "a") as file:
                file.write(f"{map_name},{algorithm},{difficulty},{steps},{time},{rescued}\n")
        except Exception as e:
            print(f"Lỗi khi lưu điểm AI: {e}")

def main():
    global maps, current_frame, animation_speed, WIDTH, HEIGHT, screen

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Khởi tạo game
    load_animation_frames()
    maps = load_maps_from_file()
    scoreboard = load_scoreboard()
    
    # Khởi tạo trạng thái game
    map_selection = False
    mode_selection = False
    difficulty_selection = False
    algorithm_selection = False
    game_active = False
    ai_mode = False
    waiting_for_restart = False
    hard_mode = False
    

    animation_timer = 0
    in_main_menu = True
    ai_high_scores = {}

    while True:
        if in_main_menu:
            # Menu chính
            play_button, create_map_button, manage_maps_button, ai_stats_button, tutorial_button, exit_button, play_hovered, create_map_hovered, manage_maps_hovered, ai_stats_hovered, tutorial_hovered, exit_hovered = draw_main_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.collidepoint(event.pos):
                        button_sound.play()
                        in_main_menu = False
                        map_selection = True
                        
                    elif create_map_button.collidepoint(event.pos):
                        button_sound.play()
                        custom_map = create_map_editor()
                        if custom_map:
                            maps = load_maps_from_file()
                    #Manage maps
                    elif manage_maps_button.collidepoint(event.pos):
                        button_sound.play()
                        manage_maps = True
                        while manage_maps:
                            scroll_offset = 0
                            max_visible = 6
                            while manage_maps:
                                maps = load_maps_from_file()
                                map_buttons, delete_buttons, edit_buttons, back_button = draw_map_management_menu(maps, scroll_offset, max_visible)
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        if back_button.collidepoint(event.pos):
                                            button_sound.play()
                                            manage_maps = False
                                            break
                                        for button, map_name in delete_buttons:
                                            if button.collidepoint(event.pos):
                                                button_sound.play()
                                                del maps[map_name]
                                                save_all_maps_to_file()
                                                break
                                        for button, map_name in edit_buttons:
                                            if button.collidepoint(event.pos):
                                                button_sound.play()
                                                # Lấy map hiện tại để chỉnh sửa
                                                current_map = maps[map_name]
                                                # Gọi map editor với map hiện có và tên map
                                                custom_map = create_map_editor(existing_map=current_map, map_name=map_name)
                                                if custom_map:
                                                    maps = load_maps_from_file()
                                                break
                                    if event.type == pygame.MOUSEWHEEL:
                                        if event.y < 0 and scroll_offset < max(0, len(maps)-max_visible):
                                            scroll_offset += 1
                                        elif event.y > 0 and scroll_offset > 0:
                                            scroll_offset -= 1
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_DOWN and scroll_offset < max(0, len(maps)-max_visible):
                                            scroll_offset += 1
                                        if event.key == pygame.K_UP and scroll_offset > 0:
                                            scroll_offset -= 1
                                pygame.time.delay(10)
                            
                    elif ai_stats_button.collidepoint(event.pos):
                        button_sound.play()
                        ai_stats_screen = True
                        in_main_menu = False
                        
                    elif tutorial_button.collidepoint(event.pos):
                        button_sound.play()
                        show_tutorial = True
                        while show_tutorial:
                            back_button = draw_game_tutorial()
                            
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if back_button.collidepoint(event.pos):
                                        button_sound.play()
                                        show_tutorial = False
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        show_tutorial = False
                            
                            pygame.time.delay(10)
                            
                    elif exit_button.collidepoint(event.pos):
                        button_sound.play()
                        pygame.quit()
                        sys.exit()

        # Màn hình chọn map
        elif map_selection:
            scroll_offset = 0
            max_visible = 6
            while map_selection:
                maps = load_maps_from_file()
                map_buttons, back_button, hover_states, back_hovered = draw_map_selection(maps, scroll_offset, max_visible)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if back_button.collidepoint(event.pos):
                            button_sound.play()
                            map_selection = False
                            in_main_menu = True
                            continue
                        for button, map_name in map_buttons:
                            if button.collidepoint(event.pos):
                                button_sound.play()
                                selected_map = maps[map_name]
                                current_map_name = map_name
                                map_selection = False
                                mode_selection = True
                                break
                    if event.type == pygame.MOUSEWHEEL:
                        if event.y < 0 and scroll_offset < max(0, len(maps)-max_visible):
                            scroll_offset += 1
                        elif event.y > 0 and scroll_offset > 0:
                            scroll_offset -= 1
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN and scroll_offset < max(0, len(maps)-max_visible):
                            scroll_offset += 1
                        if event.key == pygame.K_UP and scroll_offset > 0:
                            scroll_offset -= 1
                    pygame.time.delay(10)

        # Màn hình chọn chế độ chơi
        elif mode_selection:
            manual_button, ai_button, back_button, manual_hovered, ai_hovered, back_hovered = draw_play_mode_selection()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        button_sound.play()
                        mode_selection = False
                        map_selection = True
                        continue
                        
                    if manual_button.collidepoint(event.pos):
                        button_sound.play()
                        mode_selection = False
                        difficulty_selection = True
                        ai_mode = False
                        
                    if ai_button.collidepoint(event.pos):
                        button_sound.play()
                        mode_selection = False
                        algorithm_selection = True
                        ai_mode = True
        
        # Màn hình chọn độ khó
        elif difficulty_selection:
            easy_button, hard_button, back_button, easy_hovered, hard_hovered, back_hovered = draw_difficulty_selection()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        button_sound.play()
                        difficulty_selection = False
                        mode_selection = True
                        continue
                        
                    if easy_button.collidepoint(event.pos):
                        button_sound.play()
                        difficulty_selection = False
                        game_active = True
                        hard_mode = False
                        
                    if hard_button.collidepoint(event.pos):
                        button_sound.play()
                        difficulty_selection = False
                        game_active = True
                        hard_mode = True

        # Màn hình chọn thuật toán cho AI
        elif algorithm_selection:
            algorithm_buttons, back_button, hover_states, back_hovered = draw_ai_algorithm_selection()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        button_sound.play()
                        algorithm_selection = False
                        mode_selection = True
                        continue
                        
                    for button, algo_name in algorithm_buttons:
                        if button.collidepoint(event.pos):
                            button_sound.play()
                            selected_algorithm = algo_name
                            
                             # Nếu chọn PO, hiển thị popup cài đặt
                            if selected_algorithm == "Partially Observable":
                                # Lưu màn hình hiện tại
                                screen_backup = screen.copy()
                                
                                # Khởi tạo giá trị mặc định
                                po_settings_done = False
                                draw_po_visibility_selection.visibility_value = 50
                                draw_po_visibility_selection.fog_enabled = True
                                
                                while not po_settings_done:
                                    slider_rect, handle_rect, confirm_button, cancel_button, fog_checkbox_rect, visibility_value, fog_enabled = draw_po_visibility_selection()
                                    
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            pygame.quit()
                                            sys.exit()
                                            
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            if confirm_button.collidepoint(event.pos):
                                                button_sound.play()
                                                po_visibility = visibility_value
                                                po_fog_enabled = fog_enabled
                                                po_settings_done = True
                                                
                                            elif cancel_button.collidepoint(event.pos):
                                                button_sound.play()
                                                # Hủy và quay lại màn hình chọn thuật toán
                                                screen.blit(screen_backup, (0, 0))
                                                pygame.display.flip()
                                                break
                                                
                                            elif fog_checkbox_rect.collidepoint(event.pos):
                                                button_sound.play()
                                                draw_po_visibility_selection.fog_enabled = not fog_enabled
                                                
                                            elif slider_rect.collidepoint(event.pos) or handle_rect.collidepoint(event.pos):
                                                # Bắt đầu kéo thanh trượt
                                                dragging = True
                                                while dragging:
                                                    for event in pygame.event.get():
                                                        if event.type == pygame.MOUSEBUTTONUP:
                                                            dragging = False
                                                        if event.type == pygame.MOUSEMOTION:
                                                            x_pos = max(slider_rect.x, min(slider_rect.right, event.pos[0]))
                                                            percentage = int((x_pos - slider_rect.x) / slider_rect.width * 100)
                                                            draw_po_visibility_selection.visibility_value = percentage
                                                            # Vẽ lại popup với giá trị mới
                                                            slider_rect, handle_rect, confirm_button, cancel_button, fog_checkbox_rect, visibility_value, fog_enabled = draw_po_visibility_selection()
                                        
                                        if event.type == pygame.KEYDOWN:
                                            if event.key == pygame.K_ESCAPE:
                                                # Hủy và quay lại màn hình chọn thuật toán
                                                screen.blit(screen_backup, (0, 0))
                                                pygame.display.flip()
                                                po_settings_done = False
                                                break
                                
                                if not po_settings_done:
                                    continue  # Không tiếp tục nếu người dùng hủy

                            algorithm_selection = False
                            game_active = True
                            ai_mode = True

                            # Khởi tạo giá trị khó dựa theo chọn lựa
                            difficulty_selection = False
                            
                            if selected_algorithm == "BFS":
                                ai_function = bfs_algorithm
                            elif selected_algorithm == "A*":
                                ai_function = astar_algorithm
                            elif selected_algorithm == "Simple Hill Climbing":
                                ai_function = simple_hill_climbing_algorithm
                            elif selected_algorithm == "Partially Observable":
                                ai_function = partially_observable_algorithm
                                # Khởi tạo đầy đủ ai_knowledge với visibility_percentage và fog_enabled
                                ai_knowledge = {
                                    "maze": [[None for _ in range(COLS)] for _ in range(ROWS)],
                                    "probability": [[0.5 for _ in range(COLS)] for _ in range(ROWS)],
                                    "visited": set(),
                                    "frontier": set(),
                                    "princess_found": False,
                                    "exit_found": False,
                                    "princess_pos": None,
                                    "exit_pos": None,
                                    "princess_rescued": False,
                                    "exploration_bias": 0.3,
                                    "visibility_percentage": po_visibility,
                                    "fog_enabled": po_fog_enabled
                                }
                            elif selected_algorithm == "Min Conflicts":
                                ai_function = min_conflicts_algorithm
                            elif selected_algorithm == "Q-Learning":
                                ai_function = q_learning_algorithm
                            if selected_algorithm != "Partially Observable":
                                ai_knowledge = None
                            ai_steps = 0
                            ai_deaths = 0
                            break

        # Chơi game
        elif game_active:
            # Khởi tạo game
            maze = selected_map
            player_pos = (1, 1)
            princess_pos = None
            target_pos = None
            
            # Tìm vị trí công chúa và cổng thoát
            for row in range(ROWS):
                for col in range(COLS):
                    if maze[row][col] == 2:
                        princess_pos = (row, col)
                    elif maze[row][col] == 3:
                        target_pos = (row, col)
            
            if not princess_pos:
                princess_pos = (14, 14)
            if not target_pos:
                target_pos = (14, 1)
                
            ghost_pos = None
            steps = 0
            princess_rescued = False
            previous_player_pos = player_pos
            
            # Tốc độ di chuyển quái vật dựa vào chế độ chơi
            monster_move_time = 700 if not hard_mode else 300  # Dễ: 700ms, Khó: 300ms
            
            last_monster_move = pygame.time.get_ticks()
            visible = [[False for _ in range(COLS)] for _ in range(ROWS)]
            
            # Hiển thị toàn bộ map trong chế độ dễ hoặc khi AI không phải PO
            if not hard_mode or (ai_mode and selected_algorithm != "Partially Observable"):
                visible = [[True for _ in range(COLS)] for _ in range(ROWS)]
            else:
                update_visible_area(visible, player_pos)
                
            map_width = COLS * CELL_SIZE
            map_height = ROWS * CELL_SIZE
            offset_x = (WIDTH - map_width) // 2
            offset_y = (HEIGHT - map_height) // 2
            start_time = pygame.time.get_ticks()
            monster_speed_increase = 0
            
            # Biến cho chế độ AI
            if ai_mode:
                ai_move_delay = 200  # Độ trễ giữa các bước di chuyển của AI
                last_ai_move = pygame.time.get_ticks()

            # Biến cho thông báo quái vật
            monster_notification_time = 0
            show_monster_notification = False
            
            while game_active:
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - start_time) // 1000

                # Xử lý events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_active = False
                            in_main_menu = True
                            break
                        
                        # Xử lý di chuyển trong chế độ thủ công
                        if not ai_mode:
                            new_player_pos = player_pos
                            moved = False
                            
                            if event.key == pygame.K_UP and player_pos[0] > 0 and maze[player_pos[0]-1][player_pos[1]] != 1:
                                new_player_pos = (player_pos[0]-1, player_pos[1])
                                moved = True
                            if event.key == pygame.K_DOWN and player_pos[0] < ROWS-1 and maze[player_pos[0]+1][player_pos[1]] != 1:
                                new_player_pos = (player_pos[0]+1, player_pos[1])
                                moved = True
                            if event.key == pygame.K_LEFT and player_pos[1] > 0 and maze[player_pos[0]][player_pos[1]-1] != 1:
                                new_player_pos = (player_pos[0], player_pos[1]-1)
                                moved = True
                            if event.key == pygame.K_RIGHT and player_pos[1] < COLS-1 and maze[player_pos[0]][player_pos[1]+1] != 1:
                                new_player_pos = (player_pos[0], player_pos[1]+1)
                                moved = True

                            if moved and new_player_pos != player_pos:
                                move_sound.play()
                                previous_player_pos = player_pos
                                player_pos = new_player_pos
                                steps += 1
                                
                                # Cập nhật vị trí công chúa nếu đã giải cứu
                                if princess_rescued:
                                    princess_pos = previous_player_pos
                                
                                # Chỉ cập nhật vùng nhìn thấy trong chế độ khó
                                if hard_mode:
                                    update_visible_area(visible, player_pos)
                                offset_x = 0
                                map_height = ROWS * CELL_SIZE
                                offset_y = max(0, (HEIGHT - map_height) // 2)

                # Xử lý di chuyển của AI
                if ai_mode and current_time - last_ai_move > ai_move_delay:
                    # Cập nhật trạng thái giải cứu công chúa trước khi gọi AI
                    if player_pos == princess_pos and not princess_rescued:
                        princess_rescued = True
                        # Đảm bảo AI biết công chúa đã được cứu
                        if ai_knowledge:
                            ai_knowledge["princess_rescued"] = True
                    
                    # Gọi hàm AI để tìm bước đi tiếp theo
                    next_move, ai_knowledge = ai_function(maze, player_pos, princess_pos, target_pos, visible, ai_knowledge)
                    
                    if next_move:
                        move_sound.play()
                        previous_player_pos = player_pos
                        player_pos = next_move
                        steps += 1
                        ai_steps += 1
                        
                        # Cập nhật vị trí công chúa nếu đã giải cứu
                        if princess_rescued:
                            princess_pos = previous_player_pos
                        
                        # Chỉ cập nhật vùng nhìn thấy trong chế độ khó
                        if hard_mode:
                            update_visible_area(visible, player_pos)
                        offset_x = 0
                        map_height = ROWS * CELL_SIZE
                        offset_y = max(0, (HEIGHT - map_height) // 2)
                    
                    last_ai_move = current_time

                # Logic game
                if player_pos == princess_pos and not princess_rescued:
                    princess_found_sound.play()
                    princess_rescued = True
                    if ai_mode and ai_knowledge:
                        ai_knowledge["princess_rescued"] = True

                if steps >= 20 and not ghost_pos:
                    ghost_spawn_sound.play()
                    ghost_pos = (1, 1)
                    show_monster_notification = True
                    monster_notification_time = current_time

                # Xử lý thông báo quái vật
                if show_monster_notification:
                    if current_time - monster_notification_time < 2000:
                        alpha = min(255, int(255 * (1 - (current_time - monster_notification_time) / 2000)))
                        monster_text = "Monster appeared!"
                        monster_surface = font.render(monster_text, True, (255, 50, 50))
                        monster_panel = pygame.Rect(WIDTH//2 - monster_surface.get_width()//2 - 10, 10, 
                                                   monster_surface.get_width() + 20, 40)
                        
                        notification_surface = pygame.Surface((monster_panel.width, monster_panel.height), pygame.SRCALPHA)
                        pygame.draw.rect(notification_surface, (*PANEL_COLOR, alpha), notification_surface.get_rect(), border_radius=10)
                        pygame.draw.rect(notification_surface, (255, 50, 50, alpha), notification_surface.get_rect(), 2, border_radius=10)
                        
                        text_surface = font.render(monster_text, True, (255, 50, 50))
                        text_surface.set_alpha(alpha)

                        screen.blit(notification_surface, monster_panel)
                        screen.blit(text_surface, (monster_panel.centerx - text_surface.get_width()//2, 
                                                 monster_panel.centery - text_surface.get_height()//2))
                    else:
                        show_monster_notification = False

                if ghost_pos and current_time - last_monster_move > monster_move_time:
                    target = princess_pos if princess_rescued else player_pos
                    path = bfs(maze, ghost_pos, target)
                    if path and len(path) > 0:
                        ghost_pos = path[0]
                    last_monster_move = current_time
                    
                    # tăng tốc độ quái vật theo thời gian
                    if hard_mode and monster_move_time > 150:  # Chế độ khó, giảm xuống tối thiểu 150ms
                        monster_move_time -= 2
                    elif not hard_mode and monster_move_time > 300:  # Chế độ dễ, giảm xuống tối thiểu 300ms
                        monster_move_time -= 1

                # Vẽ game với sương mù tùy theo chế độ khó/AI
                screen.fill((20, 20, 20))
                use_fog = (hard_mode and not ai_mode)
                if ai_mode and selected_algorithm == "Partially Observable" and 'ai_knowledge' in locals() and ai_knowledge:
                    use_fog = ai_knowledge.get("fog_enabled", True)
                    
                draw_maze(maze, visible, offset_x, offset_y, player_pos, use_fog=use_fog, 
                        ai_mode=ai_mode, selected_algorithm=selected_algorithm if ai_mode else None, 
                        ai_knowledge=ai_knowledge if 'ai_knowledge' in locals() else None)
                
                draw_entities(player_pos, princess_pos, ghost_pos, target_pos, visible, offset_x, offset_y)

                # UI
                if ai_mode:
                    time_panel = pygame.Rect(WIDTH - 140, 10, 100, 40)
                    pygame.draw.rect(screen, PANEL_COLOR, time_panel, border_radius=10)
                    pygame.draw.rect(screen, GOLD_DARK, time_panel, 3, border_radius=10)
                    time_text = button_font.render(f"{elapsed_time}s", True, GOLD_LIGHT)
                    screen.blit(time_text, (time_panel.x + 12, time_panel.y + 4))
                else:
                    # Hiển thị thông tin chế độ chơi
                    mode_text = "HARD MODE" if hard_mode else "EASY MODE"
                    ui_panel = pygame.Rect(10, 10, 150, 40)
                    pygame.draw.rect(screen, PANEL_COLOR, ui_panel, border_radius=10)
                    pygame.draw.rect(screen, GOLD_DARK if hard_mode else (50, 150, 50), ui_panel, 2, border_radius=10)
                    mode_surface = font.render(mode_text, True, GOLD_LIGHT if hard_mode else (100, 255, 100))
                    screen.blit(mode_surface, (20, 20))
                    
                    # Hiển thị thời gian
                    time_panel = pygame.Rect(WIDTH - 120, 10, 110, 40)
                    pygame.draw.rect(screen, PANEL_COLOR, time_panel, border_radius=10)
                    pygame.draw.rect(screen, GOLD_DARK, time_panel, 2, border_radius=10)
                    time_text = font.render(f"{elapsed_time}s", True, WHITE)
                    screen.blit(time_text, (WIDTH - 110, 20))

                animation_timer += 1
                if animation_timer >= 10:
                    animation_timer = 0
                    current_frame = (current_frame + 1) % len(knight_frames)

                pygame.display.flip()

                # Kiểm tra kết thúc game
                if princess_rescued and player_pos == target_pos:
                    victory_sound.play()
                    
                    if ai_mode:
                        # Lưu kỷ lục AI
                        ai_score_key = f"{current_map_name}_{selected_algorithm}"
                        if ai_score_key not in ai_high_scores or ai_deaths < ai_high_scores[ai_score_key][1]:
                            ai_high_scores[ai_score_key] = (ai_steps, ai_deaths)
                        
                        draw_ai_victory_screen(selected_algorithm, ai_steps, elapsed_time, current_map_name, "HARD" if hard_mode else "EASY", 1)
                        save_ai_score(current_map_name, selected_algorithm, "HARD" if hard_mode else "EASY", ai_steps, elapsed_time, 1)
                    else:
                        save_player_score(steps, elapsed_time, current_map_name, True, "HARD" if hard_mode else "EASY")
                        scoreboard = load_scoreboard()
                        draw_end_screen("Victory!", steps, elapsed_time, scoreboard, current_map_name)
                    game_active = False
                    waiting_for_restart = True
                    
                elif ghost_pos and (ghost_pos == player_pos or ghost_pos == princess_pos):
                    defeat_sound.play()
                    
                    if ai_mode:
                        ai_deaths += 1
                        rescued = 1 if princess_rescued else 0
                        draw_ai_victory_screen(selected_algorithm, steps, elapsed_time, current_map_name, "HARD" if hard_mode else "EASY", rescued)
                        save_ai_score(current_map_name, selected_algorithm, "HARD" if hard_mode else "EASY", steps, elapsed_time, rescued)
                        game_active = False
                        waiting_for_restart = True
                        save_ai_score(current_map_name, selected_algorithm, "HARD" if hard_mode else "EASY", steps, elapsed_time, 0)
                    else:
                        rescued = princess_rescued
                        save_player_score(steps, elapsed_time, current_map_name, rescued, "HARD" if hard_mode else "EASY")
                        scoreboard = load_scoreboard()
                        draw_end_screen("Defeat!", steps, elapsed_time, scoreboard, current_map_name)
                        game_active = False
                        waiting_for_restart = True

                if not game_active and waiting_for_restart:
                    result_text = "Victory!" if princess_rescued and player_pos == target_pos else "Defeat!"
                    
                    while waiting_for_restart:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key in (pygame.K_SPACE, pygame.K_ESCAPE):
                                    waiting_for_restart = False
                                    in_main_menu = True
                                    break
                                if event.key == pygame.K_DOWN:
                                    if hasattr(draw_end_screen, 'scroll_offset'):
                                        draw_end_screen.scroll_offset += 1
                                    draw_end_screen(result_text, steps, elapsed_time, scoreboard, current_map_name)
                                if event.key == pygame.K_UP:
                                    if hasattr(draw_end_screen, 'scroll_offset'):
                                        draw_end_screen.scroll_offset = max(0, draw_end_screen.scroll_offset - 1)
                                    draw_end_screen(result_text, steps, elapsed_time, scoreboard, current_map_name)
                        pygame.time.delay(10)
        elif ai_stats_screen:
            back_button = draw_ai_stats_screen()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        button_sound.play()
                        ai_stats_screen = False
                        in_main_menu = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        ai_stats_screen = False
                        in_main_menu = True
        pygame.display.flip()
        pygame.time.delay(10)
    

if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    main()