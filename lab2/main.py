import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

# --- Глобальные параметры ---
# Освещение
light_pos = [4.0, 6.0, 4.0, 1.0]
light_color = [1.0, 1.0, 1.0, 1.0]
light_intensity = 1.0

# Камера и анимация
camera_angle = 0.0
is_rotating = True  # Тоггл вращения

# Текстура
texture_id = None

# --- Управление освещением ---
def move_light(dx, dy, dz):
    light_pos[0] += dx
    light_pos[1] += dy
    light_pos[2] += dz

def change_light_color(r, g, b):
    light_color[0] = r
    light_color[1] = g
    light_color[2] = b

# --- Текстура ---
def load_texture(filename):
    try:
        img = Image.open(filename)
        img_data = img.convert("RGBA").tobytes()
        w, h = img.size
    except FileNotFoundError:
        # Fallback-процедурная текстура (шахматная)
        w, h = 64, 64
        img_data = bytearray()
        for y in range(h):
            for x in range(w):
                if (x // 8 + y // 8) % 2 == 0:
                    img_data.extend([180, 140, 100, 255])
                else:
                    img_data.extend([130, 90, 50, 255])
        img_data = bytes(img_data)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex_id

# --- Инициализация ---
def init():
    global texture_id
    glClearColor(0.2, 0.2, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    texture_id = load_texture("texture.jpg")
    glShadeModel(GL_SMOOTH)

# --- Рисование ---
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Камера на уровне фигур
    radius = 18.0
    cam_x = math.sin(camera_angle) * radius
    cam_z = math.cos(camera_angle) * radius
    gluLookAt(cam_x, 3.0, cam_z, 0.0, 1.5, 0.0, 0.0, 1.0, 0.0)

    # Источник света с учетом интенсивности
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    final_light_color = [light_color[i] * light_intensity for i in range(3)] + [1.0]
    glLightfv(GL_LIGHT0, GL_DIFFUSE, final_light_color)
    glLightfv(GL_LIGHT0, GL_SPECULAR, final_light_color)

    # 1) Текстурированный матовый конус
    glPushMatrix()
    glTranslatef(-6.0, 0.0, 0.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 10.0)
    draw_textured_cone(1.5, 4.0, 32)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

    # 2) Отполированный тор (внутренний радиус шире)
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 128.0)
    # glutSolidTorus(innerRadius, outerRadius, nsides, rings)
    glutSolidTorus(0.8, 2.0, 32, 64)
    glPopMatrix()

    # 3) Полупрозрачный цилиндр
    glPushMatrix()
    glTranslatef(6.0, 0.0, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.2, 0.8, 0.5, 0.55])  # alpha > 0.5
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 0.6])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    q = gluNewQuadric()
    gluCylinder(q, 1.0, 1.0, 4.0, 32, 1)
    glPushMatrix()
    glRotatef(180.0, 1.0, 0.0, 0.0)
    gluDisk(q, 0.0, 1.0, 32, 1)
    glPopMatrix()
    glTranslatef(0.0, 0.0, 4.0)
    gluDisk(q, 0.0, 1.0, 32, 1)
    gluDeleteQuadric(q)
    glDisable(GL_BLEND)
    glPopMatrix()

    glutSwapBuffers()

def draw_textured_cone(radius, height, slices):
    # Боковая поверхность
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, 1.0, 0.0)
    glTexCoord2f(0.5, 1.0)
    glVertex3f(0.0, height, 0.0)  # вершина
    for i in range(slices + 1):
        angle = 2.0 * math.pi * i / slices
        nx, nz = math.cos(angle), math.sin(angle)
        glNormal3f(nx, 0.0, nz)
        glTexCoord2f(i / slices, 0.0)
        glVertex3f(radius * nx, 0.0, radius * nz)
    glEnd()

    # Основание
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, -1.0, 0.0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0.0, 0.0, 0.0)  # центр
    for i in range(slices + 1):
        angle = 2.0 * math.pi * i / slices
        x, z = math.cos(angle), math.sin(angle)
        glTexCoord2f(0.5 + 0.5 * x, 0.5 + 0.5 * z)
        glVertex3f(radius * x, 0.0, radius * z)
    glEnd()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w) / float(h if h > 0 else 1), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

# --- Обработчики ввода ---
def keyboard(key, x, y):
    # Без декодирования UTF-8 (фикс для Windows/freeglut)
    global light_intensity, is_rotating

    # Нормализуем регистр для латинских букв (A..Z -> a..z)
    if 65 <= key[0] <= 90:  # 'A'..'Z'
        k = bytes([key[0] + 32])
    else:
        k = key

    # Движение источника света (WASD)
    step = 0.5
    if k == b'w':
        move_light(0.0, step, 0.0)
    elif k == b's':
        move_light(0.0, -step, 0.0)
    elif k == b'a':
        move_light(-step, 0.0, 0.0)
    elif k == b'd':
        move_light(step, 0.0, 0.0)

    # Цвет света
    elif k == b'1':
        change_light_color(1.0, 1.0, 1.0)      # белый
    elif k == b'2':
        change_light_color(1.0, 0.2, 0.2)      # красный
    elif k == b'3':
        change_light_color(0.2, 0.2, 1.0)      # синий

    # Интенсивность света (+/= увеличивает, - уменьшает)
    elif k in (b'+', b'='):
        light_intensity = min(light_intensity + 0.1, 5.0)
    elif k == b'-':
        light_intensity = max(light_intensity - 0.1, 0.0)

    # Тоггл вращения камеры
    elif k == b'r':
        is_rotating = not is_rotating

    # Esc — выход
    elif k == b'\x1b':
        sys.exit(0)

    glutPostRedisplay()

def update(value):
    global camera_angle
    if is_rotating:
        camera_angle += 0.01
        if camera_angle > 2.0 * math.pi:
            camera_angle -= 2.0 * math.pi
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # ~60 FPS

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Scene: Textured Cone, Polished Torus, Transparent Cylinder")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == '__main__':
    main()
