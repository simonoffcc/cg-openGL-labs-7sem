import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def draw_cone(radius, height, num_segments):
    # Draw the base of the cone
    glBegin(GL_LINE_LOOP)
    for i in range(num_segments):
        theta = 2.0 * math.pi * i / num_segments
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        glVertex3f(x, 0, z)
    glEnd()

    # Draw the sides of the cone
    glBegin(GL_LINES)
    for i in range(num_segments):
        theta = 2.0 * math.pi * i / num_segments
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        glVertex3f(0, height, 0)
        glVertex3f(x, 0, z)
    glEnd()

def draw_torus(inner_radius, outer_radius, num_sides, num_rings):
    for i in range(num_rings):
        glBegin(GL_LINE_LOOP)
        for j in range(num_sides):
            theta = 2.0 * math.pi * i / num_rings
            phi = 2.0 * math.pi * j / num_sides
            
            x = (outer_radius + inner_radius * math.cos(phi)) * math.cos(theta)
            y = (outer_radius + inner_radius * math.cos(phi)) * math.sin(theta)
            z = inner_radius * math.sin(phi)
            
            glVertex3f(x, y, z)
        glEnd()

    for j in range(num_sides):
        glBegin(GL_LINE_LOOP)
        for i in range(num_rings):
            theta = 2.0 * math.pi * i / num_rings
            phi = 2.0 * math.pi * j / num_sides
            
            x = (outer_radius + inner_radius * math.cos(phi)) * math.cos(theta)
            y = (outer_radius + inner_radius * math.cos(phi)) * math.sin(theta)
            z = inner_radius * math.sin(phi)

            glVertex3f(x, y, z)
        glEnd()

def draw_cylinder(radius, height, num_segments):
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_LINE)
    gluCylinder(quad, radius, radius, height, num_segments, 1)
    gluDeleteQuadric(quad)


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Two Wireframe Cones")

    gluPerspective(45, (display[0] / display[1]), 0.1, 1500.0)
    glTranslatef(0.0, -200.0, -1000)

    glRotatef(20, 1, 0, 0)

    # Cone parameters
    cone_radius = 150
    cone1_height = 250
    cone2_height = 500
    num_segments = 50

    start_time_anim = 0
    animation_delay = 0  # 2 seconds
    animation_duration = 3000  # 3 seconds

    scene_state = 1
    rotation_angle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    scene_state = 1
                elif event.key == pygame.K_2:
                    scene_state = 2
                    start_time_anim = pygame.time.get_ticks()
                elif event.key == pygame.K_3:
                    scene_state = 3
                elif event.key == pygame.K_4:
                    scene_state = 4


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glPushMatrix()
        glRotatef(rotation_angle, 0, 1, 0)

        if scene_state == 1:
            # Cone 1 (smaller)
            glPushMatrix()
            glRotatef(0, 1, 0, 0)
            glColor3f(1, 0, 0) # Red
            draw_cone(cone_radius, cone1_height, num_segments)
            glPopMatrix()

            # Cone 2 (larger)
            glColor3f(0, 0, 1) # Blue
            draw_cone(cone_radius, cone2_height, num_segments)

        elif scene_state == 2:
            current_time = pygame.time.get_ticks() - start_time_anim
        
            cone1_rotation_x = 0
            if current_time > animation_delay:
                elapsed_animation_time = current_time - animation_delay
                if elapsed_animation_time < animation_duration:
                    cone1_rotation_x = 90 * (elapsed_animation_time / animation_duration)
                else:
                    cone1_rotation_x = 90

            # Cone 1 (smaller) - animated rotation
            glPushMatrix()
            glRotatef(cone1_rotation_x, 1, 0, 0)
            glColor3f(1, 0, 0) # Red
            draw_cone(cone_radius, cone1_height, num_segments)
            glPopMatrix()

            # Cone 2 (larger) - not rotated
            glColor3f(0, 0, 1) # Blue
            draw_cone(cone_radius, cone2_height, num_segments)
        
        elif scene_state == 3:
            # Draw torus and cylinder, not intersecting
            glPushMatrix()
            glTranslatef(-200, 0, 0)
            glColor3f(0, 1, 0) # Green
            draw_torus(30, 80, 20, 20)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(200, 0, 0)
            glRotatef(90, 1, 0, 0)
            glColor3f(1, 1, 0) # Yellow
            draw_cylinder(60, 200, 20)
            glPopMatrix()

        elif scene_state == 4:
            # Draw torus and cylinder, intersecting
            glPushMatrix()
            glTranslatef(50, 0, 0)
            glColor3f(0, 1, 0) # Green
            draw_torus(30, 80, 20, 20)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(150, 0, 0)
            glRotatef(90, 1, 0, 0)
            glColor3f(1, 1, 0) # Yellow
            draw_cylinder(60, 200, 20)
            glPopMatrix()

        glPopMatrix()

        rotation_angle += 0.5
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
