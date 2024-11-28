#version 330

uniform sampler2D tex;
uniform float time;

uniform float x_sine;
uniform float x_sine_frequency;
uniform float y_sine;
uniform float y_sine_frequency;

uniform vec2 twist_position;
uniform float twist;
uniform float twist_falloff;

uniform float aspect_ratio;
uniform float aspect_ratio_inverse;

in vec2 uv;
out vec4 color;

void main() {
    vec2 new_uv = uv - vec2(0.5, 0.5);
    new_uv.x *= aspect_ratio;
    vec2 new_twist_position = twist_position;
    new_twist_position.x *= aspect_ratio;
    vec2 new_mid = vec2(0.5 * aspect_ratio, 0.5);
    vec2 uv_copy = new_uv.xy;

    if (twist != 0) {
        vec2 twist_pos = new_uv - new_twist_position + new_mid;
        float dist = length(twist_pos);
        float angle = atan(twist_pos.y, twist_pos.x);

        angle += twist * (1.0 / pow(1.0 + length(twist_pos), twist_falloff));
        twist_pos = dist * vec2(cos(angle), sin(angle));
        new_uv = twist_pos + new_twist_position - new_mid;
    }

    if (x_sine > 0) {
        new_uv.x += sin(time + (x_sine_frequency * uv_copy.y)) * x_sine;
    }

    if (y_sine > 0) {
        new_uv.y += sin(time + (y_sine_frequency * uv_copy.x)) * y_sine;
    }

    new_uv.x *= aspect_ratio_inverse;
    new_uv += vec2(0.5, 0.5);

    color = texture(tex, new_uv);
}