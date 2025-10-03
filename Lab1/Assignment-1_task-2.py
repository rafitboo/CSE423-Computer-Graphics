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
        # Normalized coordinates
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