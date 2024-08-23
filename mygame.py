import pygame
import sys
import queue
import threading
from eegRead import eeg_data_thread
# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Force Ball Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Ball properties
ball_radius = 20
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_color = WHITE
ball_speed = 40

# Player properties
player_width = 10
player_height = 100
player1_pos = [50, HEIGHT // 2 - player_height // 2]
player2_pos = [WIDTH - 50 - player_width, HEIGHT // 2 - player_height // 2]

clock = pygame.time.Clock()

# Initialize EEG queue
eeg_queue = queue.Queue()
eeg_thread = threading.Thread(target=eeg_data_thread, args=(eeg_queue,))
eeg_thread.daemon = True
eeg_thread.start()

def update_ball_position(force_player1, force_player2):
    global ball_pos
    net_force = force_player1 - force_player2
    print(force_player1,force_player2)
    ball_pos[0] += net_force * ball_speed * 0.01
    if ball_pos[0] < ball_radius:
        ball_pos[0] = ball_radius
    elif ball_pos[0] > WIDTH - ball_radius:
        ball_pos[0] = WIDTH - ball_radius

def handle_input():
    global force_player1, force_player2
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        force_player1 += 0.25
    elif keys[pygame.K_RIGHT]:
        force_player1 -= 0.25

def draw():
    screen.fill(BLACK)
    
    pygame.draw.rect(screen, RED, (*player1_pos, player_width, player_height))
    pygame.draw.rect(screen, BLUE, (*player2_pos, player_width, player_height))
    
    pygame.draw.circle(screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
    
    pygame.display.flip()

# Initial forces
force_player1 = 0
force_player2 = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    handle_input()
    
    # Update forces from EEG data
    if not eeg_queue.empty():
        force_player1, force_player2 = eeg_queue.get()
    update_ball_position(force_player1, force_player2)
    draw()
    
    clock.tick(60)  # 60 frames per second
