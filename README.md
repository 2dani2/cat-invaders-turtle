<div align="center">

# 🐱 Cat Invaders

**A Space Invaders twist in Python: defend your ship against waves of cats, collect hearts, beat the boss, and climb the leaderboard.**

![Language](https://img.shields.io/badge/python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Graphics](https://img.shields.io/badge/graphics-turtle-ff69b4?style=for-the-badge)
![Audio](https://img.shields.io/badge/audio-pygame-green?style=for-the-badge)
![Status](https://img.shields.io/badge/status-playable-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge)

[Features](#-features) • [Controls](#-controls) • [Getting Started](#-getting-started) • [How It Works](#-how-it-works) • [Roadmap](#%EF%B8%8F-roadmap)

</div>

---

## 📖 About

Cat Invaders is an arcade shooter built with Python's `turtle` module for graphics and `pygame` for sound. Pick your ship and your enemy skin, shoot down a 30-cat invasion, survive their return fire, and take on a 50-HP boss that throws lightning bolts.

Beyond the gameplay, the project includes a **save/load system** and a persistent **Top 10 leaderboard**, both stored in plain-text files.

## ✨ Features

| | Feature | Details |
|---|---|---|
| 🎨 | **Skin selection** | 5 ship colours and 5 cat breeds, chosen from a clickable menu |
| 👾 | **Enemy waves** | A 3×10 grid of cats that drift sideways, fall, randomly change direction and shoot back |
| 👹 | **Boss fight** | Appears when the grid is cleared: 50 HP, fast horizontal patrol, lightning attacks |
| ❤️ | **Lives and power-ups** | Start with 3 lives (max 5); enemies have a 10% chance to drop a heart |
| 💾 | **Save and load** | Save mid-game with one key and resume later from a text file |
| 🏆 | **Top 10 leaderboard** | Persistent high scores, with name entry when you make the cut |
| 🔊 | **Sound effects** | Shooting, game over and victory audio, with graceful fallback if files are missing |

## 🎮 Controls

| Key | Action |
|---|---|
| `←` / `→` | Move left / right |
| `Space` | Shoot |
| `G` | Save game |
| `Esc` | Quit and record score |

**Win** by defeating the boss. **Lose** by running out of lives, colliding with a cat, or letting one reach the bottom.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pygame`
- The **Monocraft** font installed, for the on-screen score text

### Install & run

```bash
# Clone the repository
git clone https://github.com/<your-username>/cat-invaders.git
cd cat-invaders

# Install the dependency
pip install pygame

# Play
python space_invaders_game.py
```

On launch you will:
1. Click a **ship skin**, then an **enemy skin**
2. Press **Enter** for a new game, or type a save file name (e.g. `savegamegame.txt`) to resume

### Assets

The game expects these files in the same folder as the script:

```
player_<colour>.gif       menu_player_<colour>.gif      # blue, purple, green, yellow, red
<breed>_cat.gif           menu_<breed>_cat.gif          # black, calico, orange, siames, tuxedo
boss.gif   relampago.gif  heart.gif
pew.mp3    gameover.MP3   win.mp3
```

## 🧠 How It Works

### Architecture

The game is driven by a single **shared state dictionary** and a fixed-rate main loop (~60 FPS). Each frame runs a sequence of small, single-purpose update functions:

```
atualizar_balas_player  →  atualizar_balas_inimigos  →  atualizar_hearts_drop
        →  atualizar_inimigos  →  inimigos_disparam  →  atualizar_boss
        →  verificar_colisoes (player bullets / enemy bullets / direct hit / bottom)
        →  screen.update()
```

### Design decisions

- **Entity factories.** `criar_entidade` and `criar_bala` build every ship, enemy, boss, projectile and power-up from a type string, keeping creation logic in one place.
- **Distance-based collision detection** using a single `COLLISION_RADIUS` constant, easy to tune.
- **Centralised tuning.** Speeds, spacing, fire probability, boss health and lives are named constants at the top of the file.
- **Manual render control.** `screen.tracer(0)` plus an explicit `screen.update()` per frame gives smooth, flicker-free animation.
- **Event-driven input.** Key handlers are bound through the turtle screen and are unbound on game over so no input leaks through.
- **State machine for game flow.** An `is_game_over` flag cleanly separates the playing, win and lose states.
- **Serialisation to text.** The save format is a simple `KEY:value` file covering score, lives, positions of the player, enemies and bullets.
- **Resilient resource loading.** Missing sounds or sprites print a clear message instead of crashing the game.

## 💾 File Formats

**Leaderboard** (`highscoresgame.txt`), one entry per line:

```text
1250,Ana
980,Bruno
```

**Save file** (`savegamegame.txt`):

```text
SCORE:340
LIVES:3
PLAYER_X:-40.0
ENEMIES:x,y,dir;x,y,dir;...
PLAYER_BULLETS:x,y;x,y
ENEMY_BULLETS:x,y
HEARTS_FALLING:x,y
BOSS_SPAWNED:False
```

## 📁 Project Structure

```
.
├── space_invaders_game.py   # Game logic, UI, save/load and highscores
├── *.gif                    # Player, enemy, boss, heart and projectile sprites
├── *.mp3                    # Sound effects
├── highscoresgame.txt       # Leaderboard (created on first score)
├── savegamegame.txt         # Save file (created when you press G)
└── README.md
```

## 🛣️ Roadmap

- [x] Skin selection menu
- [x] Enemy grid with randomised movement and shooting
- [x] Boss fight with ranged attacks
- [x] Lives, heart drops and HUD
- [x] Save / load system
- [x] Persistent Top 10 leaderboard
- [ ] Restore falling hearts and boss state from saves
- [ ] In-game name entry instead of the terminal prompt
- [ ] Multiple levels with increasing difficulty
- [ ] Split into modules (entities, game loop, persistence)

## 🧰 Tech Stack

| Area | Details |
|---|---|
| **Language** | Python 3 |
| **Libraries** | `turtle` (graphics, input, animation), `pygame.mixer` (audio) |
| **Concepts** | Game loop, state management, event handling, collision detection, entity creation patterns |
| **I/O** | File reading/writing, custom text serialisation, parsing |
| **Practices** | Constants-driven configuration, small single-purpose functions, error handling, graceful degradation |
| **Tooling** | Git, command line |

## 🤝 Contributing

Suggestions and pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the project
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

## 👤 Author

**Daniela Silva**
[GitHub](https://github.com/2dani2) • [LinkedIn](https://linkedin.com/in/daniela-maria-marcelo-silva)

<div align="center">

⭐ If you enjoyed the game, consider giving it a star!

</div>
