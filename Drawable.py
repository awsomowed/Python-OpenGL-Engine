#OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
import glm

#Utility imports
import ctypes as ct

#Custom imports
import CompShader as csh
import Texture as tx
import Model

class Drawable:
	#Class attributes
	all_drawables = []

	def update_all_perspective(perspective):
		for dbl in Drawable.all_drawables:
			dbl.set_perspective(perspective)
		return None

	def clean_all():
		while len(Drawable.all_drawables) != 0:
			Drawable.all_drawables.pop(0).clean()
		return None

	#Instance attributes
	def __init__(self,*args):
		self.model = None
		self.shader = None
		self.model_matrix = glm.mat4(1.0)

		self.model_uniform = None
		self.view_uniform = None

		self.tex_over = []
		self.all_tex_over = {}

		for arg in args:
			if type(arg) == Model.Model:
				self.model = arg
				self.model.add_user(self)
			elif type(arg) == csh.CompShader:
				self.shader = arg
				self.shader.use_shader()
				self.model_uniform = glGetUniformLocation(self.shader.id,"model")
				self.view_uniform = glGetUniformLocation(self.shader.id,"view")
			elif type(arg) == str:
				f_type = arg[arg.rindex('.')+1:]
				if f_type == 'fbx':
					self.model = Model.Model.new(arg)
					self.model.add_user(self)
				elif f_type == 'obj':
					self.model = Model.Model.new(arg)
					self.model.add_user(self)
				else:
					raise AttributeError("Unable to handle file of type '"+str(f_type)+"'")
			else:
				raise AttributeError("Unexpected Argument of type '"+str(type(arg))+"': "+str(arg))

			Drawable.all_drawables.append(self)

	def translate_v3(self,vec):
		self.model_matrix = glm.translate(self.model_matrix,vec)

	def translate(self,*trans):
		self.model_matrix = glm.translate(self.model_matrix,glm.vec3(*trans))

	def rotate(self,magnitude,*trans):
		self.model_matrix = glm.rotate(self.model_matrix,magnitude,glm.vec3(*trans))
	
	def reset_matrix(self):
		self.model_matrix = glm.mat4(1.0)
		
	def override_texture(self, tex, uniform, mesh=-1):
		if type(tex) == str:
			tex = tx.Texture.new(tex)

		if mesh == -1:
			for i in range(len(self.tex_over)):
				self.tex_over[i][uniform] = tex
			self.all_tex_over[uniform] = tex
		else:
			self.tex_over[mesh][uniform] = tex


	def set_perspective(self,perspective):
		glUniformMatrix4fv(
			glGetUniformLocation(self.shader.id,'perspective'),
			1,GL_FALSE,glm.value_ptr(perspective))

	def model_load_callback(self):
		new_tx_over = self.model.get_empty_tx_arr()
		for i in range(len(new_tx_over)):
			if i < len(self.tex_over):
				new_tx_over[i] = self.tex_over[i]
			for key in self.all_tex_over:
				if i < len(self.tex_over):
					if not key in self.tex_over[i].keys():
						new_tx_over[i][key] = self.all_tex_over[key]
				else:
					new_tx_over[i][key] = self.all_tex_over[key]
			self.tex_over = new_tx_over

	def draw(self,view_matrix):
		if self.model.is_loaded:
			self.shader.use_shader()
			glUniformMatrix4fv(self.model_uniform,1,GL_FALSE,glm.value_ptr(self.model_matrix))
			glUniformMatrix4fv(self.view_uniform,1,GL_FALSE,glm.value_ptr(view_matrix))
			self.model.draw(self.shader,self.tex_over)
		#else:
			#if self.model.retry_load():
				#Drawable.draw(self,view_matrix)
				#self.draw(view_matrix)
	def clean(self):
		self.shader.clean()
		self.model.clean()