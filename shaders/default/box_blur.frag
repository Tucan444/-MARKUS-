#version 330

uniform sampler2D tex;
uniform int blur_size;
uniform vec2 pixel_size;

uniform float divider;
uniform int x_pass;
uniform int y_pass;

in vec2 uv;
out vec4 color;

void main() {
    vec4 accum_color = vec4(0, 0, 0, 0);

    if (x_pass == 1) {
        for (int i = -blur_size; i <= blur_size; i++) {
            accum_color += texture(tex, vec2(uv.x + pixel_size.x*i, uv.y));
        }
    } else if (y_pass == 1) {
        for (int j = -blur_size; j <= blur_size; j++) {
            accum_color += texture(tex, vec2(uv.x, uv.y + pixel_size.y*j));
        }
    }

    color = accum_color * divider;
}