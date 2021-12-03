#OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *

#Utility imports
from PIL import Image as img
from PIL import ImageOps as img_ops

#General imports

#Custom imports
import SharedFuncs as sf

class Texture:
	#Class attributes
	all_textures = {}
	loose_textures = []

	def clean_all():
		for tex in list(Texture.loose_textures):
			try:
				tex.clean()
			except BaseException as e:
				sf.print_error(e)
		for key in list(Texture.all_textures.keys()):
			try:
				Texture.all_textures[key].clean()
			except BaseException as e:
				sf.print_error(e)
	
	#Instance attributes
	def __init__(self):
		self.path = None
		self.c_format = 'RGB'
		self.id = glGenTextures(1)

	def new(*args):
		self = Texture()

		if len(args) == 1:
			if type(args[0]) == str:
				self.path = args[0]
				#Check for existing texture, if not, create from path
				self = self.find_texture()
			elif type(args[0]) == bytes:
				#Create new loose texture
				print('WARNING: Avoid using Loose Textures, they can impact performance negatively, and are unstable overall')
				self.create_loose(args[0])
			else:
				raise AttributeError("Got unexpected argument of type '"+str(type(args[0]))+"': "+str(args[0]))
		elif len(args) == 2:
			for arg in args:
				if type(arg) == str:
					self.path = arg
				elif type(arg) == bytes:
					#Create new texture from bytes with path
					self = self.find_texture(arg)
				else:
					raise AttributeError("Got unexpected argument of type '"+str(type(arg))+"': "+str(arg))
		else:
			raise AttributeError("Got unexpected arguments, expected 1-2, got "+str(len(args))+":\nargs: "+str(args))
		return self

	def create_loose(self, data):
		ds_sqrt = round(len(list(data))**0.5,0)
		self.create_texture(data, (ds_sqrt,ds_sqrt))
		Texture.loose_textures.append(self)

	def find_texture(self, data = None):
		if self.path in Texture.all_textures.keys():
			try:
				glDeleteTextures(1,self.id)
			except TypeError as e:
				pass
			self = Texture.all_textures[self.path]
		elif data != None:
			self.load_texture(data)
			Texture.all_textures[self.path] = self
		else:
			self.load_texture(*self.load_data())
			Texture.all_textures[self.path] = self
		return self

	def create_texture(self, data, dimensions):
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D,self.id)
		if self.c_format == 'RGB':
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, *dimensions, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
		elif self.c_format == 'RGBA':
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, *dimensions, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
		else:
			raise AttributeError("Unknown color format of '"+self.c_format+"'")
		glGenerateMipmap(GL_TEXTURE_2D)

	def load_texture(self, data, dimensions=None):
		if dimensions != None:
			self.create_texture(data, dimensions)
		else:
			self.create_texture(data,(round(len(list(data))**0.5,0),)*2)

	def load_data(self):
		file = img.open(self.path)
		file = img_ops.flip(file)
		dbg = file.getdata()
		data = list(file.getdata())
		dimensions = (file.getbbox()[2:4])
		self.c_format = file.mode
		file.close()
		return data, dimensions


	def clean(self):
		try:
			glDeleteTextures(1,self.id)
			Texture.all_textures.pop(self.path)
		except TypeError as e:
			pass