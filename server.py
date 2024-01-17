import numpy as np
from requests import get
from fastapi import FastAPI, Request
from random import randint
from apscheduler.schedulers.background import BackgroundScheduler
import time

ROW_COUNT = 6
COLUMN_COUNT = 7

games = {}

def cleanup_games():
    for k in games.keys():
        if ((time.time() * 1000) - games[k].get('accessTime')) > 300000:
            print("Closed Game:", k)
            del games[k]

def request():
    try:
        get("https://connect4two.onrender.com")
    except:
        print("Failed to send Request")

scheduler = BackgroundScheduler()
scheduler.add_job(func=request, trigger="interval", seconds=300)
scheduler.start()

def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board.tolist()

def get_joincode():
    return ''.join([ str(randint(0, 9)) for _ in range(0, 6)])

app = FastAPI()

@app.get('/')
async def index():
    cleanup_games()
    return {"active_games": len(games.keys())}

@app.get('/create')
async def create():
    global games
    code = get_joincode()
    game_obj = {
        "gameover": False,
        "players": 1,
        "winner": 0,
        "turn": 0,
        "board": create_board(),
        "accessTime": time.time() * 1000
    }
    games[code] = game_obj

    return {"join_code": code, "playerid": 1}

@app.get('/{code}/join')
async def join(code: str):
    global games

    game_obj = games.get(code)
    if not game_obj:
        return {"status": "FAILED"} 

    if game_obj.get("gameover"):
        game_obj["gameover"] = False
        game_obj["players"] = 0
        game_obj["winner"] = 0
        game_obj["turn"] = 0
        game_obj["board"] = create_board()
        game_obj["accessTime"] = time.time() * 1000

    game_obj["players"] += 1

    if game_obj.get("players") >= 2:
        game_obj["players"] = 2
        game_obj["turn"] = 1

    return {"playerid": game_obj.get("players")}

@app.get('/{code}/sync')
async def sync(code: str):
    global games
    game_obj = games.get(code)
    if not game_obj:
        return {"status": "FAILED"}
    game_obj["accessTime"] = time.time() * 1000
    return game_obj

@app.post('/{code}/update')
async def update(code: str, request: Request):
    global games
    
    game_obj = games.get(code)
    if not game_obj:
        return {"status": "FAILED"}
    game_obj["accessTime"] = time.time() * 1000

    jbody = await request.json()
    playerid = jbody.get('playerid')
    game_obj["board"] = jbody.get('board')

    if playerid == 1:
        game_obj["turn"] = 2
    elif playerid == 2:
        game_obj["turn"] = 1

    return {"status": "OK"}

@app.post('/{code}/gameover')
async def win(code: str, request: Request):
    global games

    game_obj = games.get(code)
    if not game_obj:
        return {"status": "FAILED"}
    game_obj["accessTime"] = time.time() * 1000

    jbody = await request.json()
    winner = jbody.get('winner')

    game_obj["winner"] = winner
    game_obj["gameover"] = True

    return {"status": "OK"}