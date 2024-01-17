import numpy as np
import pygame
import sys
import math
from requests import post, get
import json
from tkinter import simpledialog, messagebox
from threading import Thread

server = "https://connect4two.onrender.com"

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
 
ROW_COUNT = 6
COLUMN_COUNT = 7
 
def drop_piece(board, row, col, piece):
    board[row][col] = piece
 
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0
 
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
 
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
 
    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
 
    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
 
    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
 
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
     
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):      
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

id = 0
board = []
game_over = False
turn = 0
winner = 0

code = simpledialog.askstring("Join a Game", "Enter a Join-Code (Press Cancel for new Game):")
if not code:
    code = ""
else:
    code = code.strip()

def show_code():
    global code
    messagebox.showinfo("Your Join-Code", code)

def create_game():
    global code, id

    resp = get(server + "/create")
    jresp = json.loads(resp.text)
    id = jresp.get("playerid")
    code = jresp.get("join_code")

def join():
    global id

    resp = get(server + f"/{code}/join")
    id = json.loads(resp.text).get('playerid')

def sync():
    global board, game_over, turn, winner

    resp = get(server + f"/{code}/sync")
    jresp = json.loads(resp.text)

    board = np.asarray(jresp.get('board'))
    game_over = jresp.get('gameover')
    turn = jresp.get('turn')
    winner = jresp.get('winner')

def update(b):
    post(server + f"/{code}/update", json={"playerid": id, "board": b.tolist()})

def gameover(winner):
    post(server + f"/{code}/gameover", json={"winner": winner})

#initalize pygame
pygame.init()
 
#define our screen size
SQUARESIZE = 100
 
#define width and height of board
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
 
size = (width, height)
 
RADIUS = int(SQUARESIZE/2 - 5)
 
screen = pygame.display.set_mode(size)
pygame.display.update()
 
myfont = pygame.font.SysFont("monospace", 75)

first = True

while True:
    id = 0
    board = []
    game_over = False
    turn = 0
    winner = 0
    delay = 1000

    if code == "":
        create_game()
        print("Your Join-Code:", code)
    else:
        join()
    sync()

    if first:
        Thread(target=show_code).start()
        first = False

    screen.fill(BLACK)
    pygame.display.update()

    label = myfont.render(f"Player {id}", 1, BLUE)
    screen.blit(label, (40,10))
    pygame.display.update()

    while turn == 0:
        sync()
        pygame.time.wait(500)

    pygame.time.wait(5000)

    while not game_over:

        if delay <= 0:
            sync()
            delay = 1000
        delay -= 1

        for event in pygame.event.get(): 
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn != 0:
                    if turn == id:
                        if id == 1:
                            pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                        else:
                            pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
                    else: 
                        if id == 1:
                            pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                        else:
                            pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
                

            pygame.display.update()
    
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                #print(event.pos)
                # Ask for Player Input
                if turn == id:
                    localboard = board
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))
    
                    if is_valid_location(localboard, col):
                        row = get_next_open_row(localboard, col)
                        drop_piece(localboard, row, col, id)

                        if winning_move(localboard, id):
                            gameover(id)

                        update(localboard)
                    
        draw_board(board)

    if game_over:
        if winner != 0:
            label = myfont.render(f"Player {winner} wins!", 1, RED if winner == 1 else YELLOW)
            screen.blit(label, (40,10))
            pygame.display.update()
        else:
            label = myfont.render(f"No winner!", 1, BLUE)
            screen.blit(label, (40,10))
            pygame.display.update()
    
    pygame.time.wait(3000)