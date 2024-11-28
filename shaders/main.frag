#version 330

uniform sampler2D tex;
uniform vec2 position;
uniform float alpha;

in vec2 uv;
out vec4 color;

void main() {
    vec2 new_uv = uv - position;

    // uv cutting
    if ((min(new_uv.x, new_uv.y) < 0) || (max(new_uv.x, new_uv.y) > 1)) {
        color = vec4(0, 0, 0, 0);
        return;
    }

    vec4 sampled_color = texture(tex, new_uv);
    color = vec4(sampled_color.xyz, alpha);
}