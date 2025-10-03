# ###################################### Task-1 ######################################

# from OpenGL.GL import *   
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import random  
# import time


# WIDTH, HEIGHT = 800, 600

# # Transition variables
# transition_step = 0
# transition_target = None
# transition_colors = []
# last_update_time = time.time()
# last_transition_time = time.time()
# transitioning = False # Flag to check transition 

# # Rain charactaristics
# num_drops = 400
# extra_x_range = 600  # add buffer
# rain_drops = [(random.randint(-400 - extra_x_range, 400 + extra_x_range), 
#                random.randint(-300, 300)) for _ in range(num_drops)]
# rain_speed = -5 
# rain_direction = -2 


# sky_color = [0, 0, 0] # Initial sky color (black)

# # Helper mouse tracker
# a_list_for_mouse = []
# def mouse_motion(x, y):
#     x_gl = x - (WIDTH // 2)
#     y_gl = (HEIGHT // 2) - y
#     a_list_for_mouse.append((x_gl,y_gl))
#     print(f"Mouse at: ({x_gl}, {y_gl})") 

# def display():
    

#     glClear(GL_COLOR_BUFFER_BIT)
#     glLoadIdentity()

#     # Background Color ( day/night effect)
#     glClearColor(*sky_color, 1.0)  # Unpack RGB from list
#     glClear(GL_COLOR_BUFFER_BIT)

#     # Sky (top part)
#     glColor3f(*sky_color)
#     glBegin(GL_QUADS)
#     glVertex2f(-WIDTH // 2, -50)  
#     glVertex2f(WIDTH // 2, -50)
#     glVertex2f(WIDTH // 2, HEIGHT // 2)
#     glVertex2f(-WIDTH // 2, HEIGHT // 2)
#     glEnd()

#     # Ground (bottom part) 
#     glColor3f(101/255, 67/255, 33/255) # Brown
#     glBegin(GL_QUADS)
#     glVertex2f(WIDTH // 2, 20)
#     glVertex2f(-WIDTH // 2, 20)
#     glVertex2f(-WIDTH // 2, -HEIGHT // 2)
#     glVertex2f(WIDTH // 2, -HEIGHT // 2)
#     glEnd()
    
#     # Green Trees
#     glColor3f(0,0.7,0) 
#     for i in range(-400, 400, 80):
#         glBegin(GL_TRIANGLES)
#         glVertex2f(i, -80)
#         glVertex2f(i + 40, 0)
#         glVertex2f(i + 80, -80)
#         glEnd()
             
#     # House
#     glColor3f(139/255, 69/255, 90/255) #Walls
#     glBegin(GL_QUADS)
#     glVertex2f(-130, -50)
#     glVertex2f(130, -50)
#     glVertex2f(130, -150)
#     glVertex2f(-130, -150)
#     glEnd()

#     glColor3f(255/255, 182/255, 193/255) #pinky Roof
#     glBegin(GL_TRIANGLES)
#     glVertex2f(-150, -50)
#     glVertex2f(150, -50)
#     glVertex2f(0, 50)
#     glEnd()

#     glColor3f(0.0, 0.4, 1)  # Blue Door
#     glBegin(GL_QUADS)
#     glVertex2f(-20, -150)
#     glVertex2f(20, -150)
#     glVertex2f(20, -80)
#     glVertex2f(-20, -80)
#     glEnd()

#     # Windows
#     glColor3f(0.3, 0.6, 1.0)  # Sky Blue Windows
#     glBegin(GL_QUADS)
#     glVertex2f(-90, -100)
#     glVertex2f(-50, -100)
#     glVertex2f(-50, -70)
#     glVertex2f(-90, -70)
#     glEnd()
#     glBegin(GL_QUADS)
#     glVertex2f(50, -100)
#     glVertex2f(90, -100)
#     glVertex2f(90, -70)
#     glVertex2f(50, -70)
#     glEnd()

#     # Window Plus Sign
#     # Right Window "+"
#     glColor3f(0, 0, 0)
#     glBegin(GL_LINES)
#     glVertex2f(70, -100)
#     glVertex2f(70, -70)
#     glEnd()
#     glBegin(GL_LINES)
#     glVertex2f(90, -85)
#     glVertex2f(50, -85)
#     glEnd()
    
#     # Left Window "+"
#     glColor3f(0, 0, 0)  # Black Color for Plus Sign 
#     glBegin(GL_LINES)
#     glVertex2f(-70, -70)
#     glVertex2f(-70, -100)
#     glEnd()
#     glBegin(GL_LINES)
#     glVertex2f(-90, -85)
#     glVertex2f(-50, -85)
#     glEnd()

#     # Pathway
#     glColor3f(0.45, 0.45, 0.45)
#     glBegin(GL_QUADS)
#     glVertex2f(-20, -150)   # top-narrow
#     glVertex2f(20, -150)
#     glVertex2f(50, -300)    # bottom-wide
#     glVertex2f(-50, -300)
#     glEnd()
    
#     # Door Knob
#     glColor3f(0, 0, 0)  # black Knob
#     glPointSize(10)
#     glBegin(GL_POINTS)
#     glVertex2f(10, -105)
#     glEnd()
    
#     #Chimney
#     glColor3f(139/255, 69/255, 90/255)
#     glBegin(GL_QUADS)
#     glVertex2f(70, 3)   
#     glVertex2f(43, 21)
#     glVertex2f(43, 40)    
#     glVertex2f(70, 40)
#     glEnd()
#     glColor3f(0.45, 0.45, 0.45)
#     glBegin(GL_QUADS)
#     glVertex2f(35, 40) 
#     glVertex2f(78, 40)
#     glVertex2f(78, 53)
#     glVertex2f(35, 53)    
#     glEnd()
    
    

#     # Rain Drops
#     glColor3f(0.7, 0.9, 1.0) # Light Blue 
#     glBegin(GL_LINES)
#     for i in range(len(rain_drops)):
#         x, y = rain_drops[i]
#         glVertex2f(x, y) # Rain starting point
#         glVertex2f(x + rain_direction * 3, y - 20) # Rain end -20 size, dirction * 3 means angle with x


#     glEnd()
    
#     global last_update_time, last_transition_time
    
#     current_time = time.time()
    
#     # rain animation 
#     if current_time - last_update_time > 0.02:  # 20ms = 0.02 seconds
#         update_rain()
#         last_update_time = current_time
    
#     # sky transition 
#     if transitioning and current_time - last_transition_time > 0.5:  # 500ms = 0.5second
#         perform_sky_transition()
#         last_transition_time = current_time

#     glutSwapBuffers()
#     glutPostRedisplay()  # Continuous redraw 

# def update_rain():
#     global rain_drops
#     for i in range(len(rain_drops)):
#         x, y = rain_drops[i]
        
#         # Update y (falling down)
#         y += rain_speed
#         # x shift left or right based on direction)
#         x += rain_direction * 2  
#         # Reset if bottom
#         if y < -300:
#             y = 300
#             x = random.randint(-400 - extra_x_range, 400 + extra_x_range)  # reset to random x position
        
#         rain_drops[i] = (x, y)

# def idle():
#     glutPostRedisplay()
    
# def start_sky_transition(target_mode):
#     global transitioning, transition_colors, transition_step, last_transition_time

#     if target_mode == "day":
#         transition_colors = [
#             [0, 0, 0],                    # Night (black)
#             [50 / 255, 50 / 255, 50 / 255],  # Dark gray
#             [200 / 255, 200 / 255, 200 / 255],  # Light gray
#             [100/255, 180/255, 255/255]   # Day (sky blue)
#         ]
#     elif target_mode == "night":
#         transition_colors = [
#             [100/255, 180/255, 255/255],   # Day (sky blue)
#             [200 / 255, 200 / 255, 200 / 255], # Light gray
#             [50 / 255, 50 / 255, 50 / 255],    # Dark gray
#             [0, 0, 0]                          # Night (black)
#         ]

#     transition_step = 0
#     transitioning = True
#     last_transition_time = time.time()

# def perform_sky_transition():
#     global transition_step, transitioning, sky_color

#     if transition_step < len(transition_colors):
#         sky_color = transition_colors[transition_step]
#         transition_step += 1
#     else:
#         transitioning = False  # transition shesh

# def keyboard(key, x, y):
#     global transitioning

#     if key == b'd' or key == b'D' and not transitioning:
#         # if already in day 
#         if sky_color != [100/255, 180/255, 255/255]:
#             start_sky_transition("day")

#     elif key == b'n' or key == b'N' and not transitioning:
#         # if already in night
#         if sky_color != [0, 0, 0]:
#             start_sky_transition("night")

#     glutPostRedisplay()

# def special_keys (key,x,y):
#     global rain_direction
#     if key == GLUT_KEY_LEFT:
#         rain_direction -= 1
#     elif key == GLUT_KEY_RIGHT:
#         rain_direction += 1
#     glutPostRedisplay()

# glutInit()
# glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
# glutInitWindowSize(WIDTH, HEIGHT)
# glutInitWindowPosition(0, 0)
# glutCreateWindow(b"House with Rain Animation and Day Night Transition")
# glutDisplayFunc(display)
# glutKeyboardFunc(keyboard)
# glutSpecialFunc(special_keys)
# glutIdleFunc(idle)  
# glutPassiveMotionFunc(mouse_motion)  # Track mouse movement
# glMatrixMode(GL_PROJECTION) # Switch to projection matrix
# glLoadIdentity() # Reset projection matrix
# glOrtho(-400, 400, -300, 300, -1, 1)
# glMatrixMode(GL_MODELVIEW) # Switch back to model-view matrix 
# glutMainLoop()







###################################### Task-2 ######################################

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Global Variables
WIDTH, HEIGHT = 800, 600

movement_speed = 1.5
point_data = []
is_blinking = False
is_frozen = False
dots_visible = True
last_update_time = time.time()
last_blink_time = time.time()

def initialize_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(8)

def render_scene():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    glBegin(GL_POINTS)
    for point in point_data:
        # Show points if blinking is off 
        if is_blinking and not dots_visible:
            continue
        position, velocity, color = point
        glColor3f(*color)
        glVertex2f(*position)
    glEnd()
    
    glFlush()
    glutSwapBuffers()

def update_physics():
    global last_update_time, last_blink_time, dots_visible
    current_time = time.time()
    
    # Update point positions at 60 FPS
    if current_time - last_update_time >= 1.0/60.0:
        if not is_frozen:
            for i in range(len(point_data)):
                position, velocity, color = point_data[i]
                x, y = position
                dx, dy = velocity
                
                # New position
                new_x = x + dx * movement_speed
                new_y = y + dy * movement_speed
                
                # Boundary cases
                if new_x <= -1.0:
                    new_x = -1.0
                    dx = -dx
                elif new_x >= 1.0:
                    new_x = 1.0
                    dx = -dx
                
                if new_y <= -1.0:
                    new_y = -1.0
                    dy = -dy
                elif new_y >= 1.0:
                    new_y = 1.0
                    dy = -dy
                
                point_data[i] = ((new_x, new_y), (dx, dy), color)
        
        last_update_time = current_time
    
    # Blinking at 1 second intervals
    if current_time - last_blink_time >= 1.0:
        if is_blinking:
            dots_visible = not dots_visible
        last_blink_time = current_time
    
    glutPostRedisplay()

def mouse_click(button, state, x, y):
    global is_blinking, dots_visible
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Screen coordinates to normalized device coordinates
        normalized_x = (x / WIDTH) * 2 - 1
        normalized_y = 1 - (y / HEIGHT) * 2
        
        # Making points inside boundaries
        normalized_x = max(-1.0, min(1.0, normalized_x))
        normalized_y = max(-1.0, min(1.0, normalized_y))
        
        # Random diagonal velocity
        speed_magnitude = 0.01
        dx = random.choice([-speed_magnitude, speed_magnitude])
        dy = random.choice([-speed_magnitude, speed_magnitude])
        velocity = (dx, dy)
        
        # Generate random color
        color = (random.random(), random.random(), random.random())
        
        point_data.append(((normalized_x, normalized_y), velocity, color))
    
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        is_blinking = not is_blinking
        if not is_blinking:
            dots_visible = True
    
    glutPostRedisplay()

def keyboard_input(key, x, y):
    global is_frozen
    
    if key == b' ':
        is_frozen = not is_frozen
    elif key == b'l':
        # Debug info - print current state of all points
        debug_info = [
            (f"x={point[0][0]:.3f}", f"y={point[0][1]:.3f}",
             f"speed_x={point[1][0]:.3f}", f"speed_y={point[1][1]:.3f}")
            for point in point_data
        ]
        print("Points Info:", debug_info)
    
    glutPostRedisplay()

def special_keys(key, x, y):
    global movement_speed
    
    if key == GLUT_KEY_UP:
        movement_speed *= 1.2
    elif key == GLUT_KEY_DOWN:
        movement_speed *= 0.8
    
    glutPostRedisplay()


# Initialize GLUT
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WIDTH, HEIGHT)
glutCreateWindow(b"Amazing Box")

initialize_opengl()

# Set up event handlers
glutDisplayFunc(render_scene)
glutMouseFunc(mouse_click)
glutKeyboardFunc(keyboard_input)
glutSpecialFunc(special_keys)
glutIdleFunc(update_physics)

glutMainLoop()