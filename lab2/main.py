import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image


# Глобальные параметры и переключатели
light_pos = [4.0, 6.0, 4.0, 1.0]
light_color = [1.0, 1.0, 1.0, 1.0]
light_intensity = 1.0

camera_angle = 0.0
is_rotating = True

is_texture_enabled = True   # T - вкл/выкл текстуру
is_bump_enabled = False     # B - вкл/выкл bump-mapping

texture_id = None

# Функции управления светом
def move_light(dx, dy, dz):
    light_pos[0] += dx
    light_pos[1] += dy
    light_pos[2] += dz

def change_light_color(r, g, b):
    light_color[0] = r
    light_color[1] = g
    light_color[2] = b


# Визуализация источника света
def draw_light_gizmo():
    glPushAttrib(GL_CURRENT_BIT | GL_LIGHTING_BIT | GL_ENABLE_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 0.2)

    glPushMatrix()
    glTranslatef(light_pos[0], light_pos[1], light_pos[2])
    glutSolidSphere(0.2, 16, 16)
    glPopMatrix()
    glPopAttrib()

# Загрузка текстуры
def load_texture(filename):
    try:
        img = Image.open(filename).convert("RGBA")
        w, h = img.size
        img_data = img.tobytes()
        print(f"Текстура '{filename}' успешно загружена.")
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден. Используется процедурная текстура.")
        w, h = 64, 64
        img_data = bytearray()
        for y in range(h):
            for x in range(w):
                c = 180 if ((x//8 + y//8) % 2 == 0) else 120
                img_data.extend([c, c, c, 255])
        img_data = bytes(img_data)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, w, h, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    try:
        from OpenGL.raw.GL.EXT.texture_filter_anisotropic import GL_TEXTURE_MAX_ANISOTROPY_EXT
        max_aniso = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, min(8.0, max_aniso))
    except Exception:
        pass
    return tex


# Инициализация OpenGL
def init():
    global texture_id
    glClearColor(0.2, 0.2, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    texture_id = load_texture("texture.jpg")

# Отрисовка всей сцены
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    radius = 18.0
    cam_x = math.sin(camera_angle) * radius
    cam_z = math.cos(camera_angle) * radius
    gluLookAt(cam_x, 3.0, cam_z, 0.0, 1.5, 0.0, 0.0, 1.0, 0.0)

    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    final_light = [light_color[i] * light_intensity for i in range(3)] + [1.0]
    glLightfv(GL_LIGHT0, GL_DIFFUSE, final_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, final_light)

    draw_light_gizmo()

    # 1. Матовый текстурированный конус
    glPushMatrix()
    glTranslatef(-6.0, 0.0, 0.0)
    if is_texture_enabled:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    else:
        glDisable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.7, 0.6, 0.5, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.05, 0.05, 0.05, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 8.0)
    draw_textured_cone(1.5, 4.0, 64)
    if is_texture_enabled: glDisable(GL_TEXTURE_2D)
    glPopMatrix()

    # 2. Отполированный тор
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 128.0)
    glutSolidTorus(0.8, 2.0, 32, 64)
    glPopMatrix()

    # 3. Полупрозрачный цилиндр
    glPushMatrix()
    glTranslatef(6.0, 0.0, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.2, 0.8, 0.5, 0.55])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 0.6])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    q = gluNewQuadric()
    gluCylinder(q, 1.0, 1.0, 4.0, 32, 1)
    glPushMatrix(); glRotatef(180.0, 1, 0, 0); gluDisk(q, 0, 1, 32, 1); glPopMatrix()
    glTranslatef(0, 0, 4); gluDisk(q, 0, 1, 32, 1)
    gluDeleteQuadric(q)
    glDisable(GL_BLEND)
    glPopMatrix()

    glutSwapBuffers()


# Отрисовка конуса с bump-mapping
def draw_textured_cone(radius, height, slices):
    v_scale = 0.5
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, 1.0, 0.0)
    glTexCoord2f(0.5, v_scale)
    glVertex3f(0.0, height, 0.0)
    for i in range(slices + 1):
        angle = 2.0 * math.pi * i / slices
        nx, nz = math.cos(angle), math.sin(angle)
        if is_bump_enabled:
            perturb = 0.15 * math.sin(20.0 * angle)
            glNormal3f(nx + perturb, 0.0, nz + perturb)
        else:
            glNormal3f(nx, 0.0, nz)
        glTexCoord2f(i / slices, 0.0)
        glVertex3f(radius * nx, 0.0, radius * nz)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, -1.0, 0.0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(slices + 1):
        angle = 2.0 * math.pi * i / slices
        x, z = math.cos(angle), math.sin(angle)
        glTexCoord2f(0.5 + 0.5 * x, 0.5 + 0.5 * z)
        glVertex3f(radius * x, 0.0, radius * z)
    glEnd()

# Служебные функции GLUT
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w) / float(h if h > 0 else 1), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global light_intensity, is_rotating, is_texture_enabled, is_bump_enabled
    if 65 <= key[0] <= 90:
        k = bytes([key[0] + 32])
    else:
        k = key

    step = 0.5
    if k == b'w': move_light(0.0, step, 0.0)
    elif k == b's': move_light(0.0, -step, 0.0)
    elif k == b'a': move_light(-step, 0.0, 0.0)
    elif k == b'd': move_light(step, 0.0, 0.0)
    elif k == b'q': move_light(0.0, 0.0, -step)
    elif k == b'e': move_light(0.0, 0.0, step)
    elif k == b'1': change_light_color(1.0, 1.0, 1.0)
    elif k == b'2': change_light_color(1.0, 0.2, 0.2)
    elif k == b'3': change_light_color(0.2, 0.2, 1.0)
    elif k in (b'+', b'='): light_intensity = min(light_intensity + 0.1, 5.0)
    elif k == b'-': light_intensity = max(light_intensity - 0.1, 0.0)
    elif k == b'r': is_rotating = not is_rotating
    elif k == b't': is_texture_enabled = not is_texture_enabled
    elif k == b'b': is_bump_enabled = not is_bump_enabled
    elif k == b'\x1b': sys.exit(0)
    else: pass
    
    glutPostRedisplay()

def update(value):
    global camera_angle
    if is_rotating:
        camera_angle += 0.01
        if camera_angle > 2.0 * math.pi:
            camera_angle -= 2.0 * math.pi
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


# Точка входа
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(960, 720)
    glutCreateWindow(b"Graphics Lab - Final Version")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == '__main__':
    main()
