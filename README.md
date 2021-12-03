# Python-OpenGL-Engine
A Graphics Engine that I made in Python using OpenGL

# TODO List
## In Progress
[ ] Physics engine
  [ ] Physics class
		- Extends drawable?
		[ ] Center of mass
			- Avg of all vertices
		[ ] Density
			- Mass multiplier
		[ ] Friction
			- Friction multiplier
		[ ] Elasticity
			- Bounciness multiplier
		[ ] Sleeping
			- If true, less calculations are done
			- Will become true after interacted with
		[ ] Position
		[ ] Orientation
		[ ] Velocity
		[ ] Rot Velocity
	[ ] Gravity
	[ ] Anchoring
	[ ] Collision System
		- Objects will be assigned a group, and only the objects in that group or adjacent groups will be checked for collisions
		- Will check if any line between two vertices cross the surface of another object
		- !!!!! Optimize collision system by doing checks to see if it is necessary to even calculate every verticies actual position !!!!!

## Planned
[ ] Player system
	[ ] FPS camera
	[ ] wasd movement
	[ ] mouse camera rotation
	[ ] spacebar jump
	[ ] shift sprint
	[ ] control crouch
	[ ] camera bobbing
	[ ] player collision
	[ ] gravity
	[ ] momentum
[ ] Loading different maps from file
[ ] Main Menu
[ ] Pause menu
[ ] level select
[ ] level builder
	[ ] Spawn
	[ ] Goal
	[ ] Traps
	[ ] Interactables (buttons/switches)
	[ ] Enemies
	[~] lighting
[ ] Implemenmt model scaling
[ ] Make textures load in background like models do
[ ] Advanced texturing support

### Shelved
[~] Lighting engine

#### Implemented (Not Tested)
[x] Different meshes in a model can have different textures

##### Complete
[X] Reuse loaded models
[X] Reuse loaded textures
[X] Drawables can override the textures in the meshes
