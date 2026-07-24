# CSE423 Computer Graphics Labs and Project

This repository contains the lab assignments and the final project for the CSE423 Computer Graphics course. All implementations are created using Python and the PyOpenGL library.

## Table of Contents
- [Lab 1: Basic Animations and Interactions](#lab-1-basic-animations-and-interactions)
  - [Task 1: Animated 2D Scenery](#task-1-animated-2d-scenery)
  - [Task 2: The Amazing Box](#task-2-the-amazing-box)
- [Lab 2: Diamond Catcher Game](#lab-2-diamond-catcher-game)
- [Lab 3: 3D Shooter Game](#lab-3-3d-shooter-game)
- [Project: TRAIM - A 3D Aim Trainer](#project-traim---a-3d-aim-trainer)
- [Technologies Used](#technologies-used)
- [How to Run](#how-to-run)

## Lab 1: Basic Animations and Interactions

This lab focuses on fundamental 2D graphics concepts, including drawing primitives, handling user input, and creating simple animations.

### Task 1: Animated 2D Scenery

This program renders a 2D scene of a house with trees and a pathway. It features an animated rain effect and a smooth day-to-night (and vice-versa) transition.

**Features:**
- **Animated Rain:** Raindrops fall from the sky with an adjustable direction.
- **Day/Night Cycle:** The sky color transitions smoothly between day (sky blue) and night (black).
- **Interactive Controls:**
  - `D`: Transition to day time.
  - `N`: Transition to night time.
  - `Left Arrow`: Change the rain's slant to the left.
  - `Right Arrow`: Change the rain's slant to the right.

### Task 2: The Amazing Box

An interactive 2D application where users can create and manipulate colored dots within a confined box.

**Features:**
- **Dynamic Point Creation:** New dots with random colors and diagonal velocities are created at the cursor's position on a right-click.
- **Physics Simulation:** Dots move and bounce off the boundaries of the window.
- **Interactive Controls:**
  - `Right Mouse Click`: Create a new dot.
  - `Left Mouse Click`: Toggle the blinking effect for all dots.
  - `Spacebar`: Freeze or unfreeze the movement of all dots.
  - `Up/Down Arrow Keys`: Increase or decrease the movement speed of the dots.
  - `L Key`: Print the current position and velocity of all dots to the console for debugging.

## Lab 2: Diamond Catcher Game

A 2D "Catch the Diamonds" game where the player controls a catcher to grab falling diamonds. All geometric shapes in the game are rendered using the **Midpoint Line Algorithm**.

**Features:**
- **Gameplay:** The player moves a catcher horizontally to catch diamonds that fall from the top of the screen.
- **Increasing Difficulty:** The falling speed of the diamonds increases as the score goes up.
- **Scoring:** The score increments for each diamond caught.
- **Game Over:** The game ends if a diamond is missed. The catcher turns red to indicate the game-over state.
- **UI Controls:**
  - `Left/Right Arrow Keys`: Move the catcher.
  - **Mouse Click Buttons:**
    - **Restart:** Resets the game to its initial state.
    - **Play/Pause:** Pauses or resumes the game.
    - **Exit:** Closes the game window.

## Lab 3: 3D Shooter Game

A 3D third-person shooter game where the player defends against waves of incoming enemies in a walled arena.

**Features:**
- **3D Environment:** The game takes place in a 3D arena with a checkered floor and colored boundary walls.
- **Player and Enemies:** The player is a humanoid figure who can move and shoot. Enemies are sphere-based characters that chase the player.
- **Camera Modes:** Switch between a third-person and a first-person perspective.
- **Combat System:**
  - Fire bullets to destroy enemies.
  - Enemies damage the player upon collision.
  - The game tracks score, player lives, and the number of missed bullets.
- **Game Over Conditions:** The game ends if the player loses all lives or misses the maximum number of allowed bullets.
- **Cheat Mode:** An auto-aim feature that automatically targets the nearest enemy and can be set to auto-fire.
- **Controls:**
  - `W, A, S, D`: Move and turn the player.
  - `Left Mouse Click`: Fire a bullet.
  - `Right Mouse Click` / `V` (in cheat mode): Toggle between first-person and third-person camera.
  - `C`: Toggle cheat mode.
  - `R`: Restart the game after a game over.
  - `Arrow Keys`: Move the third-person camera manually.

## Project: TRAIM - A 3D Aim Trainer

TRAIM is a comprehensive, feature-rich 3D aim trainer designed to help users improve their aiming skills. It features multiple game modes, customizable settings, and detailed performance feedback.

**Core Features:**
- **Full Menu System:** A navigable main menu to select game modes, time limits, and weapons.
- **Settings Customization:** A dedicated settings screen allows users to adjust:
  - Mouse sensitivity.
  - Target size.
  - Target color.
  - Crosshair color.
- **Multiple Game Modes:**
  - **Timed Modes (Easy, Medium, Hard):** Score as many points as possible within a time limit (30s, 60s, 90s). Difficulty affects target movement, size shrinking, and the number of active targets.
  - **Practice Mode:** Destroy 100 targets with no time limit.
  - **Reaction Mode:** Measures the average time taken to shoot 10 targets after they appear.
  - **Fixed Mode:** Measures the time taken to destroy a fixed set of 10 targets.
- **Diverse Weapon Selection:**
  - **Pistol:** Standard single-shot weapon.
  - **Shotgun:** Fires a spread of 8 pellets per shot.
  - **Sniper:** A long-range rifle with a toggleable scope for precision aiming.
- **Advanced Gameplay Mechanics:**
  - First-person perspective with realistic weapon models.
  - Performance tracking for score, misses, shots fired, and accuracy.
  - Visual effects including bullet tracers and hit-impact sparks.
  - A "Cheat Mode" that provides auto-aim and auto-fire for demonstration.
- **Controls:**
  - `W, A, S, D`: Move the player.
  - `Mouse`: Aim.
  - `Left Mouse Click`: Shoot.
  - `Right Mouse Click`: Toggle scope (with Sniper).
  - `C`: Toggle cheat mode.
  - `M`: Return to the main menu from an active game.
  - `ESC`: Exit the application.

## Technologies Used
- Python
- PyOpenGL & PyOpenGL-accelerate
- GLUT (OpenGL Utility Toolkit)

## How to Run

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/rafitboo/cse423-computer-graphics.git
    cd cse423-computer-graphics
    ```

2.  **Install dependencies:**
    Make sure you have Python installed. Then, install the required libraries using pip.
    ```sh
    pip install PyOpenGL PyOpenGL_accelerate
    ```
    *Note: On some systems, you may also need to install `freeglut`. For example, on Ubuntu/Debian:*
    ```sh
    sudo apt-get install freeglut3-dev
    ```

3.  **Run a specific file:**
    Navigate to the lab or project directory and run the Python script.

    **Example: Running the Final Project**
    ```sh
    python Project/traim.py
    ```

    **Example: Running Lab 2**
    ```sh
    python Lab2/Assignment-2.py
