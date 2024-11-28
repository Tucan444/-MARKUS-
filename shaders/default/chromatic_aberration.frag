#version 330

uniform sampler2D tex;
uniform vec2 focal_point;
uniform float red_offset;
uniform float green_offset;
uniform float blue_offset;

in vec2 uv;
out vec4 color;

void main() {
    float alpha = texture(tex, uv).a;
    vec2 direction = uv - focal_point;

    vec2 red_uv = uv + (direction * red_offset);
    float red = texture(tex, red_uv).r;

    vec2 green_uv = uv + (direction * green_offset);
    float green = texture(tex, green_uv).g;

    vec2 blue_uv = uv + (direction * blue_offset);
    float blue = texture(tex, blue_uv).b;

    color = vec4(red, green, blue, alpha);
}