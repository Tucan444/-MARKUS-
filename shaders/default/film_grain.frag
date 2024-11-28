#version 330

uniform sampler2D tex;
uniform vec3 grain_color;
uniform float grain_amount;
uniform float time;

in vec2 uv;
out vec4 color;

void main() {
    vec4 sampled_color = texture(tex, uv);

    float grain = fract(sin(dot(uv, vec2(12.9898, 78.233)) + time) * 43758.5453);
    grain = (grain - 0.5) * 2.0;
    grain *= grain_amount;

    sampled_color.rgb += grain.xxx * grain_color;

    color = sampled_color;
}