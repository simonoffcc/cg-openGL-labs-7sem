import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

def create_checkerboard_texture():
    """ Creates a 256x256 checkerboard texture """
    size = 256
    checkerboard = np.zeros((size, size, 3), dtype=np.uint8)
    for i in range(size):
        for j in range(size):
            if (i // 32 % 2) == (j // 32 % 2):
                checkerboard[i, j] = [255, 255, 255] # White
            else:
                checkerboard[i, j] = [50, 50, 50]   # Dark Gray
    return checkerboard.tobytes(), size, size

def setup_texture(image_data, width, height):
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
    return texture_id

def draw_cone(radius, height, num_segments):
    glBegin(GL_TRIANGLE_FAN)
    # Apex
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, height, 0.0)
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * i / num_segments
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        # Normal for the side
        normal = (math.cos(theta), 0.5, math.sin(theta)) # Simplified normal calculation
        glNormal3fv(normal)
        glVertex3f(x, 0, z)
    glEnd()

    # Base
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * i / num_segments
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        glVertex3f(x, 0, z)
    glEnd()

def draw_torus(inner_radius, outer_radius, num_sides, num_rings):
    for i in range(num_rings):
        glBegin(GL_QUAD_STRIP)
        for j in range(num_sides + 1):
            for k in range(2): # Draw two points of the quad
                theta = 2.0 * math.pi * (i + k) / num_rings
                phi = 2.0 * math.pi * j / num_sides

                x = (outer_radius + inner_radius * math.cos(phi)) * math.cos(theta)
                y = (outer_radius + inner_radius * math.cos(phi)) * math.sin(theta)
                z = inner_radius * math.sin(phi)
                
                # Normal calculation
                normal_x = math.cos(phi) * math.cos(theta)
                normal_y = math.cos(phi) * math.sin(theta)
                normal_z = math.sin(phi)

                glNormal3f(normal_x, normal_y, normal_z)
                glVertex3f(x, y, z)
        glEnd()


def draw_cylinder(radius, height, num_segments):
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_FILL)
    gluQuadricTexture(quad, GL_TRUE)
    gluQuadricNormals(quad, GLU_SMOOTH)
    
    # Cylinder body
    gluCylinder(quad, radius, radius, height, num_segments, 1)
    
    # Top cap
    glPushMatrix()
    glTranslatef(0, 0, height)
    gluDisk(quad, 0, radius, num_segments, 1)
    glPopMatrix()

    # Bottom cap
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluDisk(quad, 0, radius, num_segments, 1)
    glPopMatrix()

    gluDeleteQuadric(quad)


def main():
    pygame.init()
    display = (1000, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Lab 2 - Materials, Lighting, and Textures")

    # --- OpenGL Setup ---
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # --- Light Setup ---
    light_pos = [0, 200, 0, 1]
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    
    light_colors = [
        [0.8, 0.8, 0.8, 1.0], # White
        [1.0, 0.0, 0.0, 1.0], # Red
        [0.0, 1.0, 0.0, 1.0], # Green
        [0.0, 0.0, 1.0, 1.0]  # Blue
    ]
    light_color_index = 0

    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_colors[light_color_index])
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_colors[light_color_index])
    
    # --- Texture Setup ---
    texture_data, width, height = create_checkerboard_texture()
    texture_id = setup_texture(texture_data, width, height)

    # --- Camera Setup ---
    gluPerspective(45, (display[0] / display[1]), 0.1, 1500.0)
    glTranslatef(0.0, -100.0, -1000)
    glRotatef(-30, 1, 0, 0)
    
    rotation_angle = 0
    light_sphere_colors = [[1,1,0], [1,0,0], [0,1,0], [0,0,1]]


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    light_color_index = (light_color_index + 1) % len(light_colors)
                    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_colors[light_color_index])
                    glLightfv(GL_LIGHT0, GL_SPECULAR, light_colors[light_color_index])


        # --- Keyboard controls for light ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            light_pos[0] -= 10
        if keys[pygame.K_RIGHT]:
            light_pos[0] += 10
        if keys[pygame.K_UP]:
            light_pos[1] += 10
        if keys[pygame.K_DOWN]:
            light_pos[1] -= 10
        if keys[pygame.K_PAGEUP]:
            light_pos[2] += 10
        if keys[pygame.K_PAGEDOWN]:
            light_pos[2] -= 10

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Update light position
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

        # Draw a sphere to represent the light source
        glPushMatrix()
        glTranslatef(light_pos[0], light_pos[1], light_pos[2])
        glColor3fv(light_sphere_colors[light_color_index])
        quad = gluNewQuadric()
        gluSphere(quad, 15, 32, 32)
        gluDeleteQuadric(quad)
        glPopMatrix()

        glPushMatrix()
        glRotatef(rotation_angle, 0, 1, 0)

        # --- Draw Objects ---
        
        # 1. Polished Torus (Shiny)
        glPushMatrix()
        glTranslatef(-300, 0, 0)
        specular = [1.0, 1.0, 1.0, 1.0]
        shininess = 128.0
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT, GL_SHININESS, shininess)
        glColor3f(0, 1, 0) # Green
        draw_torus(40, 100, 30, 30)
        # Reset material properties
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0,0,0,0])
        glMaterialf(GL_FRONT, GL_SHININESS, 0)
        glPopMatrix()

        # 2. Transparent Cone
        glPushMatrix()
        glTranslatef(0, -150, 0)
        glColor4f(0, 0, 1, 0.5) # Blue, 50% transparent
        draw_cone(150, 500, 50)
        glPopMatrix()

        # 3. Textured Cylinder (Matte)
        glPushMatrix()
        glTranslatef(300, -150, 0)
        glRotatef(-90, 1, 0, 0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1, 1, 1) # Use white color to not tint the texture
        draw_cylinder(80, 300, 30)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        glPopMatrix()

        rotation_angle += 0.3
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
