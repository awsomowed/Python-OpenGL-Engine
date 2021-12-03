#version 330 core
out vec4 FragColor;

in vec2 t_coord;

uniform sampler2D color_t;

uniform bool use_color_t;

void main()
{
	if (use_color_t)
	//if (1==2)
	{
		FragColor = texture(color_t,t_coord);
	}
	else
	{
		//if (mod(round(t_coord.x*100),2)==0)
		if (1==2)
		{
			FragColor = vec4(1.0f,0.0f,0.0f,1.0f);
		}
		else
		{
			//FragColor = vec4(0.0f,0.0f,1.0f,1.0f);
			FragColor = vec4(t_coord.xy,0.0f,1.0f);
		}
	}
	//FragColor = vec4(1.0f,1.0f,1.0f,1.0f);
}