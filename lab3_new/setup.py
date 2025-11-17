import math
import numpy as np
import trimesh
from OpenGL.GL import *

def generate_cone_data(radius, height, slices):
    cone = trimesh.creation.cone(radius=radius, height=height, sections=slices)
    verts = cone.vertices
    normals = cone.vertex_normals
    inds = cone.faces.flatten()

    uvs = np.zeros((verts.shape[0], 2), dtype=np.float32)
    for i, (x, y, z) in enumerate(verts):
        theta = math.atan2(z, x)
        u = (theta + math.pi) / (2 * math.pi)
        v = (y + height / 2) / height
        uvs[i] = [u, v]

    verts_with_data = np.hstack([verts, normals, uvs]).astype(np.float32)
    return verts_with_data, np.array(inds, dtype=np.uint32), len(inds)

def generate_cylinder_data(radius, height, slices):
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=slices)
    verts = cyl.vertices
    normals = cyl.vertex_normals
    inds = cyl.faces.flatten()

    uvs = np.zeros((verts.shape[0], 2), dtype=np.float32)
    for i, (x, y, z) in enumerate(verts):
        theta = math.atan2(z, x)
        u = (theta + math.pi) / (2 * math.pi)
        v = (y + height / 2) / height
        uvs[i] = [u, v]

    verts_with_data = np.hstack([verts, normals, uvs]).astype(np.float32)
    return verts_with_data, np.array(inds, dtype=np.uint32), len(inds)

def generate_floor_data(size, repeat_tex=10):
    half = size / 2.0
    verts = np.array([
        -half, 0.0, -half, 0.0, 1.0, 0.0, 0.0, repeat_tex,
        half, 0.0, -half, 0.0, 1.0, 0.0, repeat_tex, repeat_tex,
        half, 0.0, half, 0.0, 1.0, 0.0, repeat_tex, 0.0,
        -half, 0.0, half, 0.0, 1.0, 0.0, 0.0, 0.0
    ], dtype=np.float32)
    inds = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
    return verts, inds, len(inds)

def generate_torus_data(radius_major, radius_minor, radial_segments, tubular_segments):
    vertices = []
    normals = []
    uvs = []
    indices = []

    for i in range(radial_segments):
        theta = (i / radial_segments) * 2 * math.pi
        next_theta = ((i + 1) % radial_segments) / radial_segments * 2 * math.pi

        for j in range(tubular_segments):
            phi = (j / tubular_segments) * 2 * math.pi
            next_phi = ((j + 1) % tubular_segments) / tubular_segments * 2 * math.pi

            def point(a, b):
                x = (radius_major + radius_minor * math.cos(b)) * math.cos(a)
                y = radius_minor * math.sin(b)
                z = (radius_major + radius_minor * math.cos(b)) * math.sin(a)
                return np.array([x, y, z], dtype=np.float32)

            p1 = point(theta, phi)
            p2 = point(theta, next_phi)
            p3 = point(next_theta, phi)
            p4 = point(next_theta, next_phi)

            def normal(a, b):
                nx = math.cos(a) * math.cos(b)
                ny = math.sin(b)
                nz = math.sin(a) * math.cos(b)
                return np.array([nx, ny, nz], dtype=np.float32)

            n1 = normal(theta, phi)
            n2 = normal(theta, next_phi)
            n3 = normal(next_theta, phi)
            n4 = normal(next_theta, next_phi)

            u1, v1 = i / radial_segments, j / tubular_segments
            u2, v2 = i / radial_segments, (j + 1) / tubular_segments
            u3, v3 = (i + 1) / radial_segments, j / tubular_segments
            u4, v4 = (i + 1) / radial_segments, (j + 1) / tubular_segments

            idx = len(vertices) // 3
            vertices.extend(p1); normals.extend(n1); uvs.extend([u1, v1])
            vertices.extend(p2); normals.extend(n2); uvs.extend([u2, v2])
            vertices.extend(p3); normals.extend(n3); uvs.extend([u3, v3])
            vertices.extend(p4); normals.extend(n4); uvs.extend([u4, v4])

            indices += [
                idx, idx + 1, idx + 2,
                idx + 2, idx + 1, idx + 3
            ]

    vertices = np.array(vertices, dtype=np.float32).reshape(-1, 3)
    normals = np.array(normals, dtype=np.float32).reshape(-1, 3)
    uvs = np.array(uvs, dtype=np.float32).reshape(-1, 2)

    verts_with_data = np.hstack([vertices, normals, uvs]).astype(np.float32)
    indices = np.array(indices, dtype=np.uint32)

    return verts_with_data, indices, len(indices)

def setup_object_vao_vbo(vertices_data, indices_data=None):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices_data.nbytes, vertices_data, GL_STATIC_DRAW)

    ebo = None
    if indices_data is not None:
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_data.nbytes, indices_data, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    return vao, vbo, ebo
