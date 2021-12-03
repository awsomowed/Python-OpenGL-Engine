#OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
import glm

#Utility imports
import pyassimp as pim
import numpy as np
import ctypes as ct

#General imports
import time as t
import os

#Custom imports
import Texture as tx
import Mesh

class Model:
	#Class attributes

	new_called = False

	loading_models = []

	all_models = {}

	def retry_all_loading():
		for model in list(Model.loading_models):
			model.retry_load()

	def clean_all():
		for path in Model.all_models.keys():
			model = Model.all_models[path]

			model.clean()
			Model.all_models.pop(path)

	def load_model_texture(texture, model, uniform, mesh=-1):
		if type(model) == str:
			model = Model.new(model)
		
		if mesh == -1:
			for mesh_a in model.meshes:
				model.add_texture(texture,mesh_a,uniform)
			model.all_textures[uniform] = texture
		else:
			model.add_texture(texture, mesh, uniform)

	#Instance attributes
	def __init__(self, path):
		if Model.new_called == False:
			raise Exception('Invalid initialization, use Model.new() instead of Model()')
		self.is_loaded = False
		self.all_textures = {}
		self.textures = []
		self.meshes = []
		self.dir = None
		self.path = path
		self.users = []

	def new(path):
		Model.new_called = True
		self = Model(path)
		
		self = self.find_model(path)

		if not self.is_loaded:
			if not self in Model.loading_models:
				Model.loading_models.append(self)

		Model.all_models[path] = self
		Model.new_called = False
		return self

	def find_model(self, path):
		if path in Model.all_models:
			return Model.all_models[path]
		else:
			self.load_model(path)
			return self

	def load_model(self, path):
		try:
			try:
				scene = pim.load(path,processing=pim.postprocess.aiProcess_Triangulate)
			except BaseException as e:
				self.is_loaded = False
				return False

			self.dir = path[:path.rindex('/')]

			self.process_node(scene.mRootNode,scene)

			for usr in self.users:
				usr.model_load_callback(self)

			for i in range(len(self.meshes)):
				for key in self.textures[i]:
					self.meshes[i].add_texture(self.textures[i][key], key)

			for key in self.all_textures:
				Model.load_model_texture(self.all_textures[key],self,key)

			self.is_loaded = True

			return True
		finally:
			try:
				pim.release(scene)
			except:
				pass

	def retry_load(self):
		if self.load_model(self.path):
			Model.loading_models.pop(Model.loading_models.index(self))
			return True
		else:
			return False

	def process_node(self, node, scene):
		for i in range(node.contents.mNumMeshes): 
			mesh = scene.mMeshes[node.contents.mMeshes[i]]
			self.meshes.append(self.process_mesh(mesh, scene))
			self.textures.append({})

		for i in range(node.contents.mNumChildren):
			self.process_node(node.contents.mChildren[i], scene)

	def process_mesh(self, mesh, scene):
		vertices = []
		normals = []
		t_coords = []

		indices = []
		textures = []

		for i in range(mesh.contents.mNumVertices):
			vertices.append((
				mesh.contents.mVertices[i].x,
				mesh.contents.mVertices[i].y,
				mesh.contents.mVertices[i].z
				))

			normals.append((
				mesh.contents.mNormals[i].x,
				mesh.contents.mNormals[i].y,
				mesh.contents.mNormals[i].z
				))

			if mesh.contents.mTextureCoords[0]:
				t_coords.append((
					mesh.contents.mTextureCoords[0][i].x,
					mesh.contents.mTextureCoords[0][i].y
					))

		for i in range(mesh.contents.mNumFaces):
			face = mesh.contents.mFaces[i]
			f_ind = ()
			for j in range(face.mNumIndices):
				f_ind += (face.mIndices[j],)
			indices.append(f_ind)

		material = None
		if mesh.contents.mMaterialIndex >= 0:
			material = scene.mMaterials[mesh.contents.mMaterialIndex]

			if len(scene.textures) != 0:
				diffuse_maps = self.load_material_textures(material, pim.material.aiTextureType_DIFFUSE, 'texture_diffuse')
				textures.extend(diffuse_maps)

				specular_maps = self.load_material_textures(material, pim.material.aiTextureType_SPECULAR, 'texture_specular')
				textures.extend(specular_maps)

		return Mesh.Mesh(vertices=vertices,normals=normals,t_coords=t_coords,indices=indices,textures=textures)

	def add_texture(self, tex, mesh, uniform):
		#if given a path
		if type(tex) == str:
			#Create the texture
			tex = tx.Texture.new(tex)
		if type(mesh) == int:
			self.textures[mesh][uniform] = tex
			mesh = self.meshes[mesh]
		else:
			self.textures[self.meshes.index(mesh)][uniform] = tex

		mesh.add_texture(tex,uniform)

	def get_empty_tx_arr(self):
		return [{} for x in self.textures]

	def add_user(self,usr):
		self.users.append(usr)

	def rem_usr(self,usr):
		self.users.pop(self.users.index(usr))

	def draw(self,shader,tx_ovr=None):
		if tx_ovr == None:
			for mesh in self.meshes:
				mesh.draw(shader)
		else:
			for i in range(len(self.meshes)):
				if i >= len(tx_ovr):
					self.meshes[i].draw(shader)
				else:
					self.meshes[i].draw(shader,tx_ovr[i])
		return None

	def clean(self):
		for mesh in self.meshes:
			mesh.clean()
		if self.path in Model.all_models:
			Model.all_models.pop(self.path)