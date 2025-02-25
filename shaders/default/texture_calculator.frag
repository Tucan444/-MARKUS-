#version 330

uniform sampler2D tex_a;
uniform sampler2D tex_b;

uniform float a_amount;
uniform float b_amount;
uniform int operation;

in vec2 uv;
out vec4 color;
// on_need_basis maybe hue/saturation maps

void main() {
    vec3 a_color = (texture(tex_a, uv) * a_amount).rgb;
    vec3 b_color = (texture(tex_b, uv) * b_amount).rgb;

    vec3 result = vec3(1, 0, 1);

    if (operation == 0) {
        result = a_color + b_color;
    } else if (operation == 1) {
        result = a_color - b_color;
    } else if (operation == 2) {
        result = a_color * b_color;
    } else if (operation == 3) {
        result = a_color / b_color;
    } else if ((operation >= 4) && (operation <= 7)) {
        vec2 red_vec = vec2(a_color.r, b_color.r);
        vec2 green_vec = vec2(a_color.g, b_color.g);
        vec2 blue_vec = vec2(a_color.b, b_color.b);

        if (operation == 4) {
            result = vec3(length(red_vec), length(green_vec), length(blue_vec));
        } else if (operation == 5) {
            result = vec3(
                    abs(red_vec.x) + abs(red_vec.y),
                    abs(green_vec.x) + abs(green_vec.y),
                    abs(blue_vec.x) + abs(blue_vec.y)
            );
        } else if (operation == 6) {
            result = vec3(
            max(abs(red_vec.x), abs(red_vec.y)),
            max(abs(green_vec.x), abs(green_vec.y)),
            max(abs(blue_vec.x), abs(blue_vec.y)));
        } else if (operation == 7) {
            result = vec3(
                atan(red_vec.y, red_vec.x),
                atan(green_vec.y, green_vec.x),
                atan(blue_vec.y, blue_vec.x)
            ) * 0.1591549; // == 1. / tau
            result += vec3(0.5, 0.5, 0.5);
        }
    }

    color = vec4(result, 1);
}