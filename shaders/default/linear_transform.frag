#version 330

uniform sampler2D tex;
uniform mat2x2 transform;
uniform vec2 offset;
uniform float aspect_ratio;
uniform float aspect_ratio_inverse;

in vec2 uv;
out vec4 color;

void main() {
    vec2 new_uv = uv - vec2(0.5, 0.5);
    new_uv.x *= aspect_ratio;
    new_uv = mul(transform, new_uv);
    new_uv.x *= aspect_ratio_inverse;
    new_uv += offset + vec2(0.5, 0.5);

    color = texture(tex, new_uv);
}