#version 330 core
layout (location = 0) in vec3 pos;
layout (location = 1) in vec3 n_map;
layout (location = 2) in vec2 t_coord_in;

out vec2 t_coord;

uniform mat4 perspective;
uniform mat4 model;
uniform mat4 view;

void main()
{
	gl_Position = perspective*view*model*vec4(pos,1.0);
	t_coord = t_coord_in;
}