import pygame
from pygame import mixer

import random



pygame.font.init()

# global variables
screen_width = 800 #the width of the screen
screen_height = 700 #the height of the screen 
block_width = 300  # (width of the play block) 300 // 10 = 30 width per block
block_height = 600  # (height of the play block) meaning 600 // 20 = 30 height per block
block_size = 30 

#top left position 
tlp_x = (screen_width - block_width) // 2 
tlp_y = screen_height - block_height


#shape formats

#shape S can rotate twice
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

#shape Z can rotate twice
Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

#shape I can rotate twice
I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

#shape O can rotate once 
O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

#shape J can rotate four times
J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

#shape L can rotate four times
L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

#shape T can rotate four times
T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(191, 252, 198), (255, 190, 188), (197, 163, 255), (255, 255, 209), (172, 231, 255), (255, 203, 193), (175, 248, 216)]
# index 0 - 6 represent shape based on order

# Background Sounds 
pygame.mixer.init(44100, -16,2,2048)
mixer.music.load("tetris-soundtrack.wav")
mixer.music.play(-1) #to loop 


class Piece(object):  
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)] #the shape we get we take the colour based on the index 
        self.rotation = 0


def creating_grid(locked_pos={}):  #finding the corresponding position to the locked position to get an accurate grid 
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)] #making list for each row 

    for v in range(len(grid)): #rows represented by v
        for w in range(len(grid[v])): #columns represented by w
            if (w, v) in locked_pos: 
                c = locked_pos[(w,v)]
                grid[v][w] = c
    return grid

#translating the list so that the computer can understand 
def conversion_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for v, line in enumerate(format):
        row = list(line)
        for w, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + w, shape.y + v))

    for v, pos in enumerate(positions):
        positions[v] = (pos[0] - 2, pos[1] - 4)

    return positions 

#to make sure the shape is moving into valid spaces 
def valid_spaces(shape, grid):
    accepted_pos = [[(w, v) for w in range(10) if grid[v][w] == (0,0,0)] for v in range(20)]
    accepted_pos = [w for sub in accepted_pos for w in sub]
    #colours other than black means they are occupied, if not then free. 

    formatted = conversion_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

#functions to check if the users has lost the game 
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False  #if the users has reached the stop then they lost

#to generate a random shape during the game 
def get_the_shape(): 
    return Piece(5, 0, random.choice(shapes))

#display text to the middle of the screen during main menu and end screen of the game 
def text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (tlp_x + block_width /2 - (label.get_width()/2), tlp_y + block_height/2 - label.get_height()/2))

#this function is the one that draws the grey lines that we seen in the game 
def drawing_grid(surface, grid):
    sx = tlp_x
    sy = tlp_y

    for v in range(len(grid)): #horizontal lines 
        pygame.draw.line(surface, (128,128,128), (sx, sy + v*block_size), (sx+block_width, sy+ v*block_size)) 
        for w in range(len(grid[v])): #vertical lines
            pygame.draw.line(surface, (128, 128, 128), (sx + w*block_size, sy),(sx + w*block_size, sy + block_height)) 

#function to check if the row is full, if it's full then it would be deleted 
def clearing_rows(grid, locked):
# needs to see whether the row is clear the shift every other row above down one 
    inc = 0
    for v in range(len(grid)-1, -1, -1):
        row = grid[v]
        if (0,0,0) not in row:
            inc += 1
            #adding position to remove from the locked 
            ind = v
            for w in range(len(row)):
                try:
                    del locked[(w,v)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc

#displaying the next falling shape on the right side of the screen 
def next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (0,0,0))

    sx = tlp_x + block_width + 50
    sy = tlp_y + block_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for v, line in enumerate(format):
        row = list(line)
        for w, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + w*block_size, sy + v*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))

#to update the scores
def update_scores(nscore):
    score = maximum_scores()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

#to save the users best score 
def maximum_scores():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score

#displaying the current and best score 
def drawing_window(surface, grid, score=0, last_score = 0):
    surface.fill((255, 255, 255))
    #Tetris Title 
    pygame.font.init() 
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (0, 0, 0))

    surface.blit(label, (tlp_x + block_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (0, 0, 0))

    sx = tlp_x + block_width + 50
    sy = tlp_y + block_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('High Score: ' + last_score, 1, (255, 255, 255))

    sx = tlp_x - 200
    sy = tlp_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for v in range(len(grid)):
        for w in range(len(grid[v])):
            pygame.draw.rect(surface, grid[v][w], (tlp_x + w*block_size, tlp_y + v*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (tlp_x, tlp_y, block_width, block_height), 5)

    drawing_grid(surface, grid)
    #pygame.display.update()

#the game loop and this will run constantly 
def main(win):  
    last_score = maximum_scores()
    locked_positions = {}
    grid = creating_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_the_shape() #gets the current shape  
    next_piece = get_the_shape() #gets next shape 
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0 
    score = 0 #the game starts with 0 

    #as time goes on, the games get more difficult 
    while run:
        grid = creating_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005
                
        #piece falling codes 
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_spaces(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: #move shape to the left
                    current_piece.x -= 1
                    if not(valid_spaces(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT: #move shape to the right 
                    current_piece.x += 1
                    if not(valid_spaces(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN: #move shape down 
                    current_piece.y += 1
                    if not(valid_spaces(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP: #rotates the shape 
                    current_piece.rotation += 1
                    if not(valid_spaces(current_piece, grid)):
                        current_piece.rotation -= 1

        shape_pos = conversion_shape_format(current_piece)
        #adding colour of the piece to the grid for drawing 
        for v in range(len(shape_pos)):
            x, y = shape_pos[v]
            if y > -1:
                grid[y][x] = current_piece.color
        #if the piece hits the grounds 
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_the_shape()
            change_piece = False
            score += clearing_rows(grid, locked_positions) * 10 

        drawing_window(win, grid, score, last_score)
        next_shape(next_piece, win)
        pygame.display.update()

        #checks if the users has lost 
        if check_lost(locked_positions):
            text_middle(win, "YOU LOST!", 80, (255,0,0))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_scores(score)
            mixer.music.stop() #the music stops 

#when the game launched, the users can press any button to start the game 
def main_menu(win):  
    run = True
    while run:
        win.fill((0,0,0))
        text_middle(win, 'Press Any Key To Play', 60, (255,255,255))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()

#setting the pygame window and giving it caption 
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tetris')
main_menu(win)

