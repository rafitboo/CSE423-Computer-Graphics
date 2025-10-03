from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import random
import math
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18


# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_SETTINGS = 3
STATE_REACTION = 4
STATE_FIXED = 5

current_state = STATE_MENU

# Game mode constants
PRACTICE_MODE_INDEX = 3
REACTION_MODE_INDEX = 4
FIXED_MODE_INDEX = 5

# Target and scoring constants
PRACTICE_TARGET_GOAL = 100
REACTION_TARGET_GOAL = 10
FIXED_TARGET_GOAL = 10

# Target spawn and behavior constants
TARGET_WALL_Z = -300
TARGET_MAX_X = 250
TARGET_MAX_Y = 200
TARGET_BASE_RADIUS = 20
TARGET_SHRINK_RATE_MEDIUM = 0.1
TARGET_SHRINK_RATE_HARD = 0.3
TARGET_SPAWN_INTERVAL = 2.0
REACTION_SPAWN_DELAY = 1.0

# Visual effects constants
TRACER_DURATION = 0.07
TRACER_LENGTH = 50
HIT_EFFECT_DURATION = 0.2




# MENU AND SETTINGS CONFIGURATION


# Menu options configuration
menu_options = {
    "mode": ["Easy", "Medium", "Hard", "Practice", "Reaction", "Fixed"],
    "time": ["30s", "60s", "90s", "N/A"],
    "weapon": ["Pistol", "Shotgun", "Sniper"]
}

# Menu selection state
selected_mode_idx = 0
selected_time_idx = 0
selected_weapon_idx = 0
menu_cursor_pos = 0

# Settings configuration
settings_options = {
    "sensitivity": [0.001, 0.002, 0.003, 0.004, 0.005],
    "target_size": [0.5, 0.75, 1.0, 1.25, 1.5],
    "target_color": ["Cyan", "Red", "Green", "Yellow", "Purple"],
    "crosshair_color": ["Green", "Cyan", "Red", "Yellow", "Magenta"]
}

# Settings selection state
selected_sensitivity_idx = 1  # Default 0.002
selected_target_size_idx = 2  # Default 1.0
selected_target_color_idx = 0  # Default Cyan
selected_crosshair_color_idx = 0  # Default Green
settings_cursor_pos = 0

# Applied settings
mouse_sensitivity = 0.002
target_size_multiplier = 1.0

# Color configurations
target_colors = {
    "Cyan": (0.0, 0.7, 0.7),
    "Red": (0.8, 0.1, 0.1),
    "Green": (0.1, 0.8, 0.1),
    "Yellow": (0.9, 0.9, 0.1),
    "Purple": (0.7, 0.2, 0.8)
}

crosshair_colors = {
    "Green": (0.0, 1.0, 0.0),
    "Cyan": (0.0, 1.0, 1.0),
    "Red": (1.0, 0.0, 0.0),
    "Yellow": (1.0, 1.0, 0.0),
    "Magenta": (1.0, 0.0, 1.0)
}

current_target_color = (0.0, 0.7, 0.7)  # Default cyan
current_crosshair_color = (0.0, 1.0, 0.0)  # Default green


# GAME STATE VARIABLES

# Scoring and statistics
score = 0
misses = 0
shots_fired = 0
successful_hits = 0
accuracy = 0.0

# Timing variables
game_timer = 0
game_start_time = 0
selected_game_duration = 30
last_target_spawn_time = 0

# Mode-specific progress tracking
practice_targets_hit = 0
reaction_targets_hit = 0
fixed_targets_hit = 0
reaction_times = []
last_target_spawn_finish_time = 0

# Mode timing
reaction_mode_start_time = 0.0
reaction_mode_end_time = 0.0

fixed_mode_start_time = 0.0
fixed_mode_end_time = 0.0

# Special modes
cheat_mode_active = False
scope_mode_active = False

# PLAYER AND CAMERA VARIABLES

# Player position and orientation
player_pos = [0, 50, 100]
player_yaw = 0.0
player_pitch = 0.0
camera_offset_z = 200
fovY = 70

# Mouse and crosshair
mouse_x, mouse_y = 500, 400
crosshair_world_coords = [0, 0, 0]

# GAME OBJECTS

# Dynamic game objects
targets = []
bullet_tracers = []
hit_effects = []

# Current weapon state
current_weapon = {'type': 'Pistol'}

# UI RENDERING FUNCTIONS

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, r=1.0, g=1.0, b=1.0):
    glColor3f(r, g, b)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_main_menu():
    draw_text(450, 700, "TRAIM 4.2.3", font=GLUT_BITMAP_HELVETICA_18)
    
    # Game Mode selection row
    draw_text(200, 550, "Game Mode:", font=GLUT_BITMAP_HELVETICA_18)
    for i, mode in enumerate(menu_options["mode"]):
        is_selected = (i == selected_mode_idx)
        is_hovered = (menu_cursor_pos == 0)
        
        # Determine text color based on selection and hover state
        if is_selected and is_hovered:
            color = (1, 0, 0)  # Red for hovered selection
        elif is_selected:
            color = (0, 1, 0)  # Green for selection
        else:
            color = (1, 1, 1)  # White for default
            
        draw_text(350 + i * 100, 550, mode, font=GLUT_BITMAP_HELVETICA_18, 
                 r=color[0], g=color[1], b=color[2])

    # Game Time selection row
    time_available = (selected_mode_idx not in [PRACTICE_MODE_INDEX, REACTION_MODE_INDEX, FIXED_MODE_INDEX])
    time_color = (1, 1, 1) if time_available else (0.5, 0.5, 0.5)
    draw_text(200, 500, "Game Time:", font=GLUT_BITMAP_HELVETICA_18, 
             r=time_color[0], g=time_color[1], b=time_color[2])
    
    for i, time_option in enumerate(menu_options["time"]):
        # Show only relevant time options based on mode
        should_display = True
        if not time_available and time_option != "N/A":
            should_display = False
        elif time_available and time_option == "N/A":
            should_display = False
        
        if not should_display:
            continue

        is_selected = (i == selected_time_idx)
        is_hovered = (menu_cursor_pos == 1)

        # Color logic for time options
        if not time_available:
            if time_option == "N/A":
                color = (1, 0, 0) if is_hovered else (0, 1, 0)
            else:
                color = (0.5, 0.5, 0.5)
        else:
            if is_selected and is_hovered:
                color = (1, 0, 0)
            elif is_selected:
                color = (0, 1, 0)
            else:
                color = (1, 1, 1)
        
        draw_text(350 + i * 100, 500, time_option, font=GLUT_BITMAP_HELVETICA_18,
                 r=color[0], g=color[1], b=color[2])

    # Weapon selection row
    draw_text(200, 450, "Weapon:", font=GLUT_BITMAP_HELVETICA_18)
    for i, weapon in enumerate(menu_options["weapon"]):
        is_selected = (i == selected_weapon_idx)
        is_hovered = (menu_cursor_pos == 2)
        
        if is_selected and is_hovered:
            color = (1, 0, 0)
        elif is_selected:
            color = (0, 1, 0)
        else:
            color = (1, 1, 1)
            
        draw_text(350 + i * 120, 450, weapon, font=GLUT_BITMAP_HELVETICA_18,
                 r=color[0], g=color[1], b=color[2])

    # Start button
    start_button_texts = {
        PRACTICE_MODE_INDEX: "START PRACTICE",
        REACTION_MODE_INDEX: "START REACTION",
        FIXED_MODE_INDEX: "START FIXED"
    }
    start_text = start_button_texts.get(selected_mode_idx, "START GAME")
    
    start_color = (1, 0, 0) if menu_cursor_pos == 3 else (0.7, 0.7, 0.7)
    draw_text(400, 400, start_text, font=GLUT_BITMAP_HELVETICA_18,
             r=start_color[0], g=start_color[1], b=start_color[2])

    # Settings button
    settings_color = (1, 0, 0) if menu_cursor_pos == 4 else (0.7, 0.7, 0.7)
    draw_text(400, 350, "SETTINGS", font=GLUT_BITMAP_HELVETICA_18,
             r=settings_color[0], g=settings_color[1], b=settings_color[2])

    # Help text
    draw_text(10, 50, "Controls: W/S (Navigate Menu), A/D (Change Options), Enter (Select/Start)", 
             font=GLUT_BITMAP_HELVETICA_18)

def draw_settings():
    draw_text(450, 700, "SETTINGS", font=GLUT_BITMAP_HELVETICA_18)
    
    settings_configs = [
        ("Sensitivity:", settings_options["sensitivity"], selected_sensitivity_idx, lambda s: f"{s:.3f}"),
        ("Target Size:", settings_options["target_size"], selected_target_size_idx, lambda s: f"{s:.2f}x"),
        ("Target Color:", settings_options["target_color"], selected_target_color_idx, str),
        ("Crosshair Color:", settings_options["crosshair_color"], selected_crosshair_color_idx, str)
    ]
    
    y_positions = [550, 500, 450, 400]
    
    for setting_idx, (label, options, selected_idx, formatter) in enumerate(settings_configs):
        draw_text(300, y_positions[setting_idx], label, font=GLUT_BITMAP_HELVETICA_18)
        
        for i, option in enumerate(options):
            is_selected = (i == selected_idx)
            is_hovered = (settings_cursor_pos == setting_idx)
            
            if is_selected and is_hovered:
                color = (1, 0, 0)
            elif is_selected:
                color = (0, 1, 0)
            else:
                color = (1, 1, 1)
            
            x_offset = 90 if setting_idx >= 2 else 80  # More space for color names
            draw_text(450 + i * x_offset, y_positions[setting_idx], formatter(option),
                     font=GLUT_BITMAP_HELVETICA_18, r=color[0], g=color[1], b=color[2])

    # Back button
    back_color = (1, 0, 0) if settings_cursor_pos == 4 else (0.7, 0.7, 0.7)
    draw_text(450, 350, "BACK TO MENU", font=GLUT_BITMAP_HELVETICA_18,
             r=back_color[0], g=back_color[1], b=back_color[2])

    draw_text(10, 50, "Controls: W/S (Navigate), A/D (Change Options), Enter (Select), ESC (Back)", 
             font=GLUT_BITMAP_HELVETICA_18)


# GAME RENDERING FUNCTIONS

def draw_targets():
    for target in targets:
        if target['active']:
            glPushMatrix()
            glTranslatef(target['x'], target['y'], target['z'])
            
            # Damage visualization for multi-hit targets
            if target.get('max_health', 1) == 2 and target.get('current_health', 1) == 1:
                glColor3f(1.0, 0.5, 0.0)  # Orange for damaged targets
            else:
                glColor3f(current_target_color[0], current_target_color[1], current_target_color[2])
            
            gluSphere(gluNewQuadric(), target['radius'], 20, 20)
            glPopMatrix()

def draw_target_surface():

    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glTranslatef(0, player_pos[1] + 50, TARGET_WALL_Z)
    glScalef(TARGET_MAX_X * 2.5, TARGET_MAX_Y * 2.5, 10)
    glutSolidCube(1)
    glPopMatrix()

def draw_ingame_ui():
    
    # Mode-specific UI rendering
    if selected_mode_idx == PRACTICE_MODE_INDEX:
        draw_text(10, 770, "Time: N/A", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(10, 740, f"Score: {score}", font=GLUT_BITMAP_HELVETICA_18)
        
    elif selected_mode_idx == REACTION_MODE_INDEX:
        # Calculate elapsed time for reaction mode
        if reaction_targets_hit >= REACTION_TARGET_GOAL:
            elapsed_time = reaction_mode_end_time - reaction_mode_start_time
        else:
            elapsed_time = time.time() - reaction_mode_start_time
            
        draw_text(10, 770, f"Targets: {reaction_targets_hit}/{REACTION_TARGET_GOAL}", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(10, 740, f"Time: {elapsed_time:.2f}s", font=GLUT_BITMAP_HELVETICA_18)
        
        # Show accuracy for reaction mode
        calc_accuracy = (successful_hits / shots_fired * 100) if shots_fired > 0 else 0.0
        draw_text(10, 710, f"Accuracy: {calc_accuracy:.2f}%", font=GLUT_BITMAP_HELVETICA_18)
        
    elif selected_mode_idx == FIXED_MODE_INDEX:
        # Calculate elapsed time for fixed mode
        if fixed_targets_hit >= FIXED_TARGET_GOAL:
            elapsed_time = fixed_mode_end_time - fixed_mode_start_time
        else:
            elapsed_time = time.time() - fixed_mode_start_time
            
        draw_text(10, 770, f"Targets: {fixed_targets_hit}/{FIXED_TARGET_GOAL}", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(10, 740, f"Time: {elapsed_time:.2f}s", font=GLUT_BITMAP_HELVETICA_18)
        
    else:
        # Standard timed modes
        remaining_time = max(0, int(selected_game_duration - game_timer))
        draw_text(10, 770, f"Time: {remaining_time}", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(10, 740, f"Score: {score}", font=GLUT_BITMAP_HELVETICA_18)

    # Adjust UI positioning for cheat mode indicator
    base_y_positions = [680, 650, 620]
    if cheat_mode_active:
        draw_text(10, 680, "Cheat Mode: ON", font=GLUT_BITMAP_HELVETICA_18, r=1.0, g=0.5, b=0.0)
        base_y_positions = [650, 620, 590]

    # Show detailed stats for non-reaction/fixed modes
    if selected_mode_idx not in [REACTION_MODE_INDEX, FIXED_MODE_INDEX]:
        draw_text(10, base_y_positions[0], f"Misses: {misses}", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(10, base_y_positions[1], f"Shots Fired: {shots_fired}", font=GLUT_BITMAP_HELVETICA_18)
        
        calc_accuracy = (successful_hits / shots_fired * 100) if shots_fired > 0 else 0.0
        draw_text(10, base_y_positions[2], f"Accuracy: {calc_accuracy:.2f}%", font=GLUT_BITMAP_HELVETICA_18)

    # Current weapon display
    weapon_y = base_y_positions[2] - 30
    draw_text(10, weapon_y, f"Weapon: {current_weapon['type']}", font=GLUT_BITMAP_HELVETICA_18)

    # Draw crosshair
    draw_crosshair()

def draw_crosshair():


    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glColor3f(current_crosshair_color[0], current_crosshair_color[1], current_crosshair_color[2])
    glPointSize(6)
    glBegin(GL_LINES)
    # Horizontal line
    glVertex2f(mouse_x - 7, 800 - mouse_y)
    glVertex2f(mouse_x + 7, 800 - mouse_y)
    # Vertical line
    glVertex2f(mouse_x, 800 - mouse_y - 7)
    glVertex2f(mouse_x, 800 - mouse_y + 7)
    glEnd()
    glPointSize(1)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_game_over():
    
    draw_text(400, 600, "GAME OVER", font=GLUT_BITMAP_HELVETICA_18)
    
    calc_accuracy = (successful_hits / shots_fired * 100) if shots_fired > 0 else 0.0
    
    if selected_mode_idx == PRACTICE_MODE_INDEX:
        draw_text(380, 500, f"Targets Destroyed: {score}/{PRACTICE_TARGET_GOAL}", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(380, 470, f"Accuracy: {calc_accuracy:.2f}%", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 400, "Practice Complete! Press 'R' for Menu", font=GLUT_BITMAP_HELVETICA_18)
        
    elif selected_mode_idx == REACTION_MODE_INDEX:
        if reaction_times:
            total_time = reaction_mode_end_time - reaction_mode_start_time
            avg_reaction_time = sum(reaction_times) / len(reaction_times)
            draw_text(380, 500, f"Total Time: {total_time:.2f}s", font=GLUT_BITMAP_HELVETICA_18)
            draw_text(380, 470, f"Average Reaction Time: {avg_reaction_time:.3f}s", font=GLUT_BITMAP_HELVETICA_18)
            draw_text(380, 440, f"Accuracy: {calc_accuracy:.2f}%", font=GLUT_BITMAP_HELVETICA_18)
        else:
            draw_text(380, 500, "No reaction times recorded.", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 400, "Reaction Complete! Press 'R' for Menu", font=GLUT_BITMAP_HELVETICA_18)
        
    elif selected_mode_idx == FIXED_MODE_INDEX:
        total_time = fixed_mode_end_time - fixed_mode_start_time
        draw_text(380, 500, f"Total Time: {total_time:.2f}s", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 400, "Fixed Mode Complete! Press 'R' for Menu", font=GLUT_BITMAP_HELVETICA_18)
        
    else:
        # Standard timed modes
        draw_text(400, 550, f"Final Score: {score}", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(400, 520, f"Total Shots: {shots_fired}", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(400, 490, f"Accuracy: {calc_accuracy:.2f}%", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 400, "Press 'R' to return to Menu", font=GLUT_BITMAP_HELVETICA_18)

def draw_scope_overlay():
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Black overlay with transparent center circle
    glColor4f(0.0, 0.0, 0.0, 0.8)
    
    # Draw four rectangles around the center scope area
    scope_regions = [
        (0, 0, 1000, 350),      # Bottom
        (0, 450, 1000, 800),    # Top
        (0, 350, 350, 450),     # Left
        (650, 350, 1000, 450)   # Right
    ]
    
    glBegin(GL_QUADS)
    for x1, y1, x2, y2 in scope_regions:
        glVertex2f(x1, y1)
        glVertex2f(x2, y1)
        glVertex2f(x2, y2)
        glVertex2f(x1, y2)
    glEnd()

    # Draw scope crosshairs
    glColor3f(0.0, 1.0, 0.0)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # Horizontal crosshair
    glVertex2f(450, 400)
    glVertex2f(550, 400)
    # Vertical crosshair
    glVertex2f(500, 350)
    glVertex2f(500, 450)
    glEnd()
    glLineWidth(1.0)

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# WEAPON RENDERING FUNCTIONS

def draw_weapon():

    weapon_type = current_weapon.get('type', 'Pistol')

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(fovY, 1000.0/800.0, 0.05, 50)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    weapon_renderers = {
        'Pistol': draw_pistol,
        'Shotgun': draw_shotgun,
        'Sniper': draw_sniper
    }
    
    if weapon_type in weapon_renderers:
        weapon_renderers[weapon_type]()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_pistol():

    glTranslatef(0.25, -0.20, -0.7)
    glRotatef(player_pitch * 180 / math.pi, 1, 0, 0)
    glRotatef(-5, 1, 0, 0)
    glRotatef(5, 0, 1, 0)

    # Barrel and grip
    glColor3f(0.82, 0.71, 0.55)
    glPushMatrix()
    glTranslatef(0.0, -0.03, 0.05)
    glPushMatrix()
    glRotatef(75, 1, 0, 0)
    glRotatef(-15, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.03, 0.025, 0.15, 8, 2)
    glPopMatrix()
    glTranslatef(0.0, -0.02, 0.12)
    gluSphere(gluNewQuadric(), 0.04, 10, 10)
    glPopMatrix()

    # Slide
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glScalef(0.04, 0.04, 0.20)
    glTranslatef(0, 0, 0)
    glutSolidCube(1)
    glPopMatrix()

    # Trigger guard
    glColor3f(0.08, 0.08, 0.08)
    glPushMatrix()
    glTranslatef(0, -0.03, -0.03)
    glScalef(0.03, 0.07, 0.03)
    glutSolidCube(1)
    glPopMatrix()

def draw_shotgun():

    glTranslatef(0.20, -0.18, -0.8)
    glRotatef(player_pitch * 180 / math.pi, 1, 0, 0)
    glRotatef(-3, 1, 0, 0)
    glRotatef(8, 0, 1, 0)
    glRotatef(180, 0, 0, 1)
    glRotatef(180, 0, 1, 0)

    # Wooden stock
    glColor3f(0.55, 0.35, 0.2)
    glPushMatrix()
    glTranslatef(-0.12, -0.05, -0.10)
    glScalef(0.12, 0.07, 0.28)
    glutSolidCube(1)
    glPopMatrix()

    # Metal receiver
    glColor3f(0.15, 0.15, 0.15)
    glPushMatrix()
    glTranslatef(0.0, -0.03, 0.0)
    glScalef(0.06, 0.06, 0.14)
    glutSolidCube(1)
    glPopMatrix()

    # Barrel
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0.0, -0.02, 0.08)
    gluCylinder(gluNewQuadric(), 0.025, 0.025, 0.55, 15, 3)
    glPopMatrix()

    # Pump/foregrip
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0.0, -0.04, 0.20)
    glScalef(0.10, 0.06, 0.18)
    glutSolidCube(1)
    glPopMatrix()

    # Front sight
    glColor3f(0.9, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(0.0, -0.005, 0.63)
    gluSphere(gluNewQuadric(), 0.01, 10, 10)
    glPopMatrix()

def draw_sniper():

    glTranslatef(0.28, -0.22, -0.9)
    glRotatef(player_pitch * 180 / math.pi, 1, 0, 0)
    glRotatef(-4, 1, 0, 0)
    glRotatef(4, 0, 1, 0)
    glRotatef(180, 0, 1, 0)  # Orient barrel forward

    # Long barrel
    glColor3f(0.12, 0.12, 0.12)
    glPushMatrix()
    glTranslatef(0.0, -0.01, 0.0)
    gluCylinder(gluNewQuadric(), 0.012, 0.012, 0.75, 14, 2)
    glPopMatrix()

    # Muzzle brake
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0.0, -0.01, -0.75)
    glScalef(0.03, 0.03, 0.06)
    glutSolidCube(1)
    glPopMatrix()

    # Rifle receiver
    glColor3f(0.18, 0.18, 0.18)
    glPushMatrix()
    glTranslatef(0.0, -0.015, -0.10)
    glScalef(0.06, 0.06, 0.30)
    glutSolidCube(1)
    glPopMatrix()

    # Wooden stock
    glColor3f(0.45, 0.30, 0.18)
    glPushMatrix()
    glTranslatef(0.0, -0.02, -0.35)
    glScalef(0.08, 0.08, 0.25)
    glutSolidCube(1)
    glPopMatrix()

    # Buttpad
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0.0, -0.02, -0.48)
    glScalef(0.08, 0.09, 0.02)
    glutSolidCube(1)
    glPopMatrix()

    # Scope tube
    glColor3f(0.08, 0.08, 0.08)
    glPushMatrix()
    glTranslatef(0.0, 0.05, -0.20)
    gluCylinder(gluNewQuadric(), 0.025, 0.025, 0.40, 14, 2)
    glPopMatrix()

    # Scope lenses
    glColor3f(0.1, 0.1, 0.1)
    for lens_z in [-0.20, -0.60]:  # Front and rear lenses
        glPushMatrix()
        glTranslatef(0.0, 0.05, lens_z)
        radius = 0.026 if lens_z == -0.20 else 0.022
        gluSphere(gluNewQuadric(), radius, 10, 10)
        glPopMatrix()

    # Scope mounts
    glColor3f(0.15, 0.15, 0.15)
    for mount_z in [-0.28, -0.45]:
        glPushMatrix()
        glTranslatef(0.0, 0.03, mount_z)
        glScalef(0.04, 0.03, 0.02)
        glutSolidCube(1)
        glPopMatrix()

    # Bolt handle
    glColor3f(0.18, 0.18, 0.18)
    glPushMatrix()
    glTranslatef(0.04, -0.005, -0.05)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.006, 0.006, 0.05, 10, 2)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.07, -0.005, -0.05)
    gluSphere(gluNewQuadric(), 0.012, 10, 10)
    glPopMatrix()

    # Bipod legs
    glColor3f(0.12, 0.12, 0.12)
    for leg_x in [0.02, -0.02]:
        glPushMatrix()
        glTranslatef(leg_x, -0.06, -0.15)
        glRotatef(25, 1, 0, 0)
        glScalef(0.007, 0.007, 0.12)
        glutSolidCube(1)
        glPopMatrix()


# TARGET MANAGEMENT FUNCTIONS

def update_targets():

    global targets, last_target_spawn_time
    
    active_targets = []
    should_spawn_new = False
    
    for target in targets:
        if not target['active']:
            continue

        # Handle target movement for medium and hard modes
        if selected_mode_idx in [1, 2]:  # Medium or Hard
            target['x'] += target.get('vx', 0)
            target['y'] += target.get('vy', 0)

            # Bounce off walls
            handle_target_wall_collision(target)

        # Handle target shrinking
        should_spawn_new = handle_target_shrinking(target) or should_spawn_new
        
        # Keep active targets
        if target['radius'] > 1:
            active_targets.append(target)
    
    targets = active_targets
    
    if should_spawn_new:
        create_new_target()

def handle_target_wall_collision(target):
    
    # X-axis boundaries
    if (target['x'] - target['radius']) < -TARGET_MAX_X:
        target['x'] = -TARGET_MAX_X + target['radius']
        target['vx'] *= -1
    elif (target['x'] + target['radius']) > TARGET_MAX_X:
        target['x'] = TARGET_MAX_X - target['radius']
        target['vx'] *= -1
    
    # Y-axis boundaries
    min_y = player_pos[1] - (TARGET_MAX_Y / 2)
    max_y = player_pos[1] + (TARGET_MAX_Y / 2)
    if (target['y'] - target['radius']) < min_y:
        target['y'] = min_y + target['radius']
        target['vy'] *= -1
    elif (target['y'] + target['radius']) > max_y:
        target['y'] = max_y - target['radius']
        target['vy'] *= -1

def handle_target_shrinking(target):
    
    shrink_rates = {
        1: TARGET_SHRINK_RATE_MEDIUM,  # Medium
        2: TARGET_SHRINK_RATE_HARD     # Hard
    }
    
    if selected_mode_idx in shrink_rates:
        target['radius'] -= shrink_rates[selected_mode_idx]
        if target['radius'] <= 1:
            target['active'] = False
            return True  # Signal to spawn new target
    
    return False

def create_new_target():
    
    global targets, last_target_spawn_time
    
    # Check if we should limit active targets
    active_count = sum(1 for t in targets if t['active'])
    max_targets = get_max_targets_for_mode()
    
    if active_count >= max_targets:
        return

    # Generate random position
    target_x = random.uniform(-TARGET_MAX_X, TARGET_MAX_X)
    target_y = player_pos[1] + random.uniform(-TARGET_MAX_Y/2, TARGET_MAX_Y)
    
    # Multi-shot target chance
    is_multi_shot = random.random() < 0.2
    max_health = 2 if is_multi_shot else 1
    
    # Movement for medium/hard modes
    velocity_x, velocity_y = calculate_target_velocity()
    
    # Create target object
    new_target = {
        'x': target_x, 'y': target_y, 'z': TARGET_WALL_Z,
        'radius': TARGET_BASE_RADIUS * target_size_multiplier,
        'active': True,
        'id': random.randint(0, 100000),
        'max_health': max_health,
        'current_health': max_health,
        'vx': velocity_x,
        'vy': velocity_y,
        'spawn_time': time.time()
    }
    
    targets.append(new_target)

def get_max_targets_for_mode():

    if selected_mode_idx in [0, 1]:  # Easy, Medium
        return 1
    elif selected_mode_idx == 2:     # Hard
        return 3
    elif selected_mode_idx == REACTION_MODE_INDEX:
        return 1
    elif selected_mode_idx == FIXED_MODE_INDEX:
        return FIXED_TARGET_GOAL
    return 1

def calculate_target_velocity():

    if selected_mode_idx not in [1, 2]:  # Only medium/hard have movement
        return 0, 0
    
    speed_scale = 0.5 if selected_mode_idx == 1 else 1.0
    vx = random.uniform(-1.5, 1.5) * speed_scale
    vy = random.uniform(-1.0, 1.0) * speed_scale
    
    # Ensure minimum velocity
    if abs(vx) < 0.3:
        vx = 0.3 * (1 if vx >= 0 else -1)
    if abs(vy) < 0.2:
        vy = 0.2 * (1 if vy >= 0 else -1)
    
    return vx, vy

# SHOOTING AND COMBAT FUNCTIONS

def get_aim_vector():

    aim_x = -math.sin(player_yaw) * math.cos(player_pitch)
    aim_y = math.sin(player_pitch)
    aim_z = -math.cos(player_yaw) * math.cos(player_pitch)
    
    # Normalize vector
    length = math.sqrt(aim_x**2 + aim_y**2 + aim_z**2)
    if length == 0:
        return (0, 0, -1)
    return (aim_x/length, aim_y/length, aim_z/length)

def perform_shot(aim_direction_override=None):

    global shots_fired, bullet_tracers
    
    shots_fired += 1
    aim_dir = aim_direction_override or get_aim_vector()
    
    # Calculate muzzle position
    muzzle_pos = calculate_muzzle_position(aim_dir)
    
    # Get weapon-specific properties
    weapon_type = current_weapon.get('type', 'Pistol')
    tracer_color = get_weapon_tracer_color(weapon_type)
    
    # Handle weapon-specific shooting logic
    if weapon_type == 'Shotgun':
        handle_shotgun_shot(muzzle_pos, aim_dir, tracer_color)
    else:
        handle_single_shot(muzzle_pos, aim_dir, tracer_color)

def calculate_muzzle_position(aim_dir):
    
    muzzle_offset_forward = 10
    muzzle_offset_right = 3
    muzzle_offset_down = -2

    cam_right_x = math.cos(player_yaw)
    cam_right_z = -math.sin(player_yaw)

    return [
        player_pos[0] + aim_dir[0] * muzzle_offset_forward + cam_right_x * muzzle_offset_right,
        player_pos[1] + aim_dir[1] * muzzle_offset_forward + muzzle_offset_down,
        player_pos[2] + aim_dir[2] * muzzle_offset_forward + cam_right_z * muzzle_offset_right
    ]

def get_weapon_tracer_color(weapon_type):

    weapon_colors = {
        'Pistol': (1.0, 1.0, 0.5),    # Warm yellow
        'Shotgun': (1.0, 0.6, 0.0),   # Orange
        'Sniper': (0.2, 0.8, 1.0)     # Cyan/blue
    }
    return weapon_colors.get(weapon_type, (1.0, 1.0, 0.5))

def handle_shotgun_shot(muzzle_pos, aim_dir, tracer_color):

    global misses
    
    num_pellets = 8
    spread_angle = 10  # degrees
    shot_hit_target = False
    
    for _ in range(num_pellets):
        # Calculate pellet direction with spread
        pellet_aim_dir = apply_weapon_spread(aim_dir, spread_angle)
        
        # Create tracer for pellet
        create_bullet_tracer(muzzle_pos, pellet_aim_dir, tracer_color)
        
        # Check for hit
        if check_shot_hit(pellet_aim_dir):
            shot_hit_target = True
    
    if not shot_hit_target:
        misses += 1

def handle_single_shot(muzzle_pos, aim_dir, tracer_color):
    global misses
    
    # Create tracer
    create_bullet_tracer(muzzle_pos, aim_dir, tracer_color)
    
    # Check for hit
    if not check_shot_hit(aim_dir):
        misses += 1

def apply_weapon_spread(aim_dir, spread_degrees):

    spread_yaw = random.uniform(-spread_degrees, spread_degrees) * math.pi / 180
    spread_pitch = random.uniform(-spread_degrees, spread_degrees) * math.pi / 180

    # Apply spread (simplified rotation)
    pellet_x = aim_dir[0] * math.cos(spread_yaw) - aim_dir[2] * math.sin(spread_yaw)
    pellet_z = aim_dir[0] * math.sin(spread_yaw) + aim_dir[2] * math.cos(spread_yaw)
    pellet_y = aim_dir[1] + math.sin(spread_pitch)
    
    # Normalize
    length = math.sqrt(pellet_x**2 + pellet_y**2 + pellet_z**2)
    if length != 0:
        return (pellet_x/length, pellet_y/length, pellet_z/length)
    return aim_dir

def create_bullet_tracer(muzzle_pos, direction, color):
    
    tracer_end = [
        muzzle_pos[0] + direction[0] * TRACER_LENGTH,
        muzzle_pos[1] + direction[1] * TRACER_LENGTH,
        muzzle_pos[2] + direction[2] * TRACER_LENGTH
    ]
    
    bullet_tracers.append({
        'start': muzzle_pos,
        'end': tracer_end,
        'time': time.time(),
        'color': color
    })

def check_shot_hit(aim_dir):

    global successful_hits, score, hit_effects
    global reaction_targets_hit, reaction_times, last_target_spawn_finish_time, reaction_mode_end_time
    global fixed_targets_hit, fixed_mode_end_time, practice_targets_hit
    
    for target in targets:
        if not target['active']:
            continue

        if is_ray_sphere_collision(player_pos, aim_dir, target):
            successful_hits += 1
            target['current_health'] -= 1
            
            # Create hit effect
            impact_point = calculate_impact_point(player_pos, aim_dir, target)
            effect_radius = target['radius'] * (0.15 if target['current_health'] > 0 else 0.3)
            hit_effects.append({
                'pos': impact_point,
                'time': time.time(),
                'radius': effect_radius
            })

            # Handle target destruction
            if target['current_health'] <= 0:
                target['active'] = False
                score += 1
                handle_target_destroyed()
            
            return True
    
    return False

def is_ray_sphere_collision(ray_origin, ray_direction, target):
    # Vector from ray origin to sphere center
    to_center_x = target['x'] - ray_origin[0]
    to_center_y = target['y'] - ray_origin[1]
    to_center_z = target['z'] - ray_origin[2]

    # Project sphere center onto ray
    projection_length = (
        to_center_x * ray_direction[0] +
        to_center_y * ray_direction[1] +
        to_center_z * ray_direction[2]
    )

    if projection_length < 0:  # Sphere is behind ray origin
        return False

    # Distance squared from ray to sphere center
    center_to_ray_squared = (
        to_center_x**2 + to_center_y**2 + to_center_z**2
    ) - projection_length**2
    radius_squared = target['radius']**2

    if center_to_ray_squared > radius_squared:  # Ray misses sphere
        return False

    # Calculate intersection point
    half_chord = math.sqrt(radius_squared - center_to_ray_squared)
    intersection_distance = projection_length - half_chord

    return intersection_distance > 0

def calculate_impact_point(ray_origin, ray_dir, target):
    # Simplified calculation - use target center for impact effects
    return [target['x'], target['y'], target['z']]

def handle_target_destroyed():

    if selected_mode_idx == PRACTICE_MODE_INDEX:
        global practice_targets_hit
        practice_targets_hit += 1
        if practice_targets_hit < PRACTICE_TARGET_GOAL:
            create_new_target()
            
    elif selected_mode_idx == REACTION_MODE_INDEX:
        global reaction_targets_hit, reaction_times, last_target_spawn_finish_time, reaction_mode_end_time
        reaction_targets_hit += 1
        
        # Record reaction time
        target_hit = next((t for t in targets if not t['active']), None)
        if target_hit:
            reaction_time = time.time() - target_hit['spawn_time']
            reaction_times.append(reaction_time)
        
        last_target_spawn_finish_time = time.time()
        
        if reaction_targets_hit >= REACTION_TARGET_GOAL:
            reaction_mode_end_time = time.time()
            global current_state
            current_state = STATE_GAME_OVER
            glutSetCursor(GLUT_CURSOR_INHERIT)
            
    elif selected_mode_idx == FIXED_MODE_INDEX:
        global fixed_targets_hit, fixed_mode_end_time
        fixed_targets_hit += 1
        
        if fixed_targets_hit >= FIXED_TARGET_GOAL:
            fixed_mode_end_time = time.time()
            current_state = STATE_GAME_OVER
            glutSetCursor(GLUT_CURSOR_INHERIT)
        else:
            create_new_target()  # Spawn replacement immediately
            
    elif selected_mode_idx in [0, 1, 2]:  # Easy, Medium, Hard
        create_new_target()


# CAMERA AND CONTROLS

def setupCamera():

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Use scoped FOV for sniper rifles
    fov = 20 if (scope_mode_active and current_weapon.get('type') == 'Sniper') else fovY
    gluPerspective(fov, 1000.0/800.0, 0.1, 2000.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Calculate look-at point
    look_at_x = player_pos[0] - math.sin(player_yaw) * math.cos(player_pitch) * 100
    look_at_y = player_pos[1] + math.sin(player_pitch) * 100
    look_at_z = player_pos[2] - math.cos(player_yaw) * math.cos(player_pitch) * 100
    
    gluLookAt(player_pos[0], player_pos[1], player_pos[2],
              look_at_x, look_at_y, look_at_z,
              0, 1, 0)

def handle_mouse_movement(x, y):
    global mouse_x, mouse_y, player_yaw, player_pitch
    
    if current_state != STATE_PLAYING:
        return

    mouse_x, mouse_y = x, y

    # Apply sensitivity (reduced when scoped)
    sensitivity = mouse_sensitivity
    if scope_mode_active and current_weapon.get('type') == 'Sniper':
        sensitivity *= 0.3

    # Calculate mouse delta from window center
    win_center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
    win_center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2

    if x == win_center_x and y == win_center_y:
        return

    dx = x - win_center_x
    dy = y - win_center_y

    # Update player orientation
    player_yaw -= dx * sensitivity
    player_pitch -= dy * sensitivity

    # Clamp pitch to prevent over-rotation
    max_pitch = math.pi / 2 - 0.01
    player_pitch = max(-max_pitch, min(max_pitch, player_pitch))

    # Reset mouse to center
    glutWarpPointer(win_center_x, win_center_y)


# GAME STATE MANAGEMENT

def apply_settings():
    global mouse_sensitivity, target_size_multiplier, current_target_color, current_crosshair_color
    
    mouse_sensitivity = settings_options["sensitivity"][selected_sensitivity_idx]
    target_size_multiplier = settings_options["target_size"][selected_target_size_idx]
    
    color_name = settings_options["target_color"][selected_target_color_idx]
    current_target_color = target_colors[color_name]
    
    crosshair_color_name = settings_options["crosshair_color"][selected_crosshair_color_idx]
    current_crosshair_color = crosshair_colors[crosshair_color_name]

def reset_game():
    global score, misses, shots_fired, successful_hits, game_timer, game_start_time, targets
    global player_pos, player_yaw, player_pitch, current_state, selected_game_duration
    global practice_targets_hit, reaction_targets_hit, fixed_targets_hit, reaction_times
    global last_target_spawn_finish_time, reaction_mode_start_time, reaction_mode_end_time
    global fixed_mode_start_time, fixed_mode_end_time, current_weapon, last_target_spawn_time

    # Reset scoring and statistics
    score = 0
    misses = 0
    shots_fired = 0
    successful_hits = 0
    game_timer = 0
    
    # Reset mode-specific progress
    practice_targets_hit = 0
    reaction_targets_hit = 0
    fixed_targets_hit = 0
    reaction_times = []
    last_target_spawn_finish_time = 0

    # Set up timing for special modes
    reaction_mode_start_time = time.time()
    reaction_mode_end_time = 0.0
    fixed_mode_start_time = 0.0
    fixed_mode_end_time = 0.0

    # Configure game duration
    if selected_mode_idx in [PRACTICE_MODE_INDEX, REACTION_MODE_INDEX, FIXED_MODE_INDEX]:
        selected_game_duration = float('inf')
        if selected_mode_idx == FIXED_MODE_INDEX:
            fixed_mode_start_time = time.time()
    else:
        duration_str = menu_options["time"][selected_time_idx].replace('s', '')
        selected_game_duration = int(duration_str)

    # Reset world state
    game_start_time = time.time()
    targets = []
    player_pos = [0, 50, 100]
    player_yaw = 0.0
    player_pitch = 0.0
    last_target_spawn_time = time.time()
    current_state = STATE_PLAYING

    # Set up weapon
    weapon_type = menu_options["weapon"][selected_weapon_idx]
    current_weapon = {'type': weapon_type}

    # Apply settings and start game
    apply_settings()
    create_new_target()
    glutSetCursor(GLUT_CURSOR_NONE)


# INPUT HANDLING

def handle_menu_navigation(key):
    global menu_cursor_pos, selected_mode_idx, selected_time_idx, selected_weapon_idx, current_state

    if key == b'\r':  # Enter key
        if menu_cursor_pos == 3:  # Start button
            if selected_mode_idx in [PRACTICE_MODE_INDEX, REACTION_MODE_INDEX, FIXED_MODE_INDEX]:
                global selected_time_idx
                selected_time_idx = menu_options["time"].index("N/A")
            reset_game()
        elif menu_cursor_pos == 4:  # Settings button
            current_state = STATE_SETTINGS
            global settings_cursor_pos
            settings_cursor_pos = 0
            
    elif key in [b'w', b's']:  # Vertical navigation
        direction = -1 if key == b'w' else 1
        total_rows = 5
        new_pos = (menu_cursor_pos + direction) % total_rows
        
        # Skip time row if in special modes
        if (selected_mode_idx in [PRACTICE_MODE_INDEX, REACTION_MODE_INDEX, FIXED_MODE_INDEX] 
            and new_pos == 1):
            new_pos = (new_pos + direction) % total_rows
        
        menu_cursor_pos = new_pos
        
    elif key in [b'a', b'd']:  # Horizontal option changes
        direction = -1 if key == b'a' else 1
        
        if menu_cursor_pos == 0:  # Mode selection
            selected_mode_idx = (selected_mode_idx + direction) % len(menu_options["mode"])
            if selected_mode_idx in [PRACTICE_MODE_INDEX, REACTION_MODE_INDEX, FIXED_MODE_INDEX]:
                selected_time_idx = menu_options["time"].index("N/A")
                
        elif menu_cursor_pos == 1:  # Time selection (if available)
            if selected_mode_idx not in [PRACTICE_MODE_INDEX, REACTION_MODE_INDEX, FIXED_MODE_INDEX]:
                valid_times = [t for t in menu_options["time"] if t != "N/A"]
                current_time = menu_options["time"][selected_time_idx]
                try:
                    current_idx = valid_times.index(current_time)
                    new_idx = (current_idx + direction) % len(valid_times)
                    selected_time_idx = menu_options["time"].index(valid_times[new_idx])
                except ValueError:
                    selected_time_idx = 0
                    
        elif menu_cursor_pos == 2:  # Weapon selection
            selected_weapon_idx = (selected_weapon_idx + direction) % len(menu_options["weapon"])

def handle_settings_navigation(key):
    global current_state, settings_cursor_pos
    global selected_sensitivity_idx, selected_target_size_idx, selected_target_color_idx, selected_crosshair_color_idx

    if key == b'\r':  # Enter key
        if settings_cursor_pos == 4:  # Back button
            apply_settings()
            current_state = STATE_MENU
    elif key == b'\x1b':  # ESC key
        current_state = STATE_MENU
    elif key in [b'w', b's']:  # Vertical navigation
        direction = -1 if key == b'w' else 1
        settings_cursor_pos = (settings_cursor_pos + direction) % 5
    elif key in [b'a', b'd']:  # Horizontal option changes
        direction = -1 if key == b'a' else 1
        setting_indices = [
            selected_sensitivity_idx, selected_target_size_idx,
            selected_target_color_idx, selected_crosshair_color_idx
        ]
        
        if settings_cursor_pos < len(setting_indices):
            options_key = list(settings_options.keys())[settings_cursor_pos]
            options_list = settings_options[options_key]
            current_idx = setting_indices[settings_cursor_pos]
            new_idx = (current_idx + direction) % len(options_list)
            
            # Update the appropriate global variable
            if settings_cursor_pos == 0:
                selected_sensitivity_idx = new_idx
            elif settings_cursor_pos == 1:
                selected_target_size_idx = new_idx
            elif settings_cursor_pos == 2:
                selected_target_color_idx = new_idx
            elif settings_cursor_pos == 3:
                selected_crosshair_color_idx = new_idx

def handle_gameplay_input(key):
    global player_pos, player_yaw, cheat_mode_active, current_state

    # Player movement
    speed = 10.0
    
    if key == b'w':  # Move forward
        player_pos[2] -= speed * math.cos(player_yaw)
        player_pos[0] -= speed * math.sin(player_yaw)
    elif key == b's':  # Move backward
        player_pos[2] += speed * math.cos(player_yaw)
        player_pos[0] += speed * math.sin(player_yaw)
    elif key == b'a':  # Strafe left
        player_pos[0] -= speed * math.cos(player_yaw)
        player_pos[2] += speed * math.sin(player_yaw)
    elif key == b'd':  # Strafe right
        player_pos[0] += speed * math.cos(player_yaw)
        player_pos[2] -= speed * math.sin(player_yaw)
    elif key in [b'm', b'M']:  # Return to menu
        current_state = STATE_MENU
        glutSetCursor(GLUT_CURSOR_INHERIT)
    elif key in [b'c', b'C']:  # Toggle cheat mode
        cheat_mode_active = not cheat_mode_active
        print(f"Cheat Mode: {'ON' if cheat_mode_active else 'OFF'}")

def handle_game_over_input(key):
    
    global current_state
    
    if key in [b'r', b'R']:  # Return to menu
        current_state = STATE_MENU
        glutSetCursor(GLUT_CURSOR_INHERIT)

# EVENT HANDLERS

def keyboardListener(key, x, y):

    global current_state

    # Handle ESC key to quit
    if key == b'\x1b':
        glutLeaveMainLoop()
        return

    # Route to appropriate handler based on current state
    if current_state == STATE_MENU:
        handle_menu_navigation(key)
    elif current_state == STATE_SETTINGS:
        handle_settings_navigation(key)
    elif current_state == STATE_PLAYING:
        handle_gameplay_input(key)
    elif current_state == STATE_GAME_OVER:
        handle_game_over_input(key)

def specialKeyListener(key, x, y):
    """Handle special keys (currently unused but required by GLUT)."""
    pass

def mouseListener(button, state, x, y):
    global scope_mode_active
    
    if current_state != STATE_PLAYING:
        return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        perform_shot()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Toggle scope for sniper rifle
        if current_weapon.get('type') == 'Sniper':
            scope_mode_active = not scope_mode_active

def passiveMouseMotion(x, y):
    handle_mouse_movement(x, y)
    

# GAME LOOP AND UPDATES

def update_visual_effects():
    global bullet_tracers, hit_effects
    
    current_time = time.time()
    
    # Remove expired bullet tracers
    bullet_tracers = [tracer for tracer in bullet_tracers 
                     if current_time - tracer['time'] < TRACER_DURATION]
    
    # Remove expired hit effects
    hit_effects = [effect for effect in hit_effects 
                  if current_time - effect['time'] < HIT_EFFECT_DURATION]

def should_create_new_target():

    current_time = time.time()
    
    # Check spawn interval
    if current_time - last_target_spawn_time < TARGET_SPAWN_INTERVAL:
        return False
    
    active_count = sum(1 for t in targets if t['active'])
    
    if selected_mode_idx == 2:  # Hard mode - always spawn if under limit
        return True
    elif selected_mode_idx == PRACTICE_MODE_INDEX:
        return active_count == 0 and practice_targets_hit < PRACTICE_TARGET_GOAL
    elif selected_mode_idx == REACTION_MODE_INDEX:
        return (active_count == 0 and 
                reaction_targets_hit < REACTION_TARGET_GOAL and
                (current_time - last_target_spawn_finish_time > REACTION_SPAWN_DELAY or
                 last_target_spawn_finish_time == 0))
    elif selected_mode_idx == FIXED_MODE_INDEX:
        return active_count < FIXED_TARGET_GOAL and fixed_targets_hit < FIXED_TARGET_GOAL
    else:  # Easy and Medium modes
        return active_count == 0

def check_game_end_conditions():

    global current_state, game_timer
    
    current_time = time.time()
    
    # Check time-based game modes
    if selected_mode_idx not in [PRACTICE_MODE_INDEX, REACTION_MODE_INDEX, FIXED_MODE_INDEX]:
        game_timer = current_time - game_start_time
        if game_timer >= selected_game_duration:
            current_state = STATE_GAME_OVER
            glutSetCursor(GLUT_CURSOR_INHERIT)
            return True
    
    # Check Practice mode completion
    if selected_mode_idx == PRACTICE_MODE_INDEX and practice_targets_hit >= PRACTICE_TARGET_GOAL:
        current_state = STATE_GAME_OVER
        glutSetCursor(GLUT_CURSOR_INHERIT)
        return True
    
    # Reaction and Fixed modes are handled in handle_target_destroyed()
    return False

def execute_cheat_mode():

    if not cheat_mode_active:
        return
    
    # Find closest active target
    closest_target = None
    min_distance = float('inf')
    
    for target in targets:
        if not target['active']:
            continue
        
        # Calculate distance to target
        dx = target['x'] - player_pos[0]
        dy = target['y'] - player_pos[1]
        dz = target['z'] - player_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < min_distance:
            min_distance = distance
            closest_target = target
    
    if closest_target:
        # Aim at target
        dx = closest_target['x'] - player_pos[0]
        dy = closest_target['y'] - player_pos[1]
        dz = closest_target['z'] - player_pos[2]
        
        # Calculate required yaw and pitch
        global player_yaw, player_pitch
        player_yaw = math.atan2(-dx, -dz)
        
        horizontal_dist = math.sqrt(dx*dx + dz*dz)
        if horizontal_dist > 0:
            player_pitch = math.atan2(dy, horizontal_dist)
        
        # Clamp pitch
        max_pitch = math.pi / 2 - 0.01
        player_pitch = max(-max_pitch, min(max_pitch, player_pitch))
        
        # Auto-shoot
        perform_shot()

def idle():

    global last_target_spawn_time
    
    if current_state == STATE_PLAYING:
        # Execute cheat mode if active
        execute_cheat_mode()
        
        # Check for game end conditions
        if check_game_end_conditions():
            return
        
        # Handle target spawning
        current_time = time.time()
        if should_create_new_target():
            create_new_target()
            last_target_spawn_time = current_time
        
        # Update game objects
        update_targets()
        update_visual_effects()
    
    # Trigger screen redraw
    glutPostRedisplay()

def draw_visual_effects():
    # Draw bullet tracers
    glLineWidth(2.0)
    for tracer in bullet_tracers:
        color = tracer.get('color', (1.0, 1.0, 0.5))
        glColor3f(color[0], color[1], color[2])
        glBegin(GL_LINES)
        glVertex3fv(tracer['start'])
        glVertex3fv(tracer['end'])
        glEnd()
    glLineWidth(1.0)
    
    # Draw hit effects
    for effect in hit_effects:
        glPushMatrix()
        glTranslatef(effect['pos'][0], effect['pos'][1], effect['pos'][2])
        
        # Calculate effect animation
        effect_age = time.time() - effect['time']
        effect_progress = min(1.0, effect_age / HIT_EFFECT_DURATION)
        current_radius = effect['radius'] * (1.0 - effect_progress)
        
        if current_radius > 0.1:
            glColor4f(1, 0.7, 0.1, 1.0)
            gluSphere(gluNewQuadric(), current_radius, 8, 8)
        
        glPopMatrix()

# MAIN RENDERING FUNCTION

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if current_state == STATE_MENU:
        # Render menu in 2D orthographic mode
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        draw_main_menu()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    elif current_state == STATE_SETTINGS:
        # Render settings in 2D orthographic mode
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        draw_settings()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    elif current_state == STATE_PLAYING:
        # Render 3D game world
        setupCamera()
        
        # Draw world geometry
        draw_target_surface()
        draw_targets()
        
        # Draw visual effects
        draw_visual_effects()
        
        # Draw weapon model
        draw_weapon()
        
        # Draw scope overlay if active
        if scope_mode_active and current_weapon.get('type') == 'Sniper':
            draw_scope_overlay()
        
        # Draw UI elements
        draw_ingame_ui()

    elif current_state == STATE_GAME_OVER:
        # Render game over screen in 2D orthographic mode
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        draw_game_over()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()

# INITIALIZATION AND MAIN FUNCTION

def initialize_opengl():

    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glEnable(GL_DEPTH_TEST)           # Enable depth testing
    glEnable(GL_COLOR_MATERIAL)       # Enable color materials


def main():

    # Initialize GLUT
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow(b"Traim 4.2.3")
    
    # Initialize OpenGL settings
    initialize_opengl()
    
    # Register callback functions
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutPassiveMotionFunc(passiveMouseMotion)
    glutIdleFunc(idle)
    
    # Apply initial settings
    apply_settings()
    
    # Set initial cursor state
    glutSetCursor(GLUT_CURSOR_INHERIT)
    
    # Print welcome message
    print("Starting Traim 4.2.3...")
    print("Menu Controls: W/S (Navigate), A/D (Change Options), Enter (Select/Start)")
    print("Game Controls: W/A/S/D (Move), Mouse (Aim), Left Click (Shoot)")
    print("Settings: Customize sensitivity, target size, and target colors!")
    print("Special: Right-click with Sniper for scope, C for cheat mode, M to return to menu")
    
    # Start the main loop
    glutMainLoop()


if __name__ == "__main__":
    main()