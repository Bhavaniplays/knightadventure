import pygame
from pygame.locals import *
import random


pygame.init()
pygame.mixer.init() 


pygame.mixer.music.load("img/sound.mp3") 
pygame.mixer.music.set_volume(0.7)

# Play the music (loop indefinitely)
pygame.mixer.music.play(-1)

# Game setup
clock = pygame.time.Clock()
fps = 60

# Screen dimensions (windowed mode)
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))  # <-- windowed mode
pygame.display.set_caption('Knight Adventure')

# Font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Colours
white = (255, 255, 255)

# Game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
start_img = pygame.image.load('img/startx.png')

# Draw text on screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Reset game
def reset_game():
    global score
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

    # Show "Press SPACE to Start" message when not flying and not game over




# knight class
class knight(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/knight{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            # gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            # Controls: Mouse or Spacebar
            keys = pygame.key.get_pressed()
            if (pygame.mouse.get_pressed()[0] == 1 or keys[pygame.K_SPACE]) and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0 and not keys[pygame.K_SPACE]:
                self.clicked = False

            # Animation
            flap_cooldown = 5
            self.counter += 1
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # Rotate based on velocity
            rotated_image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
            self.image = rotated_image
        else:
            # Point down when game over
            self.image = pygame.transform.rotate(self.images[self.index], -90)

        

    # Show "Game Over" message
        # if game_over:
        #     # draw_text("GAME OVER!", font, white, screen_width // 2 - 150, screen_height // 2 - 150)
        #     # draw_text("PRESS SPACE TO RESTART", font, white, screen_width // 2 - 280, screen_height // 2 - 80)
# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()

        # position 1 = top, -1 = bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


# Button class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        # Check mouseover and click
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
          action = True

        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


# Groups
pipe_group = pygame.sprite.Group()
knight_group = pygame.sprite.Group()
flappy = knight(100, int(screen_height / 2))
knight_group.add(flappy)

# Restart button
button = Button(screen_width/2-50,screen_height/2, button_img)

# Main loop
run = True
while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))

    pipe_group.draw(screen)
    knight_group.draw(screen)
    knight_group.update()

    # Ground
    screen.blit(ground_img, (ground_scroll, 768))
    if not flying and not game_over:
            screen.blit(start_img ,(250,screen_height/2))
            
    # Score check
    if len(pipe_group) > 0:
        if knight_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and knight_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if knight_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # Collisions
    if pygame.sprite.groupcollide(knight_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if flying and not game_over:
        # Create new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()

        # Scroll ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    # Game over and restart
    if game_over:
        if button.draw():
            pygame.time.delay(200)
            game_over = False
            score = reset_game()

    # Event handler
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

    # When Space or mouse clicked
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        if not flying and not game_over:
            # Start the game
            flying = True
        elif game_over:
            # Reset and start flying again
            pygame.time.delay(200)
            game_over = False
            score = reset_game()
            flying = True  # immediately start flying again

    if event.type == pygame.MOUSEBUTTONDOWN:
        if not flying and not game_over:
            flying = True

    # Toggle fullscreen with F
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_f:
            pygame.display.toggle_fullscreen()

        
   
    pygame.display.update()

pygame.quit()
