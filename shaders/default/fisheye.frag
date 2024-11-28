#version 330

uniform sampler2D tex;

uniform float zoom;
uniform float fisheye_distance;
uniform float aspect_ratio;
uniform float aspect_ratio_inverse;

in vec2 uv;
out vec4 color;

void main() {
    vec2 new_uv = uv - vec2(0.5, 0.5);
    new_uv.x *= aspect_ratio;

    new_uv *= zoom;

    if (fisheye_distance > 0) {
        float dist = length(vec3(new_uv, fisheye_distance));
        new_uv.y *= dist / fisheye_distance;
    } else if (fisheye_distance < 0) {
        float dist = length(vec3(new_uv, fisheye_distance));
        new_uv.y *= fisheye_distance / dist;
    }

    new_uv.x *= aspect_ratio_inverse;
    new_uv += vec2(0.5, 0.5);

    color = texture(tex, new_uv);
}