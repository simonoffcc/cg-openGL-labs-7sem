#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;
in vec4 FragPosLightSpace;

uniform sampler2D diffuseTexture;
uniform sampler2D shadowMap;

uniform vec3 lightPos;
uniform vec3 viewPos;

uniform bool isTextured;
uniform bool isPolished;
uniform bool isTransparent;

float ShadowCalculation(vec4 fragPosLightSpace)
{
    // Выполняем перспективное деление
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    // Преобразуем в диапазон [0,1]
    projCoords = projCoords * 0.5 + 0.5;

    // Получаем ближайшую глубину из карты теней
    float closestDepth = texture(shadowMap, projCoords.xy).r; 
    // Получаем текущую глубину
    float currentDepth = projCoords.z;

    // Проверяем, не выходит ли фрагмент за пределы карты теней
    if(projCoords.z > 1.0)
        return 0.0;

    // ИЗМЕНЕНО: Используем более простое и предсказуемое смещение.
    // Это самый частый фикс для теней, пропадающих на плоскости.
    float bias = 0.005;
    // Старый код закомментирован:
    // float bias = max(0.005 * (1.0 - dot(Normal, normalize(lightPos - FragPos))), 0.0005);

    // PCF для сглаживания теней
    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
    for(int x = -1; x <= 1; ++x)
    {
        for(int y = -1; y <= 1; ++y)
        {
            float pcfDepth = texture(shadowMap, projCoords.xy + vec2(x, y) * texelSize).r; 
            shadow += currentDepth - bias > pcfDepth ? 1.0 : 0.0;        
        }    
    }
    shadow /= 9.0;
    
    return shadow;
}

void main()
{
    vec3 color = vec3(0.8, 0.8, 0.8); // Базовый цвет для нетекстурированных объектов
    if (isTextured) {
        color = texture(diffuseTexture, TexCoords).rgb;
    }
    
    vec3 normal = normalize(Normal);
    vec3 lightColor = vec3(1.0);

    // Ambient (окружающее освещение)
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * lightColor;
  
    // Diffuse (рассеянное освещение)
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // Specular (бликовое освещение)
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float shininess = 32.0;
    if (isPolished) {
        shininess = 128.0; // Более яркий и концентрированный блик для полировки
    }
    float spec = pow(max(dot(normal, halfwayDir), 0.0), shininess);
    vec3 specular = spec * lightColor;
    
    // Рассчитываем тень
    float shadow = ShadowCalculation(FragPosLightSpace);
    
    // Собираем финальное освещение
    vec3 lighting = (ambient + (1.0 - shadow) * (diffuse + specular)) * color;

    float alpha = 1.0;
    if (isTransparent) {
        alpha = 0.7; // Устанавливаем полупрозрачность
        lighting = ambient * color; // Прозрачные объекты не получают диффузного/бликового света для простоты
    }
    
    FragColor = vec4(lighting, alpha);
}
