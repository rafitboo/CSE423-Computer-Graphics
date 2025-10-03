from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Variables
catcher_pos = 210
catcher_w = 80
catcher_h = 20
diamond_pos_x = random.randint(50, 450)
diamond_pos_y = 500
diamond_size = 15
fall_speed = 100   #pixel/s
score = 0
is_game_over = False
is_paused = False
prev_time = time.time()

# Colors
WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
YELLOW = (1.0, 1.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
TEAL = (0.0, 1.0, 1.0)
AMBER = (1.0, 0.8, 0.0)
CYAN = (0.0, 1.0, 1.0)
MAGENTA = (1.0, 0.0, 1.0)

color_options = [RED, YELLOW, GREEN, BLUE, CYAN, MAGENTA]
diamond_color = random.choice(color_options)

#MPL
def determine_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) >= abs(dy):
        if dx > 0 and dy >= 0:
            return 0
        elif dx <= 0 and dy > 0:
            return 3
        elif dx < 0 and dy <= 0:
            return 4
        else:  # dx >= 0 and dy < 0
            return 7
    else:
        if dx > 0 and dy > 0:
            return 1
        elif dx <= 0 and dy > 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else: # dx > 0 and dy <= 0
            return 6

def to_zone0(x, y, zone):
    #Zone X to 0
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def from_zone0(x, y, zone):
    #Zone 0 to X
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def midpoint_algorithm(x1, y1, x2, y2):
    #MPL for zone 0
    points = []
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    E = 2 * dy
    NE = 2 * (dy - dx)
    y = y1
    
    for x in range(x1, x2 + 1):
        points.append((x, y))
        if d > 0:
            d += NE
            y += 1
        else:
            d += E
    
    return points

def render_line(x1, y1, x2, y2):
    # Handle edge case if points are the same
    if x1 == x2 and y1 == y2:
        glBegin(GL_POINTS)
        glVertex2f(x1, y1)
        glEnd()
        return
    # Making lines left to right
    if x1 > x2:
        x1, y1, x2, y2 = x2, y2, x1, y1
    
    zone = determine_zone(x1, y1, x2, y2)
    
    # Convert to zone 0
    x1_z0, y1_z0 = to_zone0(x1, y1, zone)
    x2_z0, y2_z0 = to_zone0(x2, y2, zone)
    
    # Making lines left to right
    if x1_z0 > x2_z0:
        x1_z0, y1_z0, x2_z0, y2_z0 = x2_z0, y2_z0, x1_z0, y1_z0
    
    # Points in zone 0
    line_points = midpoint_algorithm(x1_z0, y1_z0, x2_z0, y2_z0)
    
    # Convert back to original zone
    glBegin(GL_POINTS)
    for px, py in line_points:
        orig_x, orig_y = from_zone0(px, py, zone)
        glVertex2f(orig_x, orig_y)
    glEnd()

def draw_diamond():
    glColor3f(*diamond_color)
    
    # Diamond with 4 lines
    render_line(int(diamond_pos_x), int(diamond_pos_y), int(diamond_pos_x + diamond_size), int(diamond_pos_y + diamond_size)) # left to Top
    render_line(int(diamond_pos_x + diamond_size), int(diamond_pos_y + diamond_size), int(diamond_pos_x + 2*diamond_size), int(diamond_pos_y)) # Right 
    render_line(int(diamond_pos_x + 2*diamond_size), int(diamond_pos_y), int(diamond_pos_x + diamond_size), int(diamond_pos_y - diamond_size)) # Bottom
    render_line(int(diamond_pos_x + diamond_size), int(diamond_pos_y - diamond_size), int(diamond_pos_x), int(diamond_pos_y)) # Left

def draw_catcher():
    if is_game_over:
        glColor3f(*RED)
    else:
        glColor3f(*WHITE)
        
    # Catcher with 4 lines
    render_line(int(catcher_pos), 30, int(catcher_pos + catcher_w), 30)  #top
    render_line(int(catcher_pos + catcher_w), 30, int(catcher_pos + catcher_w-10), 10) # right
    render_line(int(catcher_pos + catcher_w-10), 10, int(catcher_pos+10), 10) # bottom
    render_line(int(catcher_pos+10), 10, int(catcher_pos), 30)  # left

def draw_restart_btn():
    glColor3f(*TEAL)
    render_line(50, 480, 30, 470) # Top
    render_line(30, 470, 50, 460) # Bottom
    render_line(30, 470, 60, 470) # Horizontal

def draw_play_pause_btn():
    glColor3f(*AMBER)
    if is_paused:
        # Play Button (Triangle)
        render_line(235, 460, 235, 480) # Left
        render_line(235, 480, 255, 470) # Top
        render_line(255, 470, 235, 460) # Right
    else:
        # Pause Button (Two Rectangles)
        # Rectangle 1
        render_line(235, 460, 235, 480) # Left
        render_line(235, 480, 242, 480) # Top
        render_line(242, 480, 242, 460) # Right
        render_line(242, 460, 235, 460) # Bottom
        # Rectangle 2
        render_line(248, 460, 248, 480) # Left
        render_line(248, 480, 255, 480) # Top
        render_line(255, 480, 255, 460) # Right
        render_line(255, 460, 248, 460) # Bottom

def draw_exit_btn():
    glColor3f(*RED)
    # X btn
    render_line(450, 460, 470, 480) # Diagonal /
    render_line(450, 480, 470, 460) # Diagonal \

def draw_buttons():
    draw_restart_btn()
    draw_play_pause_btn()
    draw_exit_btn()
    
    
# Collision Detection (AABB)
def check_collision():
    # Diamond boundaries
    diamond_left = diamond_pos_x
    diamond_right = diamond_pos_x + 2 * diamond_size
    diamond_top = diamond_pos_y + diamond_size
    diamond_bottom = diamond_pos_y - diamond_size
    
    # Catcher boundaries
    catcher_left = catcher_pos
    catcher_right = catcher_pos + catcher_w
    catcher_top = 30
    catcher_bottom = 10
    
    return (diamond_left < catcher_right and
            diamond_right > catcher_left and
            diamond_top > catcher_bottom and
            diamond_bottom < catcher_top)


# Game logic
def new_diamond():
    global diamond_pos_x, diamond_pos_y, fall_speed, diamond_color
    diamond_pos_x = random.randint(50, 400)
    diamond_pos_y = 500
    fall_speed += 10 # Increase fall speed
    diamond_color = random.choice(color_options)

def init_game():
    global score, fall_speed, is_game_over, is_paused, catcher_pos
    score = 0
    fall_speed = 100
    is_game_over = False
    is_paused = False
    catcher_pos = 210
    new_diamond()
    print("Starting Over")

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_buttons()
    draw_catcher()
    
    if not is_game_over:
        draw_diamond()
    
    glutSwapBuffers()

def handle_keys(key, x, y):
    global catcher_pos
    if not is_game_over and not is_paused:
        if key == GLUT_KEY_LEFT and catcher_pos > 0:
            catcher_pos -= 20
        elif key == GLUT_KEY_RIGHT and catcher_pos + catcher_w < 500:
            catcher_pos += 20
        glutPostRedisplay()

def handle_mouse(button, state, x, y):
    global is_game_over, is_paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = 500 - y # Convert GLUT coordinates
        
        #Restart Btn
        if 20 <= x <= 70 and 450 <= y <= 490:
            init_game()
            
        # Play/Pause Btn
        elif 220 <= x <= 270 and 450 <= y <= 490:
            if not is_game_over:
                is_paused = not is_paused
        
        # Exit Btn
        elif 440 <= x <= 480 and 450 <= y <= 490:
            print(f"Goodbye! Final Score: {score}")
            glutLeaveMainLoop()
        
        glutPostRedisplay()

def update_game():
    global diamond_pos_y, score, is_game_over, prev_time
    
    curr_time = time.time()
    delta = curr_time - prev_time
    prev_time = curr_time
    
    if not is_paused and not is_game_over:
        
        diamond_pos_y -= fall_speed * delta # Moving diamnd using delta time
        
        # If diamond reached bottom
        if diamond_pos_y <= 40:
            if check_collision():
                score += 1
                print(f"Score: {score}")
                new_diamond()
            else:
                print(f"Game Over! Final Score: {score}")
                is_game_over = True
    
    glutPostRedisplay()

def idle():
    update_game()


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(500, 500)
glutInitWindowPosition(700, 200)
glutCreateWindow(b"Catch the Diamonds!")

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, 500, 0, 500)
glMatrixMode(GL_MODELVIEW)

glClearColor(0.0, 0.0, 0.0, 1.0)

glutDisplayFunc(display)
glutSpecialFunc(handle_keys)
glutMouseFunc(handle_mouse)
glutIdleFunc(idle)

print("Game Controls:")
print("- Use LEFT/RIGHT arrow keys to move the catcher")
print("- Click the teal arrow button to restart")
print("- Click the amber button to play/pause")
print("- Click the red X button to exit")
print("- Catch the falling diamonds to score points!")

glutMainLoop()

