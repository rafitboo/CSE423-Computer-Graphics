from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Game state variables
game_over_print = False
player_pos = [0.0, 0.0, 0.0]  
player_angle = 0.0  
player_height = 15.0
bullets = []  
enemies = []  
cheat_mode = False  
follow_camera = False  # First vs third person view
camera_pos = (0, 900, 200)  # Third person 
game_score = 0
player_lives = 5
bullets_missed = 0
game_over = False

# Game constants
MAX_ENEMIES = 5
MAX_MISSED_BULLETS = 10
BOUNDARY_SIZE = 1000  # Arena size
fovY = 60  # Field of view

# Function to draw 2D text on screen
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): # type: ignore
    glColor3f(1, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, 1000, 0, 800)  # Set 2D projection for text
    
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

# 3D Vector utility class
class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z

    def to_list(self):
        return [self.x, self.y, self.z]

    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def move(self, dx, dy, dz):
        self.y += dy
        self.z += dz

# Bullet class 
class Bullet:
    def __init__(self, x, y, z, angle, target_enemy=None):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.hit = False  # bullet hit something
        self.hit_enemy = False  # bullet hit enemy (vs boundary)
        self.target_enemy = target_enemy  # For homing bullets in cheat mode

    def update(self):
        if self.hit:
            return

        movement_speed = 1

        # cheat mode
        if self.target_enemy and not self.target_enemy.hit:
            dx = self.target_enemy.x - self.x
            dz = self.target_enemy.z - self.z
            dy = self.target_enemy.y - self.y

            total_distance = math.sqrt(dx * dx + dz * dz + dy * dy)

            if total_distance > 0:
                # Move towards target 
                self.x += (dx / total_distance) * movement_speed
                self.y += (dy / total_distance) * movement_speed
                self.z += (dz / total_distance) * movement_speed
        else:
            # Normal bullet behavior 
            angle_radians = math.radians(self.angle)
            new_x = self.x + movement_speed * math.sin(angle_radians)
            new_z = self.z + movement_speed * math.cos(angle_radians)

            boundary_limit = (BOUNDARY_SIZE / 2) - 5

            # Check if bullet hits boundary
            if abs(new_x) < boundary_limit and abs(new_z) < boundary_limit:
                self.x = new_x
                self.z = new_z
            else:
                self.hit = True  # Bullet hits boundary
                
    def is_alive(self):
        return not self.hit
    
    def draw(self):
        # Draw bullet 
        glPushMatrix()
        glColor3f(1, 0, 0)
        glTranslatef(self.x, self.y-8, self.z)
        glutSolidCube(6)
        glPopMatrix()

# Enemy class - red spheres that chase the player
class Enemy:
    def __init__(self):
        self.respawn()
        self.target = False  # Whether this enemy is being targeted by homing bullet
        self.hit = False

    def respawn(self, value=None):
        # Spawn enemy at random position around player
        spawn_angle = random.uniform(0, 2 * math.pi)
        spawn_distance = random.uniform(300, 450)
        
        self.x = spawn_distance * math.sin(spawn_angle)
        self.z = spawn_distance * math.cos(spawn_angle)
        self.y = 15
        self.speed = random.uniform(0.05, 0.5)
        self.scale = 1.0  # For pulsing animation
        self.scale_direction = 0.02
        self.hit = False
        self.target = False

    def update(self):
        # Move towards player
        player_dx = player_pos[0] - self.x
        player_dz = player_pos[2] - self.z
        distance_to_player = math.sqrt(player_dx * player_dx + player_dz * player_dz)

        if distance_to_player > 0:
            move_x = (player_dx / distance_to_player) * self.speed
            move_z = (player_dz / distance_to_player) * self.speed
            self.x += move_x
            self.z += move_z

        # Pulsing animation
        self.scale += self.scale_direction
        if self.scale > 1.2 or self.scale < 0.8:
            self.scale_direction *= -1

    def draw(self):
        if self.hit:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(self.scale, self.scale, self.scale)

        # body
        glColor3f(1, 0, 0)
        gluSphere(gluNewQuadric(), 15, 20, 20)

        # head 
        glColor3f(0, 0, 0)
        glTranslatef(0, 15, 0)
        gluSphere(gluNewQuadric(), 10, 16, 16)

        glPopMatrix()

    def check_collision_with_player(self):
        dx = player_pos[0] - self.x
        dz = player_pos[2] - self.z
        collision_distance = math.sqrt(dx * dx + dz * dz)
        return collision_distance < 30

    def check_collision_with_bullet(self, bullet):
        dx = bullet.x - self.x
        dz = bullet.z - self.z
        collision_distance = math.sqrt(dx * dx + dz * dz)
        return collision_distance < 15

# Draw the player character
def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], 0, player_pos[2])
    glRotatef(player_angle, 0, 1, 0)

    # Fall over when game over
    if game_over:
        glRotatef(90, 1, 0, 0)

    # legs
    glColor3f(0.6, 0.0, 1.0)
    leg_positions = [7, -7]
    for x_pos in leg_positions:
        glPushMatrix()
        glTranslatef(x_pos, 20, 0)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 6, 3, 25, 12, 6)
        glPopMatrix()

    # body 
    glColor3f(0.2, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(0, 35, 0)
    glScalef(20, 30, 10)
    glutSolidCube(1)
    glPopMatrix()

    # head 
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 60, 0)
    gluSphere(gluNewQuadric(), 10, 16, 16)
    glPopMatrix()
    
    # arms
    glColor3f(0.8, 0.7, 0.6)
    arm_positions = [-12, 12]
    for x_pos in arm_positions:
        glPushMatrix()
        glTranslatef(x_pos, 45, 0)
        glRotatef(0, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 2, 18, 12, 2)
        glPopMatrix()
        
    # gun 
    if not game_over:
        glColor3f(0.7, 0.7, 0.7)
        glPushMatrix()
        glTranslatef(0, 38, 12)
        gluCylinder(gluNewQuadric(), 3.5, 2, 20, 12, 2)
        glPopMatrix()

    glPopMatrix()

#  hand and gun in fps
def draw_first_person_arms_and_gun():
    global player_pos, player_angle, player_height, game_over
    if game_over:
        return

    angle_rad = math.radians(player_angle)

    # Camera position in first person
    cam_x = player_pos[0]
    cam_y = player_pos[1] + player_height + 30
    cam_z = player_pos[2]

    # viewmodel centered
    forward_offset = 12.0
    right_offset = 0.0
    vertical_offset = -6.0

    forward_x = math.sin(angle_rad)
    forward_z = math.cos(angle_rad)
    right_x = math.cos(angle_rad)
    right_z = -math.sin(angle_rad)

    base_x = cam_x + forward_offset * forward_x + right_offset * right_x
    base_y = cam_y + vertical_offset
    base_z = cam_z + forward_offset * forward_z + right_offset * right_z

    
    glDisable(GL_DEPTH_TEST)
    glPushMatrix()
    glTranslatef(base_x, base_y, base_z)
    glRotatef(player_angle, 0, 1, 0)

    # Gun centered
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(0, -3, 0)
    gluCylinder(gluNewQuadric(), 3.0, 2.6, 14, 16, 2)
    glPopMatrix()

    # Muzzle tip
    glPushMatrix()
    glTranslatef(0, -3, 14)
    gluSphere(gluNewQuadric(), 2.6, 12, 12)
    glPopMatrix()

    # Right forearm
    glColor3f(0.8, 0.7, 0.6)
    glPushMatrix()
    glTranslatef(5, -4, -3)
    gluCylinder(gluNewQuadric(), 2.5, 2.0, 10, 12, 2)
    glPopMatrix()

    # Left forearm
    glPushMatrix()
    glTranslatef(-5, -4, -3)
    gluCylinder(gluNewQuadric(), 2.5, 2.0, 10, 12, 2)
    glPopMatrix()

    glPopMatrix()
    glEnable(GL_DEPTH_TEST)

# Draw game status information
def draw_status():
    draw_text(10, 770, f"Player Life Remaining: {player_lives}")
    draw_text(10, 740, f"Game Score: {game_score}")
    draw_text(10, 710, f"Player Bullet Missed: {bullets_missed}")
    draw_text(10, 680, f"Camera Mode: {'First Person' if follow_camera else 'Third Person'}")
    draw_text(10, 650, f"Cheat Mode: {'ON' if cheat_mode else 'OFF'}")

    if game_over:
        draw_text(400, 400, "GAME OVER - Press R to restart")

# Draw the game arena floor and walls
def draw_floor():
    tile_size = 50
    grid_rows, grid_cols = 20, 20

    glBegin(GL_QUADS)
    # Draw checkered floor pattern
    for row in range(-grid_rows // 2, grid_rows // 2):
        for col in range(-grid_cols // 2, grid_cols // 2):
            if (row + col) % 2 == 0:
                glColor3f(1, 1, 1)  # White tiles
            else:
                glColor3f(0.6, 0.4, 0.8)  # Purple tiles

            x_start = row * tile_size
            z_start = col * tile_size
            x_end = (row + 1) * tile_size
            z_end = (col + 1) * tile_size

            glVertex3f(x_start, -1, z_start)
            glVertex3f(x_end, -1, z_start)
            glVertex3f(x_end, -1, z_end)
            glVertex3f(x_start, -1, z_end)

    # Draw boundary walls with different colors
    boundary_half = BOUNDARY_SIZE / 2
    wall_height = 50
    
    # Front wall (white)
    glColor3f(1, 1, 1)
    glVertex3f(-boundary_half, -1, -boundary_half)
    glVertex3f(boundary_half, -1, -boundary_half)
    glVertex3f(boundary_half, wall_height, -boundary_half)
    glVertex3f(-boundary_half, wall_height, -boundary_half)

    # Right wall (green)
    glColor3f(0, 1, 0)
    glVertex3f(boundary_half, -1, -boundary_half)
    glVertex3f(boundary_half, -1, boundary_half)
    glVertex3f(boundary_half, wall_height, boundary_half)
    glVertex3f(boundary_half, wall_height, -boundary_half)

    # Back wall (cyan)
    glColor3f(0, 1, 1)
    glVertex3f(boundary_half, -1, boundary_half)
    glVertex3f(-boundary_half, -1, boundary_half)
    glVertex3f(-boundary_half, wall_height, boundary_half)
    glVertex3f(boundary_half, wall_height, boundary_half)

    # Left wall (blue)
    glColor3f(0, 0, 1)
    glVertex3f(-boundary_half, -1, boundary_half)
    glVertex3f(-boundary_half, -1, -boundary_half)
    glVertex3f(-boundary_half, wall_height, -boundary_half)
    glVertex3f(-boundary_half, wall_height, boundary_half)
    glEnd()




# Main game logic update
def update_game():
    global bullets, enemies, game_score, player_lives, bullets_missed, game_over, game_over_print

    if game_over:
        if not game_over_print:
            print("Player Died. Game Over!! Better Luck Next Time")
            game_over_print = True
        return

    # Update bullets and remove dead ones
    active_bullets = []
    for bullet in bullets:
        bullet.update()
        if bullet.is_alive():
            active_bullets.append(bullet)
        else:
            # Count missed bullets (hit boundary, not enemy)
            if not bullet.hit_enemy:
                bullets_missed += 1
                print(f"Player missed bullet:{bullets_missed}")
                if bullets_missed >= MAX_MISSED_BULLETS:
                    game_over = True
    bullets = active_bullets

    # Maintain enemy count
    while len(enemies) < MAX_ENEMIES:
        enemies.append(Enemy())

    # Update enemies and handle collisions
    active_enemies = []
    for enemy in enemies:
        enemy.update()

        #  player collision
        if enemy.check_collision_with_player():
            player_lives -= 1
            print(f"Player Remaining Life:{player_lives}")
            if player_lives <= 0:
                game_over = True
            enemy.respawn()

        # bullet collisions
        enemy_hit = False
        for bullet in bullets:
            if not bullet.hit and enemy.check_collision_with_bullet(bullet):
                bullet.hit = True
                bullet.hit_enemy = True
                enemy.hit = True
                game_score += 1
                enemy.respawn()
                enemy_hit = True
                break

        if not enemy_hit:
            active_enemies.append(enemy)
    enemies = active_enemies




# Draw all bullets
def draw_all_bullets():
    for bullet in bullets:
        bullet.draw()

# Draw all enemies
def draw_all_enemies():
    for enemy in enemies:
        enemy.draw()




# Set up camera view (first  or third person)
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos

    if follow_camera:  # First person view
        eye_elevation = player_height + 30
        cam_x = player_pos[0]
        cam_y = player_pos[1] + eye_elevation
        cam_z = player_pos[2]

        # Look in direction player is facing
        look_distance = 100
        player_angle_rad = math.radians(player_angle)
        look_x = cam_x + look_distance * math.sin(player_angle_rad)
        look_y = cam_y
        look_z = cam_z + look_distance * math.cos(player_angle_rad)

        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
        
    else:  # Third person view
        gluLookAt(x, y, z,
                  player_pos[0], player_pos[1], player_pos[2],
                  0, 1, 0)

# Fire a bullet from player position
def fire_bullet():
    global bullets, bullets_missed

    target_enemy = None
    if cheat_mode:
        # Find closest enemy for homing bullet
        closest_distance = float('inf')
        closest_enemy = None

        for enemy in enemies:
            if not enemy.hit and not enemy.target:
                dx = enemy.x - player_pos[0]
                dz = enemy.z - player_pos[2]
                distance = math.sqrt(dx * dx + dz * dz)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_enemy = enemy

        if closest_enemy:
            target_enemy = closest_enemy
            target_enemy.target = True

    # Spawn at gun muzzle 
    angle_rad = math.radians(player_angle)
    forward_x = math.sin(angle_rad)
    forward_z = math.cos(angle_rad)

    if follow_camera:
        # Match first-person viewmodel positioning
        cam_x = player_pos[0]
        cam_y = player_pos[1] + player_height + 30
        cam_z = player_pos[2]

        forward_offset = 12.0
        right_offset = 0.0
        vertical_offset = -6.0

        right_x = math.cos(angle_rad)
        right_z = -math.sin(angle_rad)

        base_x = cam_x + forward_offset * forward_x + right_offset * right_x
        base_y = cam_y + vertical_offset
        base_z = cam_z + forward_offset * forward_z + right_offset * right_z

        # Gun muzzle position
        gun_x = base_x + 14.0 * forward_x
        gun_y = base_y - 3.0
        gun_z = base_z + 14.0 * forward_z
        bullets.append(Bullet(gun_x, gun_y, gun_z, player_angle, target_enemy))
    else:
        # Match third-person player gun geometry: local (0, 38, 12) + barrel length 20 => z = 32
        gun_muzzle_offset = 32.0
        gun_x = player_pos[0] + gun_muzzle_offset * forward_x
        gun_y = player_pos[1] + 38.0
        gun_z = player_pos[2] + gun_muzzle_offset * forward_z
        bullets.append(Bullet(gun_x, gun_y, gun_z, player_angle, target_enemy))
    print("Player fired bullet")

# Move player with boundary checking
def move_player(dx, dz):
    global player_pos

    new_x = player_pos[0] + dx
    new_z = player_pos[2] + dz

    boundary_limit = (BOUNDARY_SIZE / 2) - 30

    # Only move if within boundaries
    if abs(new_x) < boundary_limit and abs(new_z) < boundary_limit:
        player_pos[0] = new_x
        player_pos[2] = new_z

# Main render function
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    
    draw_floor()

    # Don't draw player in first person view (unless game over)
    if not follow_camera or game_over:
        draw_player()
    else:
        draw_first_person_arms_and_gun()

    draw_all_bullets()
    draw_all_enemies()
    draw_status()

    glutSwapBuffers()

# Handle keyboard input
def keyboardListener(key, x, y):
    global player_pos, player_angle, cheat_mode, follow_camera, game_over, game_over_print

    if game_over:
        if key == b'r':  # Restart game
            reset_game()
            if game_over_print == True:
                game_over_print = False
        return

    player_angle_rad = math.radians(player_angle)
    movement_distance = 5

    # Movement controls (WASD)
    if key == b's' or key == b'S':  # Move backward
        dx = -movement_distance * math.sin(player_angle_rad)
        dz = -movement_distance * math.cos(player_angle_rad)
        move_player(dx, dz)
    elif key == b'w' or key == b'W':  # Move forward
        dx = movement_distance * math.sin(player_angle_rad)
        dz = movement_distance * math.cos(player_angle_rad)
        move_player(dx, dz)
    elif key == b'a' or key == b'A':  # Turn left
        player_angle += 5
    elif key == b'd' or key == b'D':  # Turn right
        player_angle -= 5
    elif key == b'c' or key == b'C':  # Toggle cheat mode
        cheat_mode = not cheat_mode
    
    # Camera switching (only available in cheat mode)
    if cheat_mode == True:
        if key == b'v' or key == b'V':
            follow_camera = not follow_camera

# Handle special keys (arrow keys for camera movement)
def specialKeyListener(key, x, y):
    global camera_pos
    
    cam_x, cam_y, cam_z = camera_pos

    if key == GLUT_KEY_LEFT:
        cam_x -= 5
    elif key == GLUT_KEY_RIGHT:
        cam_x += 5
    elif key == GLUT_KEY_UP:
        cam_y += 5
    elif key == GLUT_KEY_DOWN:
        cam_y -= 5

    camera_pos = (cam_x, cam_y, cam_z)
    
# Handle mouse clicks
def mouseListener(button, state, x, y):
    global follow_camera

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:  # Fire bullet
        fire_bullet()

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:  # Toggle camera
        follow_camera = not follow_camera

# Reset all game variables to initial state
def reset_game():
    global player_pos, player_angle, bullets, enemies
    global cheat_mode, follow_camera
    global game_score, player_lives, bullets_missed, game_over

    player_pos = [0.0, 0.0, 0.0]
    player_angle = 0.0
    bullets = []
    enemies = []
    cheat_mode = False
    follow_camera = False
    game_score = 0
    player_lives = 5
    bullets_missed = 0
    game_over = False

# Auto-aim functionality for cheat mode
def execute_cheat_mode():
    global player_angle

    closest_enemy = None
    minimum_distance = float('inf')
    
    # Find closest enemy
    for enemy in enemies:
        if enemy.hit or enemy.target:
            continue

        dx = enemy.x - player_pos[0]
        dz = enemy.z - player_pos[2]
        distance = math.sqrt(dx * dx + dz * dz)

        if distance < minimum_distance:
            minimum_distance = distance
            closest_enemy = enemy

    if closest_enemy:
        # Calculate angle to enemy
        dx = closest_enemy.x - player_pos[0]
        dz = closest_enemy.z - player_pos[2]
        angle_to_enemy = math.degrees(math.atan2(dx, dz))

        # Normalize angles
        while angle_to_enemy < 0:
            angle_to_enemy += 360

        target_angle = 360 - angle_to_enemy
        while target_angle >= 360:
            target_angle -= 360

        # Smooth rotation towards target
        angle_difference = target_angle - player_angle
        while angle_difference > 180:
            angle_difference -= 360
        while angle_difference < -180:
            angle_difference += 360

        player_angle += angle_difference * 0.1

        # Auto-fire when aimed
        if abs(angle_difference) < 10 and random.random() < 0.2:
            fire_bullet()


# Idle function - called continuously
def idle():
    update_game()

    if cheat_mode and not game_over:
        execute_cheat_mode()

    glutPostRedisplay()

# Main function - initialize and start game
def main():
    global enemies
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D OpenGL Intro")

    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for 3D

    # Initialize enemies
    for _ in range(MAX_ENEMIES):
        enemies.append(Enemy())

    # Register callback functions
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()  # Start the main loop

if __name__ == "__main__":
    main()