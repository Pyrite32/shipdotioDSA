shader_type canvas_item;
uniform float interval = 30.0;
uniform bool enabled = true;

void fragment() {
	vec4 base = texture(TEXTURE,UV);
	if (!enabled)
	{
		COLOR = base;
	}
	else
	{
		float bar_condition = step(0.5,sin(UV.x*interval+TIME+UV.y*3.0)*sin(UV.x*interval+TIME+UV.y*3.0));
		COLOR = base;
		vec3 stripe_color = COLOR.rgb + vec3(0.1, 0.0, 0.0);
		COLOR.rgb += vec3(stripe_color.r * step(0.5,bar_condition),
						 stripe_color.g * step(0.5,bar_condition),
						 stripe_color.b * step(0.5,bar_condition));
	}
	
	
}
