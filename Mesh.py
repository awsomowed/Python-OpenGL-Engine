#OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
import glm

#Utility imports
import ctypes as ct
import numpy as np

#General imports
import sys

#Custom imports
import Texture as tx

class Mesh:
	#Class attributes

	#Instance attributes
	def __init__(self,vertices=None,normals=None,t_coords=None,indices=None,textures=None):
		self.vertices = vertices
		self.normals = normals
		self.t_coords = t_coords
		self.indices = indices
		self.textures = textures

		self.b_vertices = None
		self.b_indices = None
		self.draw_tex = {}

		self.VAO = glGenVertexArrays(1)
		self.VBO = glGenBuffers(1)
		self.EBO = glGenBuffers(1)

		self.build_vertices()
		self.build_indices()

		self.update_buffers()

	def build_vertices(self):
		new_v = []
		for i in range(len(self.vertices)):
			new_v.extend(self.vertices[i])
			new_v.extend(self.normals[i])
			new_v.extend(self.t_coords[i])
		self.b_vertices = np.array(new_v,dtype='float32')

	def build_indices(self):
		new_i = []
		for i in range(len(self.indices)):
			new_i.extend(self.indices[i])
		self.b_indices = np.array(new_i,dtype='int32')

	def update_buffers(self):

		glBindVertexArray(self.VAO)

		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
		glBufferData(GL_ARRAY_BUFFER, self.b_vertices, GL_STATIC_DRAW)

		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.b_indices, GL_STATIC_DRAW)

		glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,8*self.b_vertices.itemsize,None)
		glEnableVertexAttribArray(0)

		glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,8*self.b_vertices.itemsize,ctypes.c_void_p(3*self.b_vertices.itemsize))
		glEnableVertexAttribArray(1)

		glVertexAttribPointer(2,2,GL_FLOAT,GL_FALSE,8*self.b_vertices.itemsize,ctypes.c_void_p(6*self.b_vertices.itemsize))
		glEnableVertexAttribArray(2)

		glBindVertexArray(0)

	def add_texture(self, tex, uniform):
		if type(tex) == str:
			tex = tx.Texture.new(tex)

		self.draw_tex[uniform] = tex

	def bind_all_textures(self, shader, tex_ovr):
		slot_ct = 0
		for uniform in self.draw_tex:
			if uniform in tex_ovr.keys():
				continue
			shader.use_texture(uniform)
			self.bind_texture(shader.id,self.draw_tex[uniform],slot_ct,uniform)
			slot_ct+=1
		for uniform in tex_ovr:
			shader.use_texture(uniform)
			self.bind_texture(shader.id,tex_ovr[uniform],slot_ct,uniform)
			slot_ct+=1

	def bind_texture(self,shader_id,texture,slot=0,uniform=None):
		glActiveTexture(GL_TEXTURE0+slot)
		glBindTexture(GL_TEXTURE_2D, texture.id)
		glUniform1i(glGetUniformLocation(shader_id,uniform),slot)

	def draw(self, shader, tex_ovr = {}):
		shader.use_shader()
		glBindVertexArray(self.VAO)
		self.bind_all_textures(shader, tex_ovr)
		glDrawElements(GL_TRIANGLES,len(self.b_indices),GL_UNSIGNED_INT,None)
		shader.clear_use_textures()

	def clean(self):
		for texture in self.textures:
			texture.clean()
		try:
			glDeleteVertexArrays(1,self.VAO)
			glDeleteBuffers(1,self.VBO)
			glDeleteBuffers(1,self.EBO)
		except:
			pass