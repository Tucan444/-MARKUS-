#version 330

uniform sampler2D tex;
uniform vec4 add;
uniform vec4 intensity;
uniform float invert_color;
uniform float grayscale;
uniform float dynamic_range;
uniform float dynamic_range_inverse;
uniform float gamma;
uniform float hue_shift;
uniform float saturation_change;

in vec2 uv;
out vec4 color;

vec3 rgbToHsv(vec4 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsvToRgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

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

    if ((hue_shift != 0) || (saturation_change != 0)) {
        vec3 hvs = rgbToHsv(color);

        hvs.x += hue_shift;
        hvs.x = fract(hvs.x);

        if (saturation_change < 0) {
            hvs.y *= saturation_change + 1.0;
        } else if (saturation_change > 0) {
            hvs.y = mix(hvs.y, 1.0, saturation_change);
        }

        color.xyz = hsvToRgb(hvs);
    }
}
