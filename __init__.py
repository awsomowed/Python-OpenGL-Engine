#OpenGL Imports
from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import glm

#Utility Imports
import numpy as np
import pyassimp as pim

#General Imports
import os
import sys
import math as m
import time as t

#Custom Imports
import SharedFuncs as sf
import CompShader as csh
import Drawable as dbl
import Physical as phs
import Texture as tx
import Model as mdl
import Mesh

class Camera:
	def __init__(self):
		self.pos = glm.vec3(0.0,0.0,0.0)
		self.front = glm.vec3(0.0,0.0,-1.0)
		self.up = glm.vec3(0.0,1.0,0.0)

		self.yaw = -90.0
		self.pitch = 0.0

		self.view_matrix = None

		self.rebuild_matrix()

	def rebuild_front(self):
		direction = glm.vec3()
		direction.x = m.cos(glm.radians(self.yaw))*m.cos(glm.radians(self.pitch))
		direction.y = m.sin(glm.radians(self.pitch))
		direction.z = m.sin(glm.radians(self.yaw))*m.cos(glm.radians(self.pitch))
		self.front = glm.normalize(direction)

	def rebuild_matrix(self):
		self.rebuild_front()
		new_mat = glm.lookAt(
			self.pos,
			self.pos+self.front,
			self.up)
		self.view_matrix = new_mat


def main():
	try:
		start = t.time()

		#Initialize glfw
		if not glfw.init():
			raise Exception('Failed to initialize glfw')

		#Specify OpenGL version
		glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,3)
		glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,3)
		glfw.window_hint(glfw.OPENGL_PROFILE,glfw.OPENGL_CORE_PROFILE)

		#glfw window hints
		glfw.window_hint(glfw.MAXIMIZED,glfw.TRUE)

		#Create window
		global window_size
		window_size = (600,600)
		window = glfw.create_window(*window_size,'Python OpenGL Engine v0.4',None,None)
		if window == None:
			raise Exception('Failed to create glfw window')

		#Updates the windows OpenGL context
		glfw.make_context_current(window)

		#Sets the OpenGL viewport
		glViewport(0,0,*window_size)

		#Perspective transformation matrix
		global perspective
		perspective = glm.perspective(glm.radians(45.0),window_size[0]/window_size[1],0.1,100.0)

		#Set resize callback
		glfw.set_framebuffer_size_callback(window, resize_callback)

		#Enable depth test
		glEnable(GL_DEPTH_TEST)

		#Set OpenGL texture paramaters
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		
		#Updates the window size
		resize_callback(window, *glfw.get_window_size(window))

		print(str(t.time()-start)+" seconds for initialization")
		start = t.time()

		#Create camera
		global main_cam
		main_cam = Camera()

		print(str(t.time()-start)+" seconds for camera")
		start = t.time()

		#Load shaders
		def_shader = csh.CompShader()

		print(str(t.time()-start)+" seconds for shader")
		start = t.time()

		#Load models
		mdl.Model.load_model_texture('Textures/Car Texture 1.png','Models/car_1_r.fbx','color_t')
		#mdl.Model.load_model_texture('Textures/Car Texture 2.png','Models/car_2.fbx','color_t')
		#mdl.Model.load_model_texture('Textures/Debug_0.png','Models/Not-Cube.obj','color_t')
		#mdl.Model.load_model_texture('Textures/Debug_0.png','Models/Square.fbx','color_t')

		print(str(t.time()-start)+" seconds for models and model textures")
		start = t.time()

		#Load physicals
		ground = phs.Physical('Models/Platform.fbx', def_shader)
		p_car_1 = phs.Physical('Models/car_1_r.fbx', 'Models/car_1_hitbox.fbx', def_shader)

		#Load drawables
		#car_1 = dbl.Drawable('Models/car_1.fbx', def_shader)
		#car_1_0 = dbl.Drawable('Models/car_1.fbx',def_shader)
		#car_1_1 = dbl.Drawable('Models/car_1.fbx',def_shader)
		#car_2 = dbl.Drawable('Models/car_2.fbx', def_shader)
		#not_cube = dbl.Drawable('Models/Not-Cube.obj', def_shader)
		#plane = dbl.Drawable('Models/Square.fbx', def_shader)

		print(str(t.time()-start)+" seconds for drawables + Physicals")
		start = t.time()

		#Load Override Textures
		#car_1_1.override_texture('Textures/Car Texture 1 Blue.png','color_t')

		print(str(t.time()-start)+" seconds for texture overrides")
		start = t.time()

		#Create Physical Spaces
		global main_space
		main_space = phs.CenteredSpace()

		#Final setup
		ground.add_to_space(main_space)
		ground.locked = True
		p_car_1.add_to_space(main_space)

		#Update perspective
		dbl.Drawable.update_all_perspective(perspective)

		#Timing variables

		#sf.delta_t = 0
		#last_f = 0

		main_cam.pos = glm.vec3(0,-3,7)

		fps = 1

		#Main loop
		while not glfw.window_should_close(window):
			#Update timing
			cur_t = glfw.get_time()
			sf.delta_t = cur_t - sf.last_f
			sf.last_f = cur_t

			#Display FPS
			fps = (fps*(fps-1)+(1/sf.delta_t))/fps
			glfw.set_window_title(window,'Python OpenGL Engine v0.4 [FPS: '+str(round(fps,1))+']')

			#Process input
			process_input(window)

			#Set clear color
			glClearColor(0.2,0.3,0.3,1.0)

			#Clear window
			glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

			#Update camera
			main_cam.rebuild_matrix()
			
			#Attempt to load unloaded models
			mdl.Model.retry_all_loading()

			#Translation
			#car_1.translate(2.5,0,2.5)
			#car_1_0.translate(7.5,0,glm.sin(cur_t)*10)
			#car_1_1.translate(glm.sin(cur_t)*12.5,0,glm.cos(cur_t)*12.5)
			#car_2.translate(2.5,0,-2.5)
			#not_cube.translate(-2.5,0,2.5)
			#plane.translate(-2.5,0,-2.5)

			#Rotation
			#car_1.rotate(cur_t/2,0,1,0)
			#car_1_0.rotate(cur_t,0,1,0)
			#car_1_1.rotate(cur_t+180,0,1,0)
			#car_2.rotate(glm.cos(cur_t)/5,0,0,1)
			#car_2.rotate(glm.sin(cur_t)/5,1,0,0)
			#not_cube.rotate(cur_t,0.2,0.5,0.8)
			#plane.rotate(cur_t,0.5,0.5,0.5)

			#Draw objects
			ground.draw(main_cam.view_matrix)
			p_car_1.draw(main_cam.view_matrix)
			#car_1.draw(main_cam.view_matrix)
			#car_1_0.draw(main_cam.view_matrix)
			#car_1_1.draw(main_cam.view_matrix)
			#car_2.draw(main_cam.view_matrix)
			#not_cube.draw(main_cam.view_matrix)
			#plane.draw(main_cam.view_matrix)

			#Reset transformations
			#car_1.reset_matrix()
			#car_1_0.reset_matrix()
			#car_1_1.reset_matrix()
			#car_2.reset_matrix()
			#not_cube.reset_matrix()
			#plane.reset_matrix()

			#Swap buffers
			glfw.swap_buffers(window)

			#Poll events
			glfw.poll_events()

		#End of main code
	except:
		raise
	finally:
		#Always clean up
		try:
			dbl.Drawable.clean_all()
			print('Drawables cleaned')
		except BaseException as e:
			sf.print_error(e)
		try:
			csh.CompShader.clean_all()
			print('Shaders cleaned')
		except BaseException as e:
			sf.print_error(e)
		try:
			mdl.Model.clean_all()
			print('Models cleaned')
		except BaseException as e:
			sf.print_error(e)
		try:
			tx.Texture.clean_all()
			print('Textures cleaned')
		except BaseException as e:
			sf.print_error(e)
		try:
			glfw.terminate()
			print('glfw cleaned')
		except BaseException as e:
			sf.print_error(e)
	return None

def resize_callback(window, width, height):
	if width <= 0:
		width = 1
	if height <= 0:
		height = 1
	print(width,height)
	global window_size, perspective
	window_size = (width, height)
	glViewport(0,0,*window_size)
	perspective = glm.perspective(glm.radians(45.0),window_size[0]/window_size[1],0.1,100.0)
	dbl.Drawable.update_all_perspective(perspective)

def process_input(window):
	global main_cam
	camera_speed = 2.5*sf.delta_t
	camera_rot = 25*sf.delta_t
	if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
		glfw.set_window_should_close(window, True)
	if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
		main_cam.pos += camera_speed*main_cam.front
	if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
		main_cam.pos -= camera_speed*main_cam.front
	if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
		main_cam.pos-= glm.normalize(glm.cross(main_cam.front,main_cam.up))*camera_speed
	if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
		main_cam.pos += glm.normalize(glm.cross(main_cam.front,main_cam.up))*camera_speed
	if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
		main_cam.pos += camera_speed*main_cam.up
	if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
		main_cam.pos -= camera_speed*main_cam.up
	if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
		main_cam.pitch += camera_rot
	if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
		main_cam.pitch -= camera_rot
	if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
		main_cam.yaw -= camera_rot
	if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
		main_cam.yaw += camera_rot


if __name__=='__main__':
	try:
		main()
	except BaseException as e:
		sf.print_error(e)
		raise
	except:
		print('Uncaught Exception')
		raise