# Graphical Shooter Game

By Rogie P. Bacanto

By Rogie P. Bacanto

This is a 2D top-down space shooter game built with Python and the Pygame library. It features dynamic gameplay that gets progressively harder, power-ups, and a separate UI editor to customize game settings.

## Features

*   **Graphical Interface:** A full 2D game experience with graphics for the player, enemies, and effects.
*   **Settings Editor:** A separate UI (`editor.py`) built with Tkinter to easily change game settings like player lives, speed, and more without touching the code.
*   **Dynamic Difficulty:** The game gets harder as your score increases. Enemies spawn more frequently and move faster.
*   **Power-Ups:** Chance for a "Triple Shot" power-up to drop from destroyed enemies.
*   **Sound Effects:** Audio feedback for shooting, explosions, and taking damage.
*   **Visual Polish:** Includes a main menu, explosion animations, and a scrolling background.

## How to Play (PC with Visual Studio Code)

### Step 1: Install Required Software

1.  **Python:** Ensure you have Python installed. You can get it from [python.org](https://www.python.org/downloads/). Make sure to check "Add Python to PATH" during installation.
2.  **Git:** (Optional, for cloning) You can use Git to clone the repository.

### Step 2: Set Up the Project

1.  Download or clone the repository to your PC.
2.  Open a terminal or command prompt in the project's root directory (`graphical_shooter_game`).
3.  Install the necessary Python library, **Pygame**:
    ```bash
    pip install pygame
    ```

### Step 3: Run the Game or Editor

*   **To play the game**, run the `main.py` file:
    ```bash
    python main.py
    ```

*   **To change game settings**, run the `editor.py` file. This will open a UI where you can modify the settings and save them.
    ```bash
    python editor.py
    ```

## Controls

*   `Arrow Keys`: Move the player ship left and right.
*   `Spacebar`: Shoot bullets.
