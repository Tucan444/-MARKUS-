#version 330

uniform sampler2D tex;
uniform float threshold;

in vec2 uv;
out vec4 color;

void main() {
    vec4 sampled_color = texture(tex, uv);
    float luminance = (0.299f * sampled_color.r) + (0.587f * sampled_color.g) + (0.114 * sampled_color.b);

    if (luminance < threshold) {
        color = vec4(0, 0, 0, 1);
    } else {
        color = sampled_color;
    }
}