#version 330

uniform sampler2D tex;
uniform vec4 add;
uniform vec4 intensity;
uniform float invert_color;
uniform float grayscale;
uniform float dynamic_range;
uniform float dynamic_range_inverse;
uniform float gamma;
// suggestion hsv transform, maybe in texture calculator as well

in vec2 uv;
out vec4 color;

void main() {
    vec4 sampled_color = texture(tex, uv);

    color = (sampled_color * intensity) + add;

    if (invert_color != 0) {
        vec4 inverted_color = vec4(
            1.0 - color.r,
            1.0 - color.g,
            1.0 - color.b,
            color.a
        );

        color = mix(color, inverted_color, invert_color);
    }

    if (grayscale != 0) {
        float luminance = (0.299f * color.r) + (0.587f * color.g) + (0.114 * color.b);
        vec4 grayscale_color = vec4(luminance, luminance, luminance, color.a);

        color = mix(color, grayscale_color, grayscale);
    }

    if (dynamic_range != 0) {
        color.rgb = floor(color.rgb * dynamic_range_inverse) * dynamic_range;
    }

    if (gamma != 1) {
        color.rgb = pow(color.rgb, gamma.xxx);
    }
}