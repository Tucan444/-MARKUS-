#version 330

uniform sampler2D tex;
uniform vec3 vignette_color;
uniform float power;

in vec2 uv;
out vec4 color;

void main() {
    vec4 sampled_color = texture(tex, uv);

    vec2 vig_uv = uv * (1.0 - uv);
    float vig = vig_uv.x * vig_uv.y * 15.0;
    vig = pow(vig, power);

    color = mix(vec4(vignette_color, 1), sampled_color, vig);
}