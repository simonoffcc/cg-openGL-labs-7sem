import sys
import random
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Константы ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAX_PARTICLES = 2000
TIME_STEP = 0.016 

GRAVITY_VECTOR = np.array([0.0, 0.0, 0.0])

# Параметры эмиттера (Конус)
CONE_HEIGHT = 2.0
CONE_RADIUS = 1.0
CONE_APEX = np.array([0.0, 0.0, 0.0]) 
EMISSION_RATE = 8

# Параметры боковой плоскости
PLANE_X_POS = 3.0  # Сдвинута вправо на 3 единицы

# Цвета
COLOR_START = np.array([0.0, 1.0, 1.0]) 
COLOR_END = np.array([1.0, 0.0, 1.0])   

# Глобальные переменные
particles = []
view_rot_x = 20.0
view_rot_y = 0.0
is_top_view = False # Флаг для переключения вида

class Particle:
    def __init__(self):
        self.active = False
        self.pos = np.zeros(3)
        self.vel = np.zeros(3)
        self.life = 0.0
        self.max_life = 1.0
        self.color = np.zeros(3)

    def spawn(self):
        self.active = True
        self.life = 0.0
        self.max_life = random.uniform(5.0, 8.0)
        
        h_factor = random.random() 
        current_h = h_factor * CONE_HEIGHT
        current_r = h_factor * CONE_RADIUS
        angle = random.uniform(0, 2 * math.pi)
        
        lx = current_r * math.cos(angle)
        ly = -current_h 
        lz = current_r * math.sin(angle)
        
        self.pos = CONE_APEX + np.array([lx, ly, lz])
        
        slant_len = math.hypot(CONE_RADIUS, CONE_HEIGHT)
        cos_slope = CONE_HEIGHT / slant_len
        sin_slope = CONE_RADIUS / slant_len
        
        nx = math.cos(angle) * cos_slope
        ny = sin_slope 
        nz = math.sin(angle) * cos_slope
        
        normal = np.array([nx, ny, nz])
        speed = random.uniform(0.5, 1.5)
        self.vel = normal * speed

    def update(self, dt):
        if not self.active: return

        self.vel += GRAVITY_VECTOR * dt
        self.pos += self.vel * dt
        
        # Столкновение с боковой плоскостью
        if self.pos[0] >= PLANE_X_POS:
             self.pos[0] = PLANE_X_POS - 0.01
             self.vel[0] = -self.vel[0] * 0.8 

        self.life += dt
        t = self.life / self.max_life
        self.color = (1 - t) * COLOR_START + t * COLOR_END

        if self.life >= self.max_life:
            self.active = False

def init():
    glClearColor(0.05, 0.05, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glPointSize(3.0)
    global particles
    particles = [Particle() for _ in range(MAX_PARTICLES)]

def draw_emitter_wireframe():
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glTranslatef(CONE_APEX[0], CONE_APEX[1] - CONE_HEIGHT, CONE_APEX[2])
    glRotatef(-90, 1, 0, 0) 
    glutWireCone(CONE_RADIUS, CONE_HEIGHT, 40, 10)
    glPopMatrix()

def draw_vertical_plane():
    glColor3f(0.6, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(PLANE_X_POS, 0, 0)
    glBegin(GL_LINES)
    size = 5.0
    step = 1.0
    for z in np.arange(-size, size + step, step):
        glVertex3f(0, -size, z)
        glVertex3f(0, size, z)
    for y in np.arange(-size, size + step, step):
        glVertex3f(0, y, -size)
        glVertex3f(0, y, size)
    glEnd()
    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Переключение камеры
    if is_top_view:
        # Вид сверху: камера смотрит на сцену с высоты
        gluLookAt(0, 15, 0.01, 0, 0, 0, 0, 0, -1)
    else:
        # Стандартный вид сбоку
        gluLookAt(0, 2, 20, 0, 0, 0, 0, 1, 0)
        glRotatef(view_rot_x, 1, 0, 0) # Наклоняем только в боковом виде
    
    # Вращение вокруг оси Y оставляем для обоих видов
    glRotatef(view_rot_y, 0, 1, 0)

    draw_emitter_wireframe()
    draw_vertical_plane()

    glBegin(GL_POINTS)
    for p in particles:
        if p.active:
            glColor3fv(p.color)
            glVertex3fv(p.pos)
    glEnd()

    glutSwapBuffers()

def timer(value):
    spawn_count = 0
    for p in particles:
        if not p.active and spawn_count < EMISSION_RATE:
            p.spawn()
            spawn_count += 1
    
    for p in particles:
        p.update(TIME_STEP)
    
    global view_rot_y
    view_rot_y += 0.1 
    
    glutPostRedisplay()
    glutTimerFunc(int(TIME_STEP * 1000), timer, 0)

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# Функция для обработки нажатий клавиш
def keyboard(key, x, y):
    global is_top_view
    
    # Переключение вида
    if key == b't' or key == b'T':
        is_top_view = not is_top_view
        view_mode = "Top-Down" if is_top_view else "Perspective"
        print(f"View mode: {view_mode}")
        
    # Выход по Escape
    elif key == b'\x1b':
        sys.exit()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Particle System: Press 'T' for Top View")
    
    init()
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(0, timer, 0)
    glutKeyboardFunc(keyboard) # Регистрируем функцию клавиатуры
    
    glutMainLoop()

if __name__ == "__main__":
    main()
