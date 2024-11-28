#version 330

uniform sampler2D tex;
uniform sampler2D kernel;
uniform vec2 pixel_size;
uniform vec2 kernel_pixel_size;

uniform ivec2 kernel_x_range;
uniform ivec2 kernel_y_range;
uniform float color_range;
uniform vec3 color_range_zero;

in vec2 uv;
out vec4 color;

void main() {
    vec4 accumulator = vec4(0, 0, 0, 0);

    for (int x = kernel_x_range.x; x < kernel_x_range.y; x++) {
        for (int y = kernel_y_range.x; y < kernel_y_range.y; y++) {
            vec2 xy = vec2(x, y);
            vec4 image_color = texture(tex, uv + (xy * pixel_size));

            xy -= vec2(kernel_x_range.x, kernel_y_range.x);
            vec4 kernel_color = texture(kernel, xy * kernel_pixel_size);
            kernel_color.rgb *= color_range;
            kernel_color.rgb -= color_range_zero;

            accumulator += image_color * kernel_color;
        }
    }

    color = vec4(accumulator.rgb, texture(tex, uv).a);
}