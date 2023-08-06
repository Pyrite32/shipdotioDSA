shader_type canvas_item;

void fragment() {
	float dist = distance(UV, vec2(0.5,0.5));
	vec4 base_color = texture(TEXTURE,UV);
	COLOR = base_color;
	COLOR.a = 1.0-step(0.50, dist);
}