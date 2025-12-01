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
MAX_PARTICLES = 800
TIME_STEP = 0.016 

# Параметры сцены
GRAVITY = np.array([0.0, -5.0, 0.0])
PLANE_LEVEL = -3.0

# Параметры эмиттера (Конус)
CONE_HEIGHT = 5.0
CONE_RADIUS = 2.5
CONE_APEX = np.array([0.0, 3.0, 0.0]) 
EMISSION_RATE = 8

# Цвета (R, G, B)
COLOR_START = np.array([0.0, 1.0, 1.0]) # Циан
COLOR_END = np.array([1.0, 0.0, 1.0])   # Маджента

# Глобальные переменные
particles = []
view_rot_x = 20.0
view_rot_y = 0.0

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
        self.max_life = random.uniform(2.0, 4.0)
        
        # Генерация точки на поверхности конуса
        # Конус вершиной вверх, основание внизу (относительно APEX)
        h_factor = random.random() # 0..1 (доля высоты от вершины)
        current_h = h_factor * CONE_HEIGHT
        current_r = h_factor * CONE_RADIUS
        angle = random.uniform(0, 2 * math.pi)
        
        # Позиция на поверхности (локальная)
        lx = current_r * math.cos(angle)
        ly = -current_h # Смещаемся вниз от вершины
        lz = current_r * math.sin(angle)
        
        self.pos = CONE_APEX + np.array([lx, ly, lz])
        
        # Нормаль к поверхности конуса для направления скорости
        # Нормаль наклонена вверх
        slant_len = math.hypot(CONE_RADIUS, CONE_HEIGHT)
        cos_slope = CONE_HEIGHT / slant_len
        sin_slope = CONE_RADIUS / slant_len
        
        nx = math.cos(angle) * cos_slope
        ny = sin_slope 
        nz = math.sin(angle) * cos_slope
        
        normal = np.array([nx, ny, nz])
        speed = random.uniform(1.5, 3.0)
        self.vel = normal * speed

    def update(self, dt):
        if not self.active: return

        # Физика
        self.vel += GRAVITY * dt
        self.pos += self.vel * dt
        
        # Столкновение с плоскостью
        if self.pos[1] <= PLANE_LEVEL:
            self.pos[1] = PLANE_LEVEL + 0.001
            self.vel[1] = -self.vel[1] * 0.7 # Отскок с затуханием
            self.vel[0] *= 0.9 # Трение
            self.vel[2] *= 0.9

        # Жизненный цикл и цвет
        self.life += dt
        t = self.life / self.max_life
        self.color = (1 - t) * COLOR_START + t * COLOR_END

        if self.life >= self.max_life:
            self.active = False

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glPointSize(3.0)
    
    global particles
    particles = [Particle() for _ in range(MAX_PARTICLES)]

def draw_emitter_wireframe():
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glTranslatef(CONE_APEX[0], CONE_APEX[1] - CONE_HEIGHT, CONE_APEX[2])
    glRotatef(-90, 1, 0, 0) # GLUT конус ориентирован по Z
    glutWireCone(CONE_RADIUS, CONE_HEIGHT, 10, 5)
    glPopMatrix()

def draw_plane():
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINES)
    step = 2.0
    size = 20.0
    y = PLANE_LEVEL
    for i in np.arange(-size, size + step, step):
        glVertex3f(i, y, -size)
        glVertex3f(i, y, size)
        glVertex3f(-size, y, i)
        glVertex3f(size, y, i)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    gluLookAt(0, 2, 15, 0, 0, 0, 0, 1, 0)
    glRotatef(view_rot_x, 1, 0, 0)
    glRotatef(view_rot_y, 0, 1, 0)

    draw_plane()
    draw_emitter_wireframe()

    glBegin(GL_POINTS)
    for p in particles:
        if p.active:
            glColor3fv(p.color)
            glVertex3fv(p.pos)
    glEnd()

    glutSwapBuffers()

def timer(value):
    # Эмиссия
    spawn_count = 0
    for p in particles:
        if not p.active and spawn_count < EMISSION_RATE:
            p.spawn()
            spawn_count += 1
    
    # Обновление
    for p in particles:
        p.update(TIME_STEP)
    
    global view_rot_y
    view_rot_y += 0.2 # Вращение камеры
    
    glutPostRedisplay()
    glutTimerFunc(int(TIME_STEP * 1000), timer, 0)

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Particle System: Cone & Plane")
    
    init()
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(0, timer, 0)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
