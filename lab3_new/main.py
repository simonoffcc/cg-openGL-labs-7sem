# File: main.py
import sys
import numpy as np
from pyglm import glm
from OpenGL.GL import *
from OpenGL.GLUT import *
from shaders import DEPTH_VS, DEPTH_FS, SCENE_VS, SCENE_FS, create_program
from utils import perspective, ortho, rotation_matrix
from utils import set_mat4_uniform, draw_vao_elements, load_texture_file, print_controls
from setup import generate_sphere_data, generate_cylinder_data, generate_floor_data, setup_object_vao_vbo, generate_torus_data  # <-- добавлен torus

class Scene:
    def __init__(self):
        # Параметры окна и камеры
        self.window_width = 1200
        self.window_height = 800
        self.cam_rot_x = 30.0
        self.cam_rot_y = -30.0
        self.cam_distance = 1000.0

        # Размеры и положение объектов
        self.SPHERE_RADIUS = 120.0
        self.cyl_height = 220.0
        self.cyl_radius = 70.0
        self.torus_center = np.array([300.0, 125.0, 0.0], dtype=np.float32)  # место куба
        self.sphere_center = np.array([-300.0, self.SPHERE_RADIUS, 0.0], dtype=np.float32)
        self.cyl_center   = np.array([0.0, self.cyl_height/2.0, 0.0], dtype=np.float32)

        # Параметры освещения
        self.light_enabled = True
        self.light_pos = [500.0, 500.0, 800.0, 1.0]
        self.light_intensity = 1.2
        self.light_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.light_ambient = [0.08, 0.08, 0.08, 1.0]

        # Цвета света (клавиши 1..5)
        self.LIGHT_COLOR_PRESETS = [
            (1,0,0,1),    # красный
            (0,0,1,1),    # синий
            (0,1,0,1),    # зеленый
            (1,1,0,1),    # желтый
            (1,0,1,1),     # пурпурный
            (1, 1, 1, 1)  # обычный белый свет
        ]

        # Текстура сферы
        self.sphere_texture_enabled = True
        self.sphere_texture_id = None

        # Shadow map
        self.SHADOW_WIDTH, self.SHADOW_HEIGHT = 2048, 2048
        self.depthMapFBO = None
        self.depthMap = None

        # Шейдерные программы
        self.shaderProgram = None
        self.depthShader = None

        # VAO/VBO/EBO
        self.sphere_VAO = self.sphere_VBO = self.sphere_EBO = None
        self.sphere_num_indices = 0
        self.cyl_VAO = self.cyl_VBO = self.cyl_EBO = None
        self.cyl_num_indices = 0
        self.floor_VAO = self.floor_VBO = self.floor_EBO = None
        self.floor_num_indices = 0
        self.torus_VAO = self.torus_VBO = self.torus_EBO = None
        self.torus_num_indices = 0

    def init(self):
        glClearColor(0.6,0.6,0.6,1.0)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        # Шейдеры
        self.depthShader = create_program(DEPTH_VS, DEPTH_FS)
        self.shaderProgram = create_program(SCENE_VS, SCENE_FS)
        print("[INFO] Shaders compiled.")

        # FBO и текстура для теней
        self.depthMapFBO = glGenFramebuffers(1)
        self.depthMap = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24,
                     self.SHADOW_WIDTH, self.SHADOW_HEIGHT, 0,
                     GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        border = (GLfloat*4)(1.0,1.0,1.0,1.0)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthMap, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("[ERROR] Depth FBO incomplete")
        else:
            print("[INFO] Depth FBO OK")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Геометрия
        # Сфера
        sphere_verts, sphere_inds, sphere_count = generate_sphere_data(self.SPHERE_RADIUS, 64, 48)
        self.sphere_VAO, self.sphere_VBO, self.sphere_EBO = setup_object_vao_vbo(sphere_verts, sphere_inds)
        self.sphere_num_indices = sphere_count
        # Цилиндр
        cyl_verts, cyl_inds, cyl_count = generate_cylinder_data(self.cyl_radius, self.cyl_height, 64)
        self.cyl_VAO, self.cyl_VBO, self.cyl_EBO = setup_object_vao_vbo(cyl_verts, cyl_inds)
        self.cyl_num_indices = cyl_count
        # Тор
        torus_verts, torus_inds, torus_count = generate_torus_data(120, 40, 48, 32)
        self.torus_VAO, self.torus_VBO, self.torus_EBO = setup_object_vao_vbo(torus_verts, torus_inds)
        self.torus_num_indices = torus_count
        # Пол
        floor_verts, floor_inds, floor_count = generate_floor_data(2000, 10)
        self.floor_VAO, self.floor_VBO, self.floor_EBO = setup_object_vao_vbo(floor_verts, floor_inds)
        self.floor_num_indices = floor_count

        # Текстура сферы
        self.sphere_texture_id = load_texture_file("sphere_texture.jpg")

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        print_controls()

    def compute_light_space_matrix(self):
        left, right, bottom, top = -1200.0, 1200.0, -1200.0, 1200.0
        near, far = 1.0, 3000.0
        lightProj = ortho(left, right, bottom, top, near, far)
        eye = glm.vec3(*self.light_pos[:3])
        center = glm.vec3(0.0, 0.0, 0.0)
        up = glm.vec3(0.0, 1.0, 0.0)
        lightView = glm.lookAt(eye, center, up)
        return lightProj * lightView

    def render_depth(self, prog):
        # Пол
        set_mat4_uniform(prog, "model", glm.mat4(1.0))
        draw_vao_elements(self.floor_VAO, self.floor_EBO, self.floor_num_indices)
        # Сфера
        set_mat4_uniform(prog, "model", glm.translate(glm.mat4(1.0), glm.vec3(*self.sphere_center)))
        draw_vao_elements(self.sphere_VAO, self.sphere_EBO, self.sphere_num_indices)
        # Цилиндр
        set_mat4_uniform(prog, "model", glm.translate(glm.mat4(1.0), glm.vec3(*self.cyl_center)))
        draw_vao_elements(self.cyl_VAO, self.cyl_EBO, self.cyl_num_indices)
        # Тор
        set_mat4_uniform(prog, "model", glm.translate(glm.mat4(1.0), glm.vec3(*self.torus_center)))
        draw_vao_elements(self.torus_VAO, self.torus_EBO, self.torus_num_indices)

    def render_scene(self, prog, view_mat, proj_mat, lightSpace):
        set_mat4_uniform(prog, "view", view_mat)
        set_mat4_uniform(prog, "projection", proj_mat)
        set_mat4_uniform(prog, "lightSpaceMatrix", lightSpace)

        rot = rotation_matrix(self.cam_rot_x, self.cam_rot_y)
        cam_pos = np.dot(rot, np.array([0.0, 400.0, self.cam_distance, 1.0], dtype=np.float32))[:3]
        glUniform3fv(glGetUniformLocation(prog, "viewPos"), 1, cam_pos)

        eff_intensity = self.light_intensity if self.light_enabled else 0.0
        eff_color = self.light_diffuse[:3] if self.light_enabled else [0.0, 0.0, 0.0]
        glUniform3fv(glGetUniformLocation(prog, "lightPos"), 1, self.light_pos[:3])
        glUniform3fv(glGetUniformLocation(prog, "lightColor"), 1, eff_color)
        glUniform1f(glGetUniformLocation(prog, "lightIntensity"), eff_intensity)
        glUniform3fv(glGetUniformLocation(prog, "lightAmbient"), 1, self.light_ambient[:3])

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glUniform1i(glGetUniformLocation(prog, "shadowMap"), 1)

        # --- Пол ---
        model = glm.mat4(1.0)
        set_mat4_uniform(prog, "model", model)
        glUniform3fv(glGetUniformLocation(prog, "materialDiffuse"), 1, [0.92, 0.92, 0.90])
        glUniform3fv(glGetUniformLocation(prog, "materialSpecular"), 1, [0.02, 0.02, 0.02])
        glUniform1f(glGetUniformLocation(prog, "materialShininess"), 1.0)
        glUniform1i(glGetUniformLocation(prog, "useTexture"), 0)
        glUniform1i(glGetUniformLocation(prog, "isTransparent"), 0)
        draw_vao_elements(self.floor_VAO, self.floor_EBO, self.floor_num_indices)

        # --- Сфера ---
        set_mat4_uniform(prog, "model", glm.translate(glm.mat4(1.0), glm.vec3(*self.sphere_center)))
        glUniform3fv(glGetUniformLocation(prog, "materialSpecular"), 1, [0.05, 0.05, 0.05])
        glUniform1f(glGetUniformLocation(prog, "materialShininess"), 2.0)
        if self.sphere_texture_enabled:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.sphere_texture_id)
            glUniform1i(glGetUniformLocation(prog, "useTexture"), 1)
        else:
            glUniform1i(glGetUniformLocation(prog, "useTexture"), 0)
        glUniform1i(glGetUniformLocation(prog, "isTransparent"), 0)
        draw_vao_elements(self.sphere_VAO, self.sphere_EBO, self.sphere_num_indices)

        # --- Тор (красный, глянцевый) ---
        set_mat4_uniform(prog, "model", glm.translate(glm.mat4(1.0), glm.vec3(*self.torus_center)))
        glUniform3fv(glGetUniformLocation(prog, "materialDiffuse"), 1, [1.0, 0.0, 0.0])
        glUniform3fv(glGetUniformLocation(prog, "materialSpecular"), 1, [0.6, 0.6, 0.6])
        glUniform1f(glGetUniformLocation(prog, "materialShininess"), 64.0)
        glUniform1i(glGetUniformLocation(prog, "useTexture"), 0)
        glUniform1i(glGetUniformLocation(prog, "isTransparent"), 0)
        draw_vao_elements(self.torus_VAO, self.torus_EBO, self.torus_num_indices)

        # --- Цилиндр (синий, полупрозрачный) ---
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        set_mat4_uniform(prog, "model", glm.translate(glm.mat4(1.0), glm.vec3(*self.cyl_center)))
        glUniform3fv(glGetUniformLocation(prog, "materialDiffuse"), 1, [0.0, 0.5, 1.0])
        glUniform3fv(glGetUniformLocation(prog, "materialSpecular"), 1, [0.1, 0.1, 0.1])
        glUniform1f(glGetUniformLocation(prog, "materialShininess"), 4.0)
        glUniform1i(glGetUniformLocation(prog, "useTexture"), 0)
        glUniform1i(glGetUniformLocation(prog, "isTransparent"), 1)
        draw_vao_elements(self.cyl_VAO, self.cyl_EBO, self.cyl_num_indices)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
    # Остальные callback остаются прежними...


    def display(self):
        lightSpace = self.compute_light_space_matrix()
        # --- Теневая карта ---
        glViewport(0, 0, self.SHADOW_WIDTH, self.SHADOW_HEIGHT)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glClear(GL_DEPTH_BUFFER_BIT)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(8.0, 32.0)

        glUseProgram(self.depthShader)
        set_mat4_uniform(self.depthShader, "lightSpaceMatrix", lightSpace)
        self.render_depth(self.depthShader)
        glUseProgram(0)

        glDisable(GL_POLYGON_OFFSET_FILL)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # --- Основная сцена ---
        glViewport(0, 0, self.window_width, self.window_height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shaderProgram)

        eye = glm.vec3(0.0, 400.0, self.cam_distance)
        center = glm.vec3(0.0, 0.0, 0.0)
        up = glm.vec3(0.0, 1.0, 0.0)
        view = glm.lookAt(eye, center, up) * rotation_matrix(self.cam_rot_x, self.cam_rot_y)
        proj = perspective(50.0, self.window_width / float(self.window_height), 1.0, 5000.0)
        self.render_scene(self.shaderProgram, view, proj, lightSpace)

        glUseProgram(0)
        glutSwapBuffers()

    def reshape(self, w, h):
        self.window_width = w
        self.window_height = h
        glViewport(0, 0, w, h)

    def keyboard(self,key,x,y):
        k = key.decode() if isinstance(key, bytes) else key
        if k == '0':
            self.sphere_texture_enabled = not self.sphere_texture_enabled
        elif k in '123456':
            self.light_diffuse = self.LIGHT_COLOR_PRESETS[int(k)-1]
        elif k in ('=', '+'):
            self.light_intensity = min(5.0, self.light_intensity+0.1)
        elif k == '-':
            self.light_intensity = max(0.0, self.light_intensity-0.1)
        elif k in ('ё','`'):
            self.light_enabled = not self.light_enabled
        elif k == '[':
            self.cam_distance += 50.0
        elif k == ']':
            self.cam_distance = max(200.0,self.cam_distance-50.0)
        glutPostRedisplay()

    def special(self, key, x, y):
        if key == GLUT_KEY_LEFT:
            self.cam_rot_y -= 5
        elif key == GLUT_KEY_RIGHT:
            self.cam_rot_y += 5
        elif key == GLUT_KEY_UP:
            self.cam_rot_x -= 5
        elif key == GLUT_KEY_DOWN:
            self.cam_rot_x += 5
        glutPostRedisplay()

    def keyboard_motion(self, key, x, y):
        k = key.decode() if isinstance(key, bytes) else key
        step = 20.0
        if k.lower() == 'w':
            self.light_pos[2] -= step
        elif k.lower() == 's':
            self.light_pos[2] += step
        elif k.lower() == 'a':
            self.light_pos[0] -= step
        elif k.lower() == 'd':
            self.light_pos[0] += step
        elif k.lower() == 'r':
            self.light_pos[1] += step
        elif k.lower() == 'f':
            self.light_pos[1] -= step
        glutPostRedisplay()

def main():
    global scene
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    scene = Scene()
    glutInitWindowSize(scene.window_width, scene.window_height)
    glutCreateWindow(b"Lab3")
    scene.init()
    glutDisplayFunc(scene.display)
    glutReshapeFunc(scene.reshape)
    glutKeyboardFunc(lambda k, x, y: (scene.keyboard(k, x, y), scene.keyboard_motion(k, x, y)))
    glutSpecialFunc(scene.special)
    glutMainLoop()

if __name__ == "__main__":
    main()
