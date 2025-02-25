#version 330

uniform sampler2D tex_light;
uniform vec4 light_color;

uniform vec2 center;
uniform vec2 size;
uniform float radius;
uniform float falloff;
uniform float falloff_inv;
uniform float falloff_speed;
uniform int hill_of_peace;

uniform float aspect_ratio;

in vec2 uv;
out vec4 color;

float sdf(vec2 v) {
    v -= center;
    v = abs(v);
    v -= size;
    v = max(vec2(0.0, 0.0), v);

    float dist = max(0.0, length(v) - radius);

    if (dist == 0.0) {
        return 0.0;
    } else if (falloff == 0) {
        return 1.0;
    }

    return pow(min(1.0, dist * falloff_inv), falloff_speed);
}

void main() {
    vec4 light_tex_color = texture(tex_light, uv);

    vec2 uvn = uv - vec2(0.5, 0.5);
    uvn.x *= aspect_ratio;

    float light = 1.0 - sdf(uvn);

    if (hill_of_peace == 1) {
        light = 1.0 - light;
    }

    vec4 final_color = light_tex_color + (light_color*light);
    color = vec4(final_color.rgb, 1.0);
}