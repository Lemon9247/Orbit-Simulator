from ursina import *
import math

GRAVITATIONAL_CONSTANT = 6.67*10
simulating = False  # Global variable used to pause/unpause the simulator

app = Ursina()
window.title = "3D Orbital Simulator"
window.borderless = False
window.fullscreen = True
window.exit_button.visible = False
window.fps_counter.enabled = True
time_interval = 0.001          # Time interval used for each simulation step

class Spectator(Entity):
# This class is used to control the camera
    def __init__(self,sensitivity=None,fov=None,speed=None):
        super().__init__()
        self.position = Vec3(0,0,0)
        self.speed = speed if speed != None else 20
        camera.position = self.position
        camera.rotation = Vec3(0,0,0)
        camera.fov = fov if fov != None else 70
        mouse.locked = True
        self.mouse_sensitivity = sensitivity if sensitivity != None else 30

    def update(self):
        if mouse.locked:
            # Rotate camera and player controller based on mouse motion.
            camera.rotation_x -= mouse.velocity[1]*self.mouse_sensitivity
            camera.rotation_x = clamp(camera.rotation_x,-90,90)
            self.rotation_y += mouse.velocity[0]*self.mouse_sensitivity
            camera.rotation_y = self.rotation_y

            # Calculate facing of the player controller
            self.direction = Vec3(self.forward*(held_keys["w"]-held_keys["s"])
            +self.right*(held_keys["d"]-held_keys["a"])
            ).normalized()

            # Move the player controller and the camera
            self.position += self.direction*self.speed*time.dt
            self.y += (held_keys["space"]-held_keys["shift"])*self.speed*time.dt
            camera.position = self.position

class Body(Entity):
# This class is used for physical bodies within the simulator.
    def __init__(self, mass = 0.0, position = None, velocity = None, acceleration = None, colour = None):
        super().__init__(model="sphere")
        self.mass = mass
        self.position = Vec3(position) if position != None else Vec3(0,0,0)
        self.velocity = Vec3(velocity) if velocity != None else Vec3(0,0,0)
        self.acceleration = Vec3(acceleration) if acceleration != None else Vec3(0,0,0)
        self.diameter = 10*math.log(mass,10)
        self.scale = (self.diameter,self.diameter,self.diameter)
        self.color = colour if colour != None else color.random_color()

    def change_position(self):
        return Vec3(self.position+self.velocity*time_interval)

    def change_velocity(self):
        return Vec3(self.velocity+self.acceleration*time_interval)

    def change_acceleration(self):
        acceleration = Vec3(0,0,0)
        for body in bodies: # Calculate net gravitational acceleration of the body due to each other body
            try:
                displacement = Vec3(self.position-body.position)
                distance = math.sqrt(dot_product(displacement,displacement))
                delta_a = Vec3(displacement*GRAVITATIONAL_CONSTANT*body.mass/(distance**3))
                acceleration = Vec3(acceleration-delta_a)
            except:
                continue
        return acceleration

    def check_collision(self,body):
        displacement = Vec3(self.position-body.position)
        distance = math.sqrt(dot_product(displacement,displacement))
        if distance <= (self.diameter+body.diameter)/2:
            return True
        else:
            return False

    def get_collision_velocity(self,body):
        # Find the *change* in the body's velocity due to a collision with another body.
        mass_fraction = -2*body.mass/(self.mass+body.mass)
        relative_velocity = Vec3(self.velocity-body.velocity)
        displacement = Vec3(self.position-body.position)
        distance = math.sqrt(dot_product(displacement,displacement))
        collision_multiplier = mass_fraction*dot_product(relative_velocity,displacement)/(distance**2)
        delta_v = Vec3(displacement*collision_multiplier)
        return delta_v

def dot_product(vect1,vect2):
    return vect1[0]*vect2[0]+vect1[1]*vect2[1]+vect1[2]*vect2[2]

def do_collisions(bodies):
    # Gets each body to check for collisions and run their collision methods. Return a list of the new velocities.
    new_velocities = []
    for body1 in bodies:
        delta_v = Vec3(0,0,0)
        for body2 in bodies:
            if body1 == body2:
                continue
            if body1.check_collision(body2):
                delta_v += body1.get_collision_velocity(body2)
        new_vel = body1.velocity+delta_v
        new_velocities.append(new_vel)
    return new_velocities

def update():
    # Main loop - runs continuously
    if simulating:
        global bodies
        new_states= []
        for body in bodies: # Calculate next states for each body due to gravitational effects, then apply them.
            new_acc = body.change_acceleration()
            new_vel = body.change_velocity()
            new_pos = body.change_position()
            new_states.append((new_pos,new_vel,new_acc))
        for i in range(len(bodies)):
            body = bodies[i]
            new_state = new_states[i]
            body.position = new_state[0]
            body.velocity = new_state[1]
            body.acceleration = new_state[2]

        new_velocities = do_collisions(bodies) # Handle collisions
        for i in range(len(bodies)):
            body = bodies[i]
            new_vel = new_velocities[i]
            body.velocity = new_vel

def input(key):
    # This function runs continuously and handles user input not relating to a specific object
    global simulating
    if key == "escape": # Pause both simulation and camera. Also unlocks the mouse.
        if mouse.locked:
            mouse.locked = False
            window.exit_button.visible = True
            simulating = False
        else:
            mouse.locked = True
            window.exit_button.visible = False
            simulating = True
    if key == "p": # Pause/unpause simulation, but not the camera
        if simulating:
            simulating = False
        else:
            simulating = True


# All physical bodies are stored in a "bodies" list so they can easily access each other's data
bodies = []
# Initial Conditions
bodies.append(Body(mass=10,position=(0,0,80),velocity=(-100,20,0)))
bodies.append(Body(mass=10000))
bodies.append(Body(mass=500,position=(0,-40,0),velocity=(150,0,0)))
bodies.append(Body(mass=20,position=(0,40,0),velocity=(0,-10,0)))

# Propogate velocities backwards by half a step for the Leapfrog Method
for body in bodies:
    body.acceleration = body.change_acceleration()
    delta_v = Vec3(body.acceleration*time_interval/2)
    body.velocity = Vec3(body.velocity-delta_v)

Spectator(speed=40)
app.run()
