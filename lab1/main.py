import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Параметры фигур и анимации
cone_radius = 150
cone1_height = 250
cone2_height = 500
num_segments = 50

torus_inner_radius = 30
torus_outer_radius = 80
torus_num_sides = 20
torus_num_rings = 20

cylinder_radius = 60
cylinder_height = 200
cylinder_num_segments = 30

animation_duration = 3000

# Переменные состояния
scene_state = 1
rotation_angle = 0
start_time_anim = 0
start_time_anim_scene4 = 0
window_width = 800
window_height = 600
is_rotation_enabled = True

# Функции отрисовки
def draw_cone(radius, height, segments):
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_LINE)
    gluCylinder(quad, radius, 0, height, segments, 1)
    gluDeleteQuadric(quad)

def draw_torus(inner_radius, outer_radius, sides, rings):
    glutWireTorus(inner_radius, outer_radius, sides, rings)

def draw_cylinder(radius, height, segments):
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_LINE)
    gluCylinder(quad, radius, radius, height, segments, 1)
    gluDeleteQuadric(quad)

# Основная функция отрисовки
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Настройка камеры
    gluPerspective(50, (window_width / window_height), 0.1, 1500.0)
    glTranslatef(0.0, -150.0, -1000) # Чуть смещаем для лучшего обзора
    glRotatef(25, 1, 0, 0)

    # Общее вращение всей сцены
    glPushMatrix()
    glRotatef(rotation_angle, 0, 1, 0)

    # Логика отрисовки для каждой сцены
    if scene_state == 1:
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glColor3f(1, 0, 0)  # Красный
        draw_cone(cone_radius, cone1_height, num_segments)
        glColor3f(0, 0, 1)  # Синий
        draw_cone(cone_radius, cone2_height, num_segments)
        glPopMatrix()

    elif scene_state == 2:
        current_time = glutGet(GLUT_ELAPSED_TIME) - start_time_anim
        cone1_rotation_x = 0
        if current_time < animation_duration:
            cone1_rotation_x = 90 * (current_time / animation_duration)
        else:
            cone1_rotation_x = 90

        # Анимированный конус (маленький)
        glPushMatrix()
        glRotatef(cone1_rotation_x, 1, 0, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1, 0, 0)  # Красный
        draw_cone(cone_radius, cone1_height, num_segments)
        glPopMatrix()

        # Статичный конус (большой)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glColor3f(0, 0, 1)  # Синий
        draw_cone(cone_radius, cone2_height, num_segments)
        glPopMatrix()

    elif scene_state == 3:
        glPushMatrix()
        glTranslatef(-200, 100, 0)
        glColor3f(0, 1, 0)  # Зелёный
        draw_torus(torus_inner_radius, torus_outer_radius, torus_num_sides, torus_num_rings)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(200, 100, 0)
        glRotatef(90, 1, 0, 0)
        glColor3f(1, 1, 0)  # Желтый
        draw_cylinder(cylinder_radius, cylinder_height, cylinder_num_segments)
        glPopMatrix()

    elif scene_state == 4:
        # Расчет анимации для 4-й сцены
        current_time = glutGet(GLUT_ELAPSED_TIME) - start_time_anim_scene4
        progress = min(current_time / animation_duration, 1.0) # Прогресс от 0.0 до 1.0

        # Начальные позиции (как в сцене 3)
        start_x_torus = -200.0
        start_x_cylinder = 200.0
        
        # Конечные позиции для пересечения
        end_x_torus = -60.0
        end_x_cylinder = 60.0

        # Интерполяция позиций для обеих фигур
        torus_x = start_x_torus + (end_x_torus - start_x_torus) * progress
        cylinder_x = start_x_cylinder + (end_x_cylinder - start_x_cylinder) * progress

        # Анимированный тор
        glPushMatrix()
        glTranslatef(torus_x, 100, 0)
        glColor3f(0, 1, 0)  # Зелёный
        draw_torus(torus_inner_radius, torus_outer_radius, torus_num_sides, torus_num_rings)
        glPopMatrix()

        # Анимированный цилиндр
        glPushMatrix()
        glTranslatef(cylinder_x, 100, 0)
        glRotatef(90, 1, 0, 0)
        glColor3f(1, 1, 0)  # Желтый
        draw_cylinder(cylinder_radius, cylinder_height, cylinder_num_segments)
        glPopMatrix()

    glPopMatrix()
    glutSwapBuffers()

# Функция для анимации и обновления
def idle():
    global rotation_angle
    if is_rotation_enabled:
        rotation_angle += 0.02
    glutPostRedisplay()

# Функция обработки клавиатуры
def keyboard(key, x, y):
    global scene_state, start_time_anim, start_time_anim_scene4, is_rotation_enabled
    key = key.decode("utf-8")
    if key == '1':
        scene_state = 1
    elif key == '2':
        scene_state = 2
        start_time_anim = glutGet(GLUT_ELAPSED_TIME)
    elif key == '3':
        scene_state = 3
    elif key == '4':
        scene_state = 4
        start_time_anim_scene4 = glutGet(GLUT_ELAPSED_TIME)
    elif key == '5':
        is_rotation_enabled = not is_rotation_enabled
    elif key == '\x1b':  # Клавиша ESC
        sys.exit()

# --- Функция обработки изменения размера окна ---
def reshape(w, h):
    global window_width, window_height
    window_width = w
    window_height = h
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Lab 1")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
