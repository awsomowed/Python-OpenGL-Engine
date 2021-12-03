#OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
import glm

#Utility imports

#General imports
import math as m

#Custom imports
import CompShader as csh
import Drawable as dbl
import Model as mdl

class CenteredList(list):
	def __init__(self):
		list.__init__(self)
		self.append(None)
		self.min = 0
		self.center_i = 0
		self.max = 0

	def __setitem__(self,key,value):
		#Check if list can be shrunk
		if value == None:
			if len(self) < key+self.center_i:
				pass
			elif key+self.center_i < 0:
				pass
			else:
				#Set value with index offset by center
				list.__setitem__(self,key+self.center_i,value)
				while True:
					#Can remove negative pos
					if list.__getitem__(self,0) == None:
						#Check for 0
						if self.min != 0:
							self.pop(0)
							self.center_i-=1
							self.min+=1
						else:
							break
					else:
						break
				while True:
					#Can remove positive pos
					if list.__getitem__(self,-1) == None:
						if self.max != 0:
							self.pop(-1)
							self.max-=1
						else:
							break
					else:
						break
		else:
			#Check if list needs to be extended
			while True:
				if key < self.min:
					self.insert(0,None)
					self.center_i+=1
					self.min-=1
				else:
					break
			while True:
				if key > self.max:
					self.append(None)
					self.max+=1
				else:
					break
			#Set value with index offset by center
			list.__setitem__(self,key+self.center_i,value)

	def __getitem__(self,key):
		#Get value with index offset by center
		return list.__getitem__(self,key+self.center_i)

	def __str__(self):
		out = '['
		for i in range(len(self)):
			if list.__getitem__(self,i) != None:
				out += str(i-self.center_i)+': '+str(list.__getitem__(self,i))
			else:
				out += str(i-self.center_i)
			if i < len(self)-1:
				out+=', '
			else:
				out+=']'
		return out

	def is_empty(self):
		if len(self) <= 1:
			if self[0] == None:
				return True
		return False

class CenteredSpace(CenteredList):
	def __init__(self):
		CenteredList.__init__(self)

	def __setitem__(self,pos,value):
		if value == None:
			#Verify in existing bounds
			if pos[0] < self.min or pos[0] > self.max:
				pass
			y_ls = CenteredList.__getitem__(self,pos[0])
			if pos[1] < y_ls.min or pos[1] > y_ls.max:
				pass
			y_ls[pos[1]][pos[2]] = value
			#remove empty lists
			if y_ls[pos[1]].is_empty():
				y_ls[pos[1]] = None
			if y_ls.is_empty():
				CenteredList.__setitem__(self,pos[0],None)
		else:
			#Add new CenteredList if needed
			if pos[0] < self.min or pos[0] > self.max:
				CenteredList.__setitem__(self,pos[0],CenteredList())
			y_ls = CenteredList.__getitem__(self,pos[0])
			if pos[1] < y_ls.min or pos[1] > y_ls.max:
				y_ls[pos[1]] = CenteredList()
			y_ls[pos[1]][pos[2]] = value

	def __getitem__(self,pos):
		return CenteredList.__getitem__(self, pos[0])[pos[1]][pos[2]]

	def add_obj(self,x,y,z,obj):
		y_ls = CenteredList.__getitem__(self, x)
		if y_ls == None:
			y_ls = CenteredList()
			CenteredList.__setitem__(self, x, y_ls)
		z_ls = y_ls[y]
		if z_ls == None:
			z_ls = CenteredList()
			y_ls[y] = z_ls
		region = z_ls[z]
		if region == None:
			region = PhysicsRegion(x,y,z)
			z_ls[z] = region

class PhysicsRegion:
	#Class attributes
	REGION_SIZE = 25

	def find_region(*pos):
		if len(pos) == 1 and type(pos[0]) == glm.vec3:
			return m.floor(pos[0].x/PhysicsRegion.REGION_SIZE),m.floor(pos[0].y/PhysicsRegion.REGION_SIZE),m.floor(pos[0].z/PhysicsRegion.REGION_SIZE)
		else:
			return m.floor(pos[0]/PhysicsRegion.REGION_SIZE),m.floor(pos[1]/PhysicsRegion.REGION_SIZE),m.floor(pos[2]/PhysicsRegion.REGION_SIZE)

	#Instance attributes
	def __init__(self, x,y,z):
		self.x_bounds = (x*PhysicsRegion.REGION_SIZE,(x+1)*PhysicsRegion.REGION_SIZE)
		self.y_bounds = (y*PhysicsRegion.REGION_SIZE,(y+1)*PhysicsRegion.REGION_SIZE)
		self.z_bounds = (z*PhysicsRegion.REGION_SIZE,(z+1)*PhysicsRegion.REGION_SIZE)
		
		self.location = (x,y,z)

		self.phys_obj = []

	def get_collide_checks(self,this):
		all_checks = []
		for obj in self.phys_obj:
			if not obj is this:
				all_checks.append(obj)
		try:
			all_checks += this.space[self.location[0]+1,self.location[1],self.location[2]].phys_obj()
		except:
			pass
		try:
			all_checks += this.space[self.location[0]-1,self.location[1],self.location[2]].phys_obj()
		except:
			pass
		try:
			all_checks += this.space[self.location[0],self.location[1]+1,self.location[2]].phys_obj()
		except:
			pass
		try:
			all_checks += this.space[self.location[0],self.location[1]-1,self.location[2]].phys_obj()
		except:
			pass
		try:
			all_checks += this.space[self.location[0],self.location[1],self.location[2]+1].phys_obj()
		except:
			pass
		try:
			all_checks += this.space[self.location[0],self.location[1],self.location[2]-1].phys_obj()
		except:
			pass
		return all_checks

class Physical(dbl.Drawable):
	#Class attributes


	#Instance attributes
	def __init__(self, *args):
		self.LOADED = False

		self.hitbox = None
		
		model_a = None
		shader_a = None
		pass_args = []
		for arg in args:
			if type(arg) == str:
				if model_a == None:
					model_a = arg
				elif self.hitbox == None:
					self.hitbox = mdl.Model.new(arg)
					self.hitbox.add_user(self)
				else:
					pass_args.append(arg)
					raise AttributeError('Unexpected Argument: ' + arg)
			elif type(arg) == mdl.Model:
				if model_a == None:
					model_a = arg
				elif self.hitbox == None:
					self.hitbox = arg
					self.hitbox.add_user(self)
				else:
					pass_args.append(arg)
					raise AttributeError('Unexpected Argument: ' + arg)
			elif type(arg) == csh.CompShader:
				if shader_a == None:
					shader_a = arg
				else:
					pass_args.append(arg)
					raise AttributeError('Unexpected Argument: ' + arg)
			else:
				pass_args.append(arg)
				raise AttributeError('Unexpected Argument: ' + arg)

		if not shader_a == None:
			pass_args = [shader_a] + pass_args
		if not model_a == None:
			pass_args = [model_a] + pass_args

		dbl.Drawable.__init__(self,*pass_args)

		if self.hitbox == None:
			self.hitbox = self.model

		#avg pos of all faces, calculated from the center of the face
		#each face will be weighted by its area
		#after finding average of all weighted face pos, divide by average weight
		#Should result in correct center of mass
		self.c_mass = glm.vec3(0) #Center of mass
		self.h_mass = 0 #Average distance between c_mass and all vertices

		self.min_x = 0
		self.max_x = 0
		self.min_y = 0
		self.max_y = 0
		self.min_z = 0
		self.max_z = 0

		self.density = 1
		self.friction = 1
		self.elasticity = 1

		self.locked = False

		self.sleeping = False

		self.position = glm.vec3(0)
		self.orientation = glm.vec3(0)

		self.velocity = glm.vec3(0)
		self.rot_velocity = glm.vec3(0)

		self.forces = []

		self.space = None
		self.phys_reg = None

		self.hitbox_vertices = []
		self.collide_vertices = []

		self.hitbox_faces = []
		self.collide_faces = []

		self.last_matrix = self.model_matrix

	def model_load_callback(self, caller):
		if caller == self.model:
			dbl.Drawable.model_load_callback(self)
		if caller == self.hitbox:
			self.update_hitbox_faces()
			self.update_hitbox_vertices()

	def update_hitbox_vertices(self):
		#Only on model load
		def new_vertex(vertex):
			for c_vert in self.hitbox_vertices:
				if c_vert.x == vertex.x and c_vert.y == vertex.y and c_vert.z == vertex.z:
					return None
			self.hitbox_vertices.append(vertex)

		def new_face(face):
			for vert in face:
				new_vertex(vert)
		
		[new_face(face) for face in self.hitbox_faces]

	def update_hitbox_faces(self):
		#Only on model load
		for mesh in self.hitbox.meshes:
			for index in mesh.indices:
				self.hitbox_faces.append((
					glm.vec4(mesh.vertices[index[0]],1),
					glm.vec4(mesh.vertices[index[1]],1),
					glm.vec4(mesh.vertices[index[2]],1) ))

	def update_collide_faces(self):
		#Every Frame
		self.collide_faces = []
		for face in self.hitbox_faces:
			self.collide_faces.append((
				face[0]*self.model_matrix,
				face[1]*self.model_matrix,
				face[2]*self.model_matrix))

	def update_collide_vertices(self):
		#Every Frame
		self.collide_vertices = []
		for vertex in self.hitbox_vertices:
			self.collide_vertices.append(vertex*self.model_matrix)

	def draw(self,view_matrix):
		if self.LOADED == True:
			self.update()
			self.last_matrix = self.model_matrix
			self.translate_v3(self.position)
			self.update_collide_faces()
			self.update_collide_vertices()
			self.check_collisions()
			dbl.Drawable.draw(self,view_matrix)
			self.reset_matrix()
		else:
			if self.model.is_loaded == True and self.hitbox.is_loaded == True:
				self.LOADED = True
				self.draw(view_matrix)

			#if self.model.is_loaded == False and self.model.retry_load():
			#	self.draw(view_matrix)
			
			#if self.hitbox.is_loaded == False and self.hitbox.retry_load():
			#	self.draw(view_matrix)

	#	#	#
	#When drawing an object, it will first apply any forces added to it
	#Force format: (apply_point(3tuple), angle(2tuple), magnitude)
	#To apply force, will get angle of origin to f_point and f_direction
	#This angle will be used to determine how much force is applied rotationally and translationally
	#During calculation:
	#	
	#	#	#

	def check_collisions(self):

		for obj in (self.space[self.phys_reg[0],self.phys_reg[1],self.phys_reg[2]].get_collide_checks(self)):
			collide_possible = False
			#Check if there is possibility of collision (uses max and in x y and z values)
			#if collide_possible:
			if True:
				#get only verticies that have a chance of collision based off of max x, y, and z values
				#get only faces that have a chance of collision based off of max x, y and z values
				
				for index, vertex in enumerate(self.collide_vertices):
					print(index)
					vertex_last = self.hitbox_vertices[index]*self.last_matrix
					for face in obj.collide_faces:
						#TEMPORARY SOLUTION
						f_x_cds = [v.x for v in face]
						f_x_cds.sort()
						f_max_x = f_x_cds[0]
						f_min_x = f_x_cds[2]
						f_y_cds = [v.y for v in face]
						f_y_cds.sort()
						f_max_y = f_y_cds[0]
						f_min_y = f_y_cds[2]
						f_z_cds = [v.z for v in face]
						f_z_cds.sort()
						f_max_z = f_z_cds[0]
						f_min_z = f_z_cds[2]

						if f_max_y >= vertex.y and f_max_y <= vertex_last.y:
							self.velocity.y = -self.velocity.y
						#pass
						#check x
						#check y
						#check z

				#Check to see if vertex is inbetween faces vertices on x, y, or z axis
				#Find center of face
				#TWO WAYS
				#Account for rotation in math
				#store rotated verte
				#TWO WAYS
				#Check if vertex moved from one side to the other side

				#get all potential verticies/faces
				#check collisions
				#if collission:
					#apply force to both objects
			#pass

	def update(self):
		#Apply gravity
		if not self.locked:
			self.velocity += glm.vec3(0,-0.0001,0)
			pass
		for force in self.forces:
			#Apply forces
			pass
		#Apply velocity
		self.position += self.velocity
		#Apply momentum loss
		self.velocity.x -=self.velocity.x/100
		self.velocity.y -=self.velocity.y/100
		self.velocity.z -=self.velocity.z/100
		#self.velocity -= self.velocity/10

	def apply_force(self, f_tuple):
		#((f_point_x,f_point_y,f_point_z),(f_angle,f_elevation),magnitude)
		if not self.Locked:
			self.force.append(f_tuple)

	def add_to_space(self,space):
		self.space = space
		self.phys_reg = (PhysicsRegion.find_region(self.position))
		space.add_obj(*self.phys_reg,self)
		#space[self.phys_reg].phys_obj.append(self)
		space[self.phys_reg[0],self.phys_reg[1],self.phys_reg[2]].phys_obj.append(self)
		#space[*self.phys_reg].phys_obj.append(self)