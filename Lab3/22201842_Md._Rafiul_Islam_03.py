from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random




game_over_print = False
player_pos = [0.0, 0.0, 0.0]
player_angle = 0.0
player_height = 15.0
bullets = []
enemies = []
cheat_mode = False
follow_camera = False
camera_pos = (0, 800, 200)
game_score = 0
player_lives = 5
bullets_missed = 0
game_over = False
MAX_ENEMIES = 5
MAX_MISSED_BULLETS = 10
BOUNDARY_SIZE = 1000
fovY = 60




def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): # type: ignore
    glColor3f(1, 0, 0)
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



class Bullet:
    def __init__(self, x, y, z, angle, target_enemy=None):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.hit = False
        self.hit_enemy = False
        self.target_enemy = target_enemy


    def update(self):
        if self.hit:
            return

        movement_speed = 1

        if self.target_enemy and not self.target_enemy.hit:
            dx = self.target_enemy.x - self.x
            dz = self.target_enemy.z - self.z
            dy = self.target_enemy.y - self.y

            total_distance = math.sqrt(dx * dx + dz * dz + dy * dy)

            if total_distance > 0:
                self.x += (dx / total_distance) * movement_speed
                self.y += (dy / total_distance) * movement_speed
                self.z += (dz / total_distance) * movement_speed
        else:
            angle_radians = math.radians(self.angle)
            new_x = self.x + movement_speed * math.sin(angle_radians)
            new_z = self.z + movement_speed * math.cos(angle_radians)

            boundary_limit = (BOUNDARY_SIZE / 2) - 5

            if abs(new_x) < boundary_limit and abs(new_z) < boundary_limit:
                self.x = new_x
                self.z = new_z
            else:
                self.hit = True
                
                
    def is_alive(self):
        return not self.hit
    
    
    def draw(self):
        glPushMatrix()
        glColor3f(1, 0, 0)
        glTranslatef(self.x, self.y, self.z)
        glutSolidCube(6)
        glPopMatrix()



class Enemy:
    def __init__(self):
        self.respawn()
        self.target = False
        self.hit = False

 
    def respawn(self, value=None):
        spawn_angle = random.uniform(0, 2 * math.pi)
        spawn_distance = random.uniform(300, 450)
        
        self.x = spawn_distance * math.sin(spawn_angle)
        self.z = spawn_distance * math.cos(spawn_angle)
        self.y = 15
        self.speed = random.uniform(0.05, 0.5)
        self.scale = 1.0
        self.scale_direction = 0.02
        self.hit = False
        self.target = False


    def update(self):
        player_dx = player_pos[0] - self.x
        player_dz = player_pos[2] - self.z
        distance_to_player = math.sqrt(player_dx * player_dx + player_dz * player_dz)

        if distance_to_player > 0:
            move_x = (player_dx / distance_to_player) * self.speed
            move_z = (player_dz / distance_to_player) * self.speed
            self.x += move_x
            self.z += move_z

        self.scale += self.scale_direction
        
        if self.scale > 1.2 or self.scale < 0.8:
            self.scale_direction *= -1


    def draw(self):
        if self.hit:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(self.scale, self.scale, self.scale)

        glColor3f(1, 0, 0)
        gluSphere(gluNewQuadric(), 15, 20, 20)

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

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], 0, player_pos[2])
    glRotatef(player_angle, 0, 1, 0)

    if game_over:
        glRotatef(90, 1, 0, 0)

    # Legs
    glColor3f(0.6, 0.0, 1.0)
    leg_positions = [7, -7]
    for x_pos in leg_positions:
        glPushMatrix()
        glTranslatef(x_pos, 20, 0)
        glRotatef(90, 1, 0, 0)
        
        gluCylinder(gluNewQuadric(), 6, 3, 25, 12, 6)
        glPopMatrix()

    #Body
    glColor3f(0.2, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(0, 35, 0)
    glScalef(20, 30, 10)
    glutSolidCube(1)
    glPopMatrix()

    # Head
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 60, 0)
    gluSphere(gluNewQuadric(), 10, 16, 16)
    glPopMatrix()
    
    #Arms
    glColor3f(0.8, 0.7, 0.6)
    arm_positions = [-12, 12]
    for x_pos in arm_positions:
        glPushMatrix()
        glTranslatef(x_pos, 45, 0)
        glRotatef(0, 1, 0, 0)
        
        gluCylinder(gluNewQuadric(), 4, 2, 18, 12, 2)
        glPopMatrix()
        
    # Gun
    if not game_over:
        glColor3f(0.7, 0.7, 0.7)
        glPushMatrix()
        glTranslatef(0, 38, 12)
        
        gluCylinder(gluNewQuadric(), 3.5, 2, 20, 12, 2)
        glPopMatrix()

    glPopMatrix()


def draw_status():
    draw_text(10, 770, f"Player Life Remaining: {player_lives}")
    draw_text(10, 740, f"Game Score: {game_score}")
    draw_text(10, 710, f"Player Bullet Missed: {bullets_missed}")
    draw_text(10, 680, f"Camera Mode: {'First Person' if follow_camera else 'Third Person'}")
    draw_text(10, 650, f"Cheat Mode: {'ON' if cheat_mode else 'OFF'}")

    if game_over:
        draw_text(400, 400, "GAME OVER - Press R to restart")


def draw_floor():
    tile_size = 50
    grid_rows, grid_cols = 20, 20

    glBegin(GL_QUADS)
    for row in range(-grid_rows // 2, grid_rows // 2):
        for col in range(-grid_cols // 2, grid_cols // 2):
            if (row + col) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.6, 0.4, 0.8)

            x_start = row * tile_size
            z_start = col * tile_size
            x_end = (row + 1) * tile_size
            z_end = (col + 1) * tile_size

            glVertex3f(x_start, -1, z_start)
            glVertex3f(x_end, -1, z_start)
            glVertex3f(x_end, -1, z_end)
            glVertex3f(x_start, -1, z_end)

    boundary_half = BOUNDARY_SIZE / 2
    wall_height = 50
    
    glColor3f(1, 1, 1)
    glVertex3f(-boundary_half, -1, -boundary_half)
    glVertex3f(boundary_half, -1, -boundary_half)
    glVertex3f(boundary_half, wall_height, -boundary_half)
    glVertex3f(-boundary_half, wall_height, -boundary_half)

    glColor3f(0, 1, 0)
    glVertex3f(boundary_half, -1, -boundary_half)
    glVertex3f(boundary_half, -1, boundary_half)
    glVertex3f(boundary_half, wall_height, boundary_half)
    glVertex3f(boundary_half, wall_height, -boundary_half)

    glColor3f(0, 1, 1)
    glVertex3f(boundary_half, -1, boundary_half)
    glVertex3f(-boundary_half, -1, boundary_half)
    glVertex3f(-boundary_half, wall_height, boundary_half)
    glVertex3f(boundary_half, wall_height, boundary_half)

    glColor3f(0, 0, 1)
    glVertex3f(-boundary_half, -1, boundary_half)
    glVertex3f(-boundary_half, -1, -boundary_half)
    glVertex3f(-boundary_half, wall_height, -boundary_half)
    glVertex3f(-boundary_half, wall_height, boundary_half)
    glEnd()


def update_game():
    global bullets, enemies, game_score, player_lives, bullets_missed, game_over, game_over_print

    if game_over:
        if not game_over_print:
            print("Player Died. Game Over!! Better Luck Next Time")
            game_over_print = True
        return

    active_bullets = []
    for bullet in bullets:
        bullet.update()
        if bullet.is_alive():
            active_bullets.append(bullet)
        else:
            if not bullet.hit_enemy:
                bullets_missed += 1
                print(f"Player missed bullet:{bullets_missed}")
                if bullets_missed >= MAX_MISSED_BULLETS:
                    game_over = True
    bullets = active_bullets

    while len(enemies) < MAX_ENEMIES:
        enemies.append(Enemy())

    active_enemies = []
    for enemy in enemies:
        enemy.update()

        if enemy.check_collision_with_player():
            player_lives -= 1
            print(f"Player Remaining Life:{player_lives}")
            if player_lives <= 0:
                game_over = True
            enemy.respawn()

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


def draw_all_bullets():
    for bullet in bullets:
        bullet.draw()


def draw_all_enemies():
    for enemy in enemies:
        enemy.draw()


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos

    if follow_camera:
        eye_elevation = player_height + 30
        cam_x = player_pos[0]
        cam_y = player_pos[1] + eye_elevation
        cam_z = player_pos[2]

        look_distance = 100
        player_angle_rad = math.radians(player_angle)
        look_x = cam_x + look_distance * math.sin(player_angle_rad)
        look_y = cam_y
        look_z = cam_z + look_distance * math.cos(player_angle_rad)

        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
    else:
        gluLookAt(x, y, z,
                  player_pos[0], player_pos[1], player_pos[2],
                  0, 1, 0)


def fire_bullet():
    global bullets, bullets_missed

    target_enemy = None
    if cheat_mode:
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

    if follow_camera:
        gun_x = player_pos[0]
        gun_y = player_pos[1] + player_height + 10
        gun_z = player_pos[2]
        bullets.append(Bullet(gun_x, gun_y, gun_z, player_angle, target_enemy))
    else:
        gun_offset = 25
        player_angle_rad = math.radians(player_angle)
        gun_x = player_pos[0] + gun_offset * math.sin(player_angle_rad)
        gun_y = player_pos[1] + 35
        gun_z = player_pos[2] + gun_offset * math.cos(player_angle_rad)

        bullets.append(Bullet(gun_x, gun_y, gun_z, player_angle, target_enemy))
    print("Player fired bullet")


def move_player(dx, dz):
    global player_pos

    new_x = player_pos[0] + dx
    new_z = player_pos[2] + dz

    boundary_limit = (BOUNDARY_SIZE / 2) - 30

    if abs(new_x) < boundary_limit and abs(new_z) < boundary_limit:
        player_pos[0] = new_x
        player_pos[2] = new_z


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    
    draw_floor()

    if not follow_camera or game_over:
        draw_player()

    draw_all_bullets()
    draw_all_enemies()
    draw_status()

    glutSwapBuffers()


def keyboardListener(key, x, y):
    global player_pos, player_angle, cheat_mode, follow_camera, game_over, game_over_print

    if game_over:
        if key == b'r':
            reset_game()
            if game_over_print == True:
                game_over_print = False
        return

    player_angle_rad = math.radians(player_angle)
    movement_distance = 5

    if key == b's' or key == b'S':
        dx = -movement_distance * math.sin(player_angle_rad)
        dz = -movement_distance * math.cos(player_angle_rad)
        move_player(dx, dz)
    elif key == b'w' or key == b'W':
        dx = movement_distance * math.sin(player_angle_rad)
        dz = movement_distance * math.cos(player_angle_rad)
        move_player(dx, dz)
    elif key == b'a' or key == b'A':
        player_angle += 5
    elif key == b'd' or key == b'D':
        player_angle -= 5
    elif key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
    
    if cheat_mode == True:
        if key == b'v' or key == b'V':
            follow_camera = not follow_camera


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
    

def mouseListener(button, state, x, y):
    global follow_camera

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        follow_camera = not follow_camera


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


def execute_cheat_mode():
    global player_angle

    closest_enemy = None
    minimum_distance = float('inf')
    
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
        dx = closest_enemy.x - player_pos[0]
        dz = closest_enemy.z - player_pos[2]
        angle_to_enemy = math.degrees(math.atan2(dx, dz))

        while angle_to_enemy < 0:
            angle_to_enemy += 360

        target_angle = 360 - angle_to_enemy
        while target_angle >= 360:
            target_angle -= 360

        angle_difference = target_angle - player_angle
        while angle_difference > 180:
            angle_difference -= 360
        while angle_difference < -180:
            angle_difference += 360

        player_angle += angle_difference * 0.1

        if abs(angle_difference) < 10 and random.random() < 0.2:
            fire_bullet()


def manage_enemy_targeting():
    for enemy in enemies:
        if enemy.hit:
            enemy.target = False

        if enemy.target:
            bullet_tracking = False
            for bullet in bullets:
                if bullet.target_enemy == enemy and bullet.is_alive():
                    bullet_tracking = True
                    break

            if not bullet_tracking:
                enemy.target = False


def idle():
    update_game()

    if cheat_mode and not game_over:
        execute_cheat_mode()

    manage_enemy_targeting()
    glutPostRedisplay()


def main():
    global enemies
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D OpenGL Intro")

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    for _ in range(MAX_ENEMIES):
        enemies.append(Enemy())

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()