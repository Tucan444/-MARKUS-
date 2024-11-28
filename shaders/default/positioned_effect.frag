#version 330

uniform sampler2D tex_source;
uniform sampler2D tex_dest;

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
    vec4 source_color = texture(tex_source, uv);
    vec4 dest_color = texture(tex_dest, uv);

    vec2 uvn = uv - vec2(0.5, 0.5);
    uvn.x *= aspect_ratio;

    float lerp_parameter = sdf(uvn);

    if (hill_of_peace == 1) {
        lerp_parameter = 1.0 - lerp_parameter;
    }

    color = mix(dest_color, source_color, lerp_parameter);
}