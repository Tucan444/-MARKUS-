#version 330

uniform sampler2D tex;
uniform int obscure_last;

uniform vec3 obscure_color;
uniform float obscure;
uniform int obscure_shape;
uniform float clear_distance;

uniform vec3 bar_color;
uniform float imprisonment;
uniform int bar_shape;
uniform float repeatance;

uniform float aspect_ratio;

in vec2 uv;
out vec4 color;

float shape_distance(vec2 position, int used_shape) {
    if (used_shape == 1) {
        return length(position);
    }

    if (used_shape == 2) {
        return max(abs(position.x), abs(position.y));
    }

    if (used_shape == 3) {
        return abs(position.x) + abs(position.y);
    }

    return 0;
}

void main() {
    vec4 sampled_color = texture(tex, uv);

    vec2 shape_uv = uv - vec2(0.5, 0.5);
    shape_uv.x *= aspect_ratio;

    float center_distance = shape_distance(shape_uv, obscure_shape);
    float obscure_enclosure = 0;

    float overrun = center_distance - (clear_distance * obscure);
    if (overrun > 0) {
        obscure_enclosure = 1;
    }

    vec2 bar_uv = vec2(uv.x * aspect_ratio, uv.y);
    bar_uv = fract(bar_uv * repeatance) - vec2(0.5, 0.5);
    float bar_distance = shape_distance(bar_uv, bar_shape);
    float imprisonment_enclosure = 0;

    if ((bar_distance < imprisonment) && (bar_shape != 0)) {
        imprisonment_enclosure = 1;
    }

    if (obscure_last == 1) {
        color = mix(sampled_color, vec4(bar_color, 1), imprisonment_enclosure);
        color = mix(color, vec4(obscure_color, 1), obscure_enclosure);
    } else {
        color = mix(sampled_color, vec4(obscure_color, 1), obscure_enclosure);
        color = mix(color, vec4(bar_color, 1), imprisonment_enclosure);
    }
}