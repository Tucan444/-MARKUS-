#version 330

in vec2 position;
in vec2 texcoord;
out vec2 uv;

void main() {
    uv = texcoord;
    gl_Position = vec4(position.xy, 0, 1);
}