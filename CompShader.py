#OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *

#Custom imports
import Texture as tx

class CompShader:
	
	#Class attributes
	comp_shaders = {}
	comp_programs = {}

	def clean_all():
		for key in CompShader.comp_shaders.keys():
			shader = CompShader.comp_shaders[key]
			glDeleteShader(shader)
		for key in CompShader.comp_programs.keys():
			prog = CompShader.comp_programs[key]
			prog.clean()

	#Instance attributes
    #Initialize
	def __init__(self,*args):
		#Shader file paths
		self.f_path = None
		self.v_path = None

		#Current shader paths
		self.f_sh_id = None
		self.v_sh_id = None

		#Program id
		self.id = glCreateProgram()

		self.active_tex = []

		#Call update_program()
		if len(args) == 0:
			self.update_program(f_path='DEF',v_path='DEF')
		elif len(args) == 1:
			self.update_program(f_path=args[0]+'.frag',v_path=args[0]+'.vert')
		elif len(args) == 2:
			self.update_program(f_path=args[0],v_path=args[1])
		else:
			raise Exception('Excpected 0, 1, or 2 arguments, got '+str(len(args)))
	
	#Updates program using new file paths
	def update_program(self,f_path=None,v_path=None):
		#Uses default shaders
		if f_path == 'DEF':
			f_path = 'Shaders/Default.frag'
		if v_path == 'DEF':
		   v_path = 'Shaders/Default.vert'
		
		#Ignore current shaders
		if self.f_path == f_path:
			f_path = None
		if self.v_path == v_path:
			v_path = None

		#Update shader paths
		if f_path != None:
			self.f_path = f_path
		if v_path != None:
			self.v_path = v_path

		#Check existing programs
		if self.get_prog_name() in CompShader.comp_programs.keys():
			glDeleteProgram(self.id)
			self = CompShader.comp_programs[self.get_prog_name()]
			return
		else:
			#Get shaders from path
			if f_path != None:
				self.f_sh_id = self.get_shader(f_path,GL_FRAGMENT_SHADER)
				glAttachShader(self.id,self.f_sh_id)
			if v_path != None:
				self.v_sh_id = self.get_shader(v_path,GL_VERTEX_SHADER)
				glAttachShader(self.id,self.v_sh_id)
			CompShader.comp_programs[self.get_prog_name()] = self

		glLinkProgram(self.id)

		success = glGetProgramiv(self.id,GL_LINK_STATUS)
		if not success:
			info_log = glGetProgramInfoLog(self.id)
			raise Exception('Shader Creation Failed: '+info_log)

	#Get shader of type from path
	def get_shader(self,path,type):
		#If compiled shader is stored
		if path in CompShader.comp_shaders.keys():
			#Check if shader still exist
			try:
				#Check existing shader for correct type
				if GglGetShaderiv(CompShader.comp_shaders[path],GL_SHADER_TYPE) != type:
					#Raise error
					raise ValueError('Found existing shader, but shader has the wrong shader type')
				else:
					#Return existing shader to use
					return CompShader.comp_shaders[path]
			except ValueError as e:
				#Reraise error from shader type
				raise e
			except Exception as e:
				#Shader was stored, but has been deleted
				#Remove from stored list
				CompShader.comp_shaders.pop(path)
				#Call function again
				return self.get_shader(path,type)
		else:
			#Shader is not stored
			#Create new shader and return
			return self.create_shader(path,type)

	#Create a shader from the source
	def create_shader(self,path,type):
		#Get shader source from file
		data = ''
		with open(path,mode='r',encoding='utf-8') as file:
			data += file.read()
			data += '\0'

		#Create shader
		shader = glCreateShader(type)
		
		#Attach source
		glShaderSource(shader,data)

		#Compile shader
		glCompileShader(shader)
		
		#Add self to compiled shader objects
		CompShader.comp_shaders[path] = shader
		
		glShaderSource(shader,'')

		#Check for errors
		s = glGetShaderiv(shader, GL_COMPILE_STATUS)
		if not s:
			print(glGetShaderInfoLog(shader))

		success = glGetShaderiv(shader,GL_COMPILE_STATUS)
		if not success:
			raise Exception(glGetShaderInfoLog(shader))
		
		#Return shader
		return shader

	def clear_use_textures(self):
		while len(self.active_tex) > 0:
			glUniform1i(glGetUniformLocation(self.id,self.active_tex.pop(0)),False)

	def use_texture(self, texture='color_t', use=True):
		glUniform1i(glGetUniformLocation(self.id,'use_'+texture),use)
		self.active_tex.append('use_'+texture)

	def use_shader(self):
		glUseProgram(self.id)

	#Gets programs name
	def get_prog_name(self):
		#Combines shader paths and returns
		return self.f_path+self.v_path

	def clean(self):
		try:
			glDeleteProgram(self.id)
		except BaseException as e:
			pass