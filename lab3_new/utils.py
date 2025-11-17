# File: utils.py
from pyglm import glm
from OpenGL.GL import *
from PIL import Image

# --- Матрицы ---
def lookAt(eye, center, up):
    return glm.lookAt(glm.vec3(*eye), glm.vec3(*center), glm.vec3(*up))

def perspective(fov, aspect, near, far):
    return glm.perspective(glm.radians(fov), aspect, near, far)

def ortho(left, right, bottom, top, near, far):
    return glm.ortho(left, right, bottom, top, near, far)

def translate(x, y, z):
    return glm.translate(glm.mat4(1.0), glm.vec3(x, y, z))

def scale(x, y, z):
    return glm.scale(glm.mat4(1.0), glm.vec3(x, y, z))

def rotation_matrix(angle_x, angle_y):
    m = glm.mat4(1.0)
    m = glm.rotate(m, glm.radians(angle_x), glm.vec3(1, 0, 0))
    m = glm.rotate(m, glm.radians(angle_y), glm.vec3(0, 1, 0))
    return m

def set_mat4_uniform(program, name, mat):
    loc = glGetUniformLocation(program, name)
    if loc != -1:
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(mat))

# VAO   - Vertex Array Object
# EBO   - Element Buffer Object (индексы)
# VBO   - Vertex Buffer Object
def draw_vao_elements(VAO, EBO, count):
    glBindVertexArray(VAO)
    if EBO:
        glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, None)
    else:
        glDrawArrays(GL_TRIANGLES, 0, count)
    glBindVertexArray(0)

def load_texture_file(path):
    try:
        img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
        img_data = img.convert("RGBA").tobytes()
        width, height = img.size

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        # параметры фильтрации и повторения
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        return tex_id
    except Exception as e:
        print("[ERROR] Failed to load texture:", e)
        return 0

def print_controls():
    print("\n------ Controls -------- ")
    print("1 2 3 4 5 6 - смена цвета света")
    print("стрелки клавиатуры  - вращение камеры")
    print("+/- - регулировка яркости света")
    print("WASD+RF - перемещение источника света")
    print("[ ] - приближение/отдаление камеры")
    print("ё - включить/выключить освещение")
    print("0 - включить/выключить текстуру сферы")
    print("----------------------------\n")
