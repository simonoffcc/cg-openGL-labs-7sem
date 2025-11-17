# File: shaders.py
from OpenGL.GL import *             # импорт OpenGL функций

# Вершинный шейдер (формирует координаты для теневой карты)
DEPTH_VS = """\
#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 lightSpaceMatrix;
uniform mat4 model;
void main() {
    gl_Position = lightSpaceMatrix * model * vec4(aPos, 1.0);
}
"""  # Vertex shader

# Фрагментный шейдер (цвет не нужен, поэтому пустой)
DEPTH_FS = """\
#version 330 core
void main() { }
"""  # Fragment shader

# Вершинный шейдер сцены (с учетом освещения и теней)
SCENE_VS = """\
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoords;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoords;
out vec4 LightSpacePos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 lightSpaceMatrix;

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));             // Позиция фрагмента в мировых координатах
    Normal = mat3(transpose(inverse(model))) * aNormal;  // Трансформированная нормаль
    TexCoords = aTexCoords;                               // Текстурные координаты
    LightSpacePos = lightSpaceMatrix * model * vec4(aPos, 1.0); // Координаты для тени
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""  # Vertex shader source for the scene

# Фрагментный шейдер сцены (расчет света, тени и материала)
SCENE_FS = """\
#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;
in vec4 LightSpacePos;

uniform sampler2D diffuseTexture;
uniform sampler2D shadowMap;

uniform vec3 viewPos;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform float lightIntensity;
uniform vec3 lightAmbient;

uniform float materialShininess;
uniform vec3 materialDiffuse;
uniform vec3 materialSpecular;
uniform bool useTexture;
uniform bool isTransparent;

// Функция расчета тени
float calculateShadow() {
    vec3 projCoords = LightSpacePos.xyz / LightSpacePos.w;
    projCoords = projCoords * 0.5 + 0.5;
    if (projCoords.x < 0.0 || projCoords.x > 1.0 ||
        projCoords.y < 0.0 || projCoords.y > 1.0) {
        return 0.0; // фрагмент вне теневого квадрата
    }
    float currentDepth = projCoords.z;
    float bias = max(0.12 * (1.0 - dot(normalize(Normal), normalize(lightPos - FragPos))), 0.03);
    vec2 texelSize = 1.0 / vec2(textureSize(shadowMap, 0));
    float shadow = 0.0;
    for(int x = -1; x <= 1; ++x)
        for(int y = -1; y <= 1; ++y) {
            float pcfDepth = texture(shadowMap, projCoords.xy + vec2(x,y) * texelSize).r;
            shadow += currentDepth - bias > pcfDepth ? 1.0 : 0.0;
        }
    shadow /= 9.0;
    return clamp(shadow, 0.0, 1.0);
}

void main() {
    vec3 ambient = lightAmbient * materialDiffuse; // фоновое освещение

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = lightColor * diff * materialDiffuse * lightIntensity;

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = 0.0;
    if (diff > 0.0)
        spec = pow(max(dot(viewDir, reflectDir), 0.0), materialShininess);
    vec3 specular = lightColor * spec * materialSpecular * lightIntensity;

    float shadow = calculateShadow(); // вычисляем тень
    vec3 lighting = ambient + (1.0 - shadow) * (diffuse + specular);

    vec4 texColor = vec4(materialDiffuse, 1.0);
    if (useTexture)
        texColor = texture(diffuseTexture, TexCoords);

    vec4 color = vec4(lighting, 1.0) * texColor;
    if (isTransparent)
        FragColor = vec4(color.rgb, 0.7);
    else
        FragColor = color;
}
"""  # Fragment shader source for the scene

# Компиляция шейдера из исходного кода
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)            # передаем исходный код
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode())  # выдаем ошибку компиляции
    return shader  # возвращаем ID шейдера

# Создание программы шейдеров из вершинного и фрагментного шейдеров
def create_program(vs_source, fs_source):
    vertex_shader = compile_shader(vs_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fs_source, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program).decode())  # ошибка линковки
    glDeleteShader(vertex_shader)     # удаляем вершинный шейдер (не нужен после линковки)
    glDeleteShader(fragment_shader)   # удаляем фрагментный шейдер
    return program  # возвращаем ID шейдерной программы
