# é necessário instalar a fonte MONOCRAFT para ver o texto corretamente

import turtle
import random
import time
import os
import sys
import pygame

pygame.init()

# =========================
# Configurações e Constantes
# =========================
LARGURA, ALTURA = 600, 900
BORDA_X = (LARGURA // 2) - 20
BORDA_Y = (ALTURA // 2) - 10

PLAYER_SPEED = 20
PLAYER_BULLET_SPEED = 16
ENEMY_ROWS = 3
ENEMY_COLS = 10
ENEMY_SPACING_X = 50
ENEMY_SPACING_Y = 60
ENEMY_SIZE = 32
ENEMY_START_Y = BORDA_Y - ENEMY_SIZE - 50
ENEMY_FALL_SPEED = 0.5
ENEMY_DRIFT_STEP = 2
ENEMY_FIRE_PROB = 0.006
ENEMY_INVERT_CHANCE = 0.05

BOSS_SPEED = 5
BOSS_HEALTH = 50

COLLISION_RADIUS = 40
HIGHSCORES_FILE = "highscoresgame.txt"
SAVE_FILE = "savegamegame.txt"
TOP_N = 10
MAX_LIVES = 5

STATE = None
PLAYER_GIF = None
ENEMY_GIF = None
BOSS_GIF = "boss.gif"
RELAMPAGO_GIF = "relampago.gif"
HEART_GIF = "heart.gif"

# =========================
# Sons
# =========================
try:
    pewpew = pygame.mixer.Sound('pew.mp3')
except pygame.error as e:
    print(f"Erro ao carregar som: {e}")
    pewpew = None

try:
    game_over_sound = pygame.mixer.Sound('gameover.MP3')
except pygame.error as e:
    print(f"Erro ao carregar som: {e}")
    game_over_sound = None

try:
    win_sound = pygame.mixer.Sound('win.mp3')
except pygame.error as e:
    print(f"Erro ao carregar som: {e}")
    win_sound = None

# =========================
# Skins
# =========================
player_colors = ["blue", "purple", "green", "yellow", "red"]
enemy_colors = ["black", "calico", "orange", "siames", "tuxedo"]

menu_player_files = [f"menu_player_{c}.gif" for c in player_colors]
menu_enemy_files = [f"menu_{c}_cat.gif" for c in enemy_colors]

game_player_files = [f"player_{c}.gif" for c in player_colors]
game_enemy_files = [f"{c}_cat.gif" for c in enemy_colors]


def check_and_add_shape(screen, file_name):
    if os.path.exists(file_name):
        screen.addshape(file_name)
    else:
        print(f"ERRO: ficheiro {file_name} não encontrado!")


def escolher_skin(screen, tipo, menu_files):
    escolhido = None
    turtles = []
    y_start = 200
    y = y_start
    for f in menu_files:
        t = turtle.Turtle(visible=False)
        check_and_add_shape(screen, f)
        t.shape(f)
        t.penup()
        t.setposition(0, y)
        t.showturtle()
        turtles.append((t, f))
        y -= 100

    def click_handler(x, y):
        nonlocal escolhido
        for t, f in turtles:
            if t.distance(x, y) < 50:
                escolhido = f

    screen.onscreenclick(click_handler)
    while not escolhido:
        screen.update()
        time.sleep(0.01)
    for t, _ in turtles:
        t.hideturtle()
    screen.onscreenclick(None)

    if tipo == "player":
        color = escolhido.split("_")[-1].split(".")[0]
        return f"player_{color}.gif"
    else:
        color = escolhido.split("_")[1].split(".")[0]
        return f"{color}_cat.gif"

# =========================
# Highscores
# =========================


def ler_highscores(filename):
    highscores = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                score_str, name = line.strip().split(',')
                highscores.append((int(score_str), name))
    highscores.sort(key=lambda x: x[0], reverse=True)
    return highscores


def atualizar_highscores(filename, score):
    highscores = ler_highscores(filename)
    if len(highscores) < TOP_N or score > highscores[-1][0]:
        print(f"\nParabéns! Entrou no Top {TOP_N}!")
        player_name = input("Introduza o seu nome: ").strip()
        highscores.append((score, player_name))
        highscores.sort(key=lambda x: x[0], reverse=True)
        highscores = highscores[:TOP_N]
        with open(filename, 'w') as f:
            for s, n in highscores:
                f.write(f"{s},{n}\n")
        print(f"Highscore de {score} registado para {player_name}.")
    else:
        print(
            f"\nO seu score de {score} não foi suficiente para o Top {TOP_N}.")

# =========================
# Save/Load
# =========================


def guardar_estado_txt(filename, state):
    with open(filename, 'w') as f:
        f.write(f"SCORE:{state['score']}\n")
        f.write(f"LIVES:{state['player_lives']}\n")
        if state['player']:
            f.write(f"PLAYER_X:{state['player'].xcor()}\n")
        enemy_data = []
        for e in state['enemies']:
            dir = e.dx/ENEMY_DRIFT_STEP if ENEMY_DRIFT_STEP != 0 else 1
            enemy_data.append(f"{e.xcor()},{e.ycor()},{dir}")
        hearts_falling = []
        for h in state['hearts']:
            hearts_falling.append(f"{h.xcor()},{h.ycor()}")

        f.write(f"ENEMIES:{';'.join(enemy_data)}\n")
        bullets_p = [f"{b.xcor()},{b.ycor()}" for b in state["player_bullets"]]
        f.write(f"PLAYER_BULLETS:{';'.join(bullets_p)}\n")
        bullets_e = [f"{b.xcor()},{b.ycor()}" for b in state["enemy_bullets"]]
        f.write(f"ENEMY_BULLETS:{';'.join(bullets_e)}\n")
        f.write(f"LIVES:{state['player_lives']}\n")
        f.write(f"HEARTS_FALLING:{';'.join(hearts_falling)}\n")
        f.write(f"BOSS_SPAWNED:{state['boss_spawned']}\n")
    print(f"Estado guardado em '{filename}'.")


def carregar_estado_txt(filename):
    if not os.path.exists(filename):
        return None
    loaded = {"score": 0, "player_x": 0, "enemies": [],
              "player_bullets": [], "enemy_bullets": [], "player_lives": 3}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            key, value = line.split(":", 1)
            if key == "SCORE":
                loaded["score"] = int(value)
            elif key == "LIVES":
                loaded["player_lives"] = int(value)
            elif key == "PLAYER_X":
                loaded["player_x"] = float(value)
            elif key == "ENEMIES" and value:
                for e_str in value.split(";"):
                    x, y, d = e_str.split(",")
                    loaded["enemies"].append((float(x), float(y), float(d)))
            elif key == "PLAYER_BULLETS" and value:
                for b_str in value.split(";"):
                    x, y = b_str.split(",")
                    loaded["player_bullets"].append((float(x), float(y)))
            elif key == "ENEMY_BULLETS" and value:
                for b_str in value.split(";"):
                    x, y = b_str.split(",")
                    loaded["enemy_bullets"].append((float(x), float(y)))
            elif key == "HEARTS_FALLING" and value:
                for h_str in value.split(";"):
                    x, y = h_str.split(",")
                    try:
                        loaded["hearts_falling"].append((float(x), float(y)))
                    except KeyError:
                        return None
            elif key == "BOSS_SPAWNED":
                loaded["boss_spawned"] = value.lower() == "true"

    print(f"Estado carregado de '{filename}'.")
    return loaded

# =========================
# Criação de entidades
# =========================


def criar_entidade(x, y, tipo):
    t = turtle.Turtle(visible=False)
    t.penup()
    if tipo == "player":
        t.shape(PLAYER_GIF)
    elif tipo == "enemy":
        t.shape(ENEMY_GIF)
    elif tipo == "boss":
        t.shape(BOSS_GIF)
    t.setposition(x, y)
    t.showturtle()
    return t


def criar_bala(x, y, tipo):
    t = turtle.Turtle(visible=False)
    t.penup()
    if tipo == "bala_player":
        t.shape("turtle")
        t.color("yellow")
        t.shapesize(0.5, 1)
        t.setheading(90)
    elif tipo == "bala_enemy":
        t.shape("triangle")
        t.color("red")
        t.shapesize(0.5, 1)
        t.setheading(270)
    elif tipo == "relampago":
        t.shape(RELAMPAGO_GIF)
        t.setheading(270)
    elif tipo == "heart":
        t.shape(HEART_GIF)
        t.setheading(270)
        t.shapesize(1, 1)
    t.setposition(x, y)
    t.showturtle()
    return t


def spawn_inimigos_em_grelha(state, posicoes_existentes=None, dirs_existentes=None):
    enemies = []
    if posicoes_existentes:
        for i, (x, y) in enumerate(posicoes_existentes):
            e = criar_entidade(x, y, "enemy")
            e.dx = dirs_existentes[i] * \
                ENEMY_DRIFT_STEP if dirs_existentes else ENEMY_DRIFT_STEP
            enemies.append(e)
    else:
        x_start = -BORDA_X + ENEMY_SIZE/2
        for r in range(ENEMY_ROWS):
            for c in range(ENEMY_COLS):
                x = x_start + c*ENEMY_SPACING_X
                y = ENEMY_START_Y - r*ENEMY_SPACING_Y
                e = criar_entidade(x, y, "enemy")
                e.dx = ENEMY_DRIFT_STEP
                enemies.append(e)
    state["enemies"] = enemies
    return enemies


def restaurar_balas(state, lista_pos, tipo):
    if tipo == "bala_player":
        target = state["player_bullets"]
    elif tipo == "bala_enemy":
        target = state["enemy_bullets"]
    else:
        return
    for x, y in lista_pos:
        target.append(criar_bala(x, y, tipo))


def spawn_heart(state, x, y):
    h = criar_bala(x, y, "heart")
    state["hearts_drop"].append(h)

# =========================
# UI Score e Hearts
# =========================


def criar_ui(state):
    t = turtle.Turtle(visible=False)
    t.penup()
    t.color("white")
    t.setposition(BORDA_X, BORDA_Y-50)
    t.hideturtle()
    state["score_display"] = t
    atualizar_score(state)
    state["hearts"] = []
    atualizar_hearts(state)
    state["hearts_drop"] = []


def atualizar_score(state):
    t = state["score_display"]
    t.clear()
    t.write(f"Score: {state['score']}", align="right",
            font=("Monocraft", 16, "normal"))


def atualizar_hearts(state):
    for h in state["hearts"]:
        h.hideturtle()
    state["hearts"].clear()
    for i in range(state["player_lives"]):
        h = turtle.Turtle(visible=False)
        h.shape(HEART_GIF)
        h.penup()
        h.setposition(-BORDA_X+20+i*35, BORDA_Y-40)
        h.showturtle()
        state["hearts"].append(h)


def criar_texto(x, y, texto, cor, tamanho, estilo="normal"):
    t = turtle.Turtle(visible=False)
    t.penup()
    t.color(cor)
    t.goto(x, y)
    t.write(texto, align="center", font=("Courier", tamanho, estilo))
    return t


def game_over_sequence(reason):
    global STATE
    if STATE["is_game_over"]:
        return
    STATE["is_game_over"] = True
    print(f"Game Over! Razão: {reason}", flush=True)
    STATE["screen"].onkeypress(None, "Left")
    STATE["screen"].onkeypress(None, "Right")
    STATE["screen"].onkeypress(None, "space")
    STATE["player"].hideturtle()
    for inimigo in STATE["enemies"]:
        inimigo.hideturtle()
    for bala in STATE["player_bullets"] + STATE["enemy_bullets"]:
        bala.hideturtle()
    if game_over_sound:
        game_over_sound.play()
    STATE["game_over_text"] = criar_texto(
        0, 50, "GAME OVER", "red", 60, "bold")
    STATE["score_text"] = criar_texto(
        0, -50, f"Score: {STATE['score']}", "white", 30)
    terminar_handler()


def win_sequence(reason):
    global STATE
    if STATE["is_game_over"]:
        return
    STATE["is_game_over"] = True
    print(f"Vitória! Razão: {reason}", flush=True)
    STATE["screen"].onkeypress(None, "Left")
    STATE["screen"].onkeypress(None, "Right")
    STATE["screen"].onkeypress(None, "space")
    STATE["player"].hideturtle()
    for inimigo in STATE["enemies"]:
        inimigo.hideturtle()
    for bala in STATE["player_bullets"] + STATE["enemy_bullets"]:
        bala.hideturtle()
    if win_sound:
        win_sound.play()
    criar_texto(0, 80, "YOU WIN!", "green", 60, "bold")
    criar_texto(0, 0, f"Score: {STATE['score']}", "white", 30)
    terminar_handler()
# =========================
# Handlers de tecla
# =========================


def mover_esquerda_handler():
    global STATE
    if STATE["is_game_over"]:
        return
    player = STATE.get("player")
    nx = player.xcor() - PLAYER_SPEED
    if nx < -BORDA_X:
        nx = -BORDA_X
    player.setx(nx)


def mover_direita_handler():
    global STATE
    if STATE["is_game_over"]:
        return
    player = STATE.get("player")
    nx = player.xcor() + PLAYER_SPEED
    if nx > BORDA_X:
        nx = BORDA_X
    player.setx(nx)


def disparar_handler():
    global STATE
    if STATE["is_game_over"]:
        return
    player = STATE.get("player")
    x = player.xcor()
    y = player.ycor() + 20
    b = criar_bala(x, y, "bala_player")
    STATE["player_bullets"].append(b)
    if pewpew:
        pewpew.play()


def gravar_handler():
    global STATE
    guardar_estado_txt(STATE["files"]["save"], STATE)


def terminar_handler():
    global STATE
    STATE["screen"].onkeypress(None, "Left")
    STATE["screen"].onkeypress(None, "Right")
    STATE["screen"].onkeypress(None, "space")
    STATE["screen"].onkeypress(None, "g")
    final_score = STATE["score"]
    print("\n--- JOGO TERMINADO ---")
    print(f"Sua Pontuação Final: {final_score}")
    atualizar_highscores(STATE["files"]["highscores"], final_score)
    screen.bye()

# =========================
# Atualizações do jogo
# =========================


def atualizar_balas_player(state):
    novas_balas = []
    for b in state["player_bullets"]:
        b.sety(b.ycor() + PLAYER_BULLET_SPEED)
        if b.ycor() <= BORDA_Y + 20:
            novas_balas.append(b)
        else:
            b.hideturtle()
    state["player_bullets"] = novas_balas


def atualizar_balas_inimigos(state):
    novas = []
    for b in state["enemy_bullets"]:
        b.sety(b.ycor() - PLAYER_BULLET_SPEED)
        if b.ycor() >= -BORDA_Y-20:
            novas.append(b)
        else:
            b.hideturtle()
    state["enemy_bullets"] = novas


def atualizar_hearts_drop(state):
    novas = []
    player = state["player"]
    for h in state["hearts_drop"]:
        h.sety(h.ycor()-3)
        if h.distance(player) < COLLISION_RADIUS:
            h.hideturtle()
            if state["player_lives"] < MAX_LIVES:
                state["player_lives"] += 1
                atualizar_hearts(state)
        elif h.ycor() > -BORDA_Y:
            novas.append(h)
        else:
            h.hideturtle()
    state["hearts_drop"] = novas


def atualizar_inimigos(state):
    for e in state["enemies"]:
        e.sety(e.ycor()-ENEMY_FALL_SPEED)
        e.setx(e.xcor()+e.dx)
        if e.xcor() >= BORDA_X or e.xcor() <= -BORDA_X:
            e.dx *= -1
        if random.random() < ENEMY_INVERT_CHANCE:
            e.dx *= -1


def inimigos_disparam(state):
    for e in state["enemies"]:
        if random.random() < ENEMY_FIRE_PROB:
            state["enemy_bullets"].append(criar_bala(
                e.xcor(), e.ycor()-20, "bala_enemy"))


def verificar_colisoes_player_bullets(state):
    novos_inimigos = []
    for e in state["enemies"]:
        atingido = False
        for b in state["player_bullets"]:
            if b.distance(e) < COLLISION_RADIUS:
                b.hideturtle()
                e.hideturtle()
                atingido = True
                state["score"] += 10
                if random.random() < 0.1:
                    spawn_heart(state, e.xcor(), e.ycor())
        if not atingido:
            novos_inimigos.append(e)
    state["enemies"] = novos_inimigos
    atualizar_score(state)


def verificar_colisoes_enemy_bullets(state):
    player = state["player"]
    novas_balas = []
    for b in state["enemy_bullets"]:
        if b.distance(player) < COLLISION_RADIUS:
            b.hideturtle()
            state["player_lives"] -= 1
            atualizar_hearts(state)
            if state["player_lives"] <= 0:
                game_over_sequence("Perdeste todas as vidas!")
        else:
            novas_balas.append(b)
    state["enemy_bullets"] = novas_balas


def inimigo_chegou_ao_fundo(state):
    return any(e.ycor() <= -320 for e in state["enemies"])


def verificar_colisao_player_com_inimigos(state):
    player = state["player"]
    for e in state["enemies"]:
        if player.distance(e) < COLLISION_RADIUS:
            state["player_lives"] = 0
            atualizar_hearts(state)
            return True
    return False

# =========================
# Boss
# =========================


def spawn_boss(state):
    if state.get("boss_spawned"):
        return
    b = criar_entidade(0, ENEMY_START_Y - 100, "boss")
    b.dx = BOSS_SPEED
    b.health = BOSS_HEALTH
    state["boss"] = b
    state["boss_spawned"] = True


def atualizar_boss(state):
    if not state.get("boss"):
        return
    b = state["boss"]
    b.setx(b.xcor() + b.dx)
    if b.xcor() >= BORDA_X or b.xcor() <= -BORDA_X:
        b.dx *= -1
    novas_balas = []
    for pb in state["player_bullets"]:
        if pb.distance(b) < COLLISION_RADIUS:
            pb.hideturtle()
            b.health -= 1
            state["score"] += 20
        else:
            novas_balas.append(pb)
    state["player_bullets"] = novas_balas
    if random.random() < 0.05:
        state["enemy_bullets"].append(
            criar_bala(b.xcor(), b.ycor()-20, "relampago"))

    if b.health <= 0:
        b.hideturtle()
        state["boss"] = None
        win_sequence("Parabéns! Boss derrotado!")
        return


# =========================
# Execução Principal
# =========================
if __name__ == "__main__":
    screen = turtle.Screen()
    screen.title("Space Invaders IPRP")
    screen.bgcolor("black")
    screen.setup(width=LARGURA, height=ALTURA)
    screen.tracer(0)

    # Adicionar shapes de jogo
    for f in game_player_files + game_enemy_files + [BOSS_GIF, RELAMPAGO_GIF, HEART_GIF]:
        check_and_add_shape(screen, f)

    # Menu visual de skins
    PLAYER_GIF = escolher_skin(screen, "player", menu_player_files)
    ENEMY_GIF = escolher_skin(screen, "enemy", menu_enemy_files)

    # Carregar jogo
    filename = input(
        "Carregar jogo? Enter para novo ou nome do ficheiro: ").strip()
    loaded = carregar_estado_txt(filename) if filename else None

    # Estado do jogo
    state = {"screen": screen,
             "player": None,
             "enemies": [],
             "player_bullets": [],
             "enemy_bullets": [],
             "score": 0,
             "player_lives": 3,
             "hearts": [],
             "score_display": None,
             "frame": 0,
             "files": {"highscores": HIGHSCORES_FILE, "save": SAVE_FILE},
             "is_game_over": False,
             "game_over_text": None,
             "score_text": None,
             "hearts_drop": [],
             "boss": None,
             "boss_spawned": False}

    if loaded:
        state["score"] = loaded["score"]
        state["player_lives"] = loaded["player_lives"]
        state["player"] = criar_entidade(loaded["player_x"], -350, "player")
        enemy_positions = [(x, y) for x, y, _ in loaded["enemies"]]
        enemy_dirs = [d for _, _, d in loaded["enemies"]]
        spawn_inimigos_em_grelha(state, enemy_positions, enemy_dirs)
        restaurar_balas(state, loaded["player_bullets"], "bala_player")
        restaurar_balas(state, loaded["enemy_bullets"], "bala_enemy")
    else:
        state["player"] = criar_entidade(0, -350, "player")
        spawn_inimigos_em_grelha(state)

    criar_ui(state)
    STATE = state

    # Teclas
    screen.listen()
    screen.onkeypress(mover_esquerda_handler, "Left")
    screen.onkeypress(mover_direita_handler, "Right")
    screen.onkeypress(disparar_handler, "space")
    screen.onkeypress(gravar_handler, "g")
    screen.onkeypress(terminar_handler, "Escape")

    # Loop principal
    while True:
        if STATE["is_game_over"]:
            STATE["screen"].update()
            time.sleep(0.016)
            continue

        atualizar_balas_player(state)
        atualizar_balas_inimigos(state)
        atualizar_hearts_drop(state)
        atualizar_inimigos(state)
        inimigos_disparam(state)

        if len(state["enemies"]) == 0 and not state.get("boss_spawned"):
            spawn_boss(state)

        atualizar_boss(state)
        verificar_colisoes_player_bullets(state)
        verificar_colisoes_enemy_bullets(state)
        if not STATE["is_game_over"]:
            if verificar_colisao_player_com_inimigos(STATE):
                game_over_sequence("Colisão direta com inimigo!")
            if inimigo_chegou_ao_fundo(STATE):
                game_over_sequence("Um inimigo chegou ao fundo!")
        state["frame"] += 1
        screen.update()
        time.sleep(0.016)
