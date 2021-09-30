from ursina import *
import math

GRAVITATIONAL_STRENGTH = 6.67*10
ELECTRIC_STRENGTH = 8.854*(10**6)
MAGNETIC_STRENGTH = 4*math.pi*(10**11)
TIME_INTERVAL = 0.001       # Time interval used for each simulation step

bodies = []     # All physical bodies are stored in a "bodies" list so they can easily access each other's data
                # If a body is not added to this list, the simulator will ignore it

class Body(Entity):
# This class is used for physical bodies within the simulator.
    def __init__(self, mass = 0.0, charge = 0.0, position = None, velocity = None, acceleration = None, colour = None):
        super().__init__(model="sphere")
        self.mass = mass
        self.charge = charge
        self.position = Vec3(position) if position != None else Vec3(0,0,0)
        self.velocity = Vec3(velocity) if velocity != None else Vec3(0,0,0)
        self.acceleration = Vec3(acceleration) if acceleration != None else Vec3(0,0,0)
        self.diameter = 10*math.log(mass,10)
        self.scale = (self.diameter,self.diameter,self.diameter)
        self.color = colour if colour != None else color.random_color()

    def change_position(self):
        return Vec3(self.position+self.velocity*TIME_INTERVAL)

    def change_velocity(self):
        return Vec3(self.velocity+self.acceleration*TIME_INTERVAL)

    def change_acceleration(self):
        acceleration = Vec3(0,0,0)
        for body in bodies: # Calculate net gravitational acceleration of the body due to each other body
            gravity = self.do_gravity(body)
            acceleration = Vec3(acceleration+gravity)
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

    def do_gravity(self,body):
        try:
            displacement = Vec3(self.position-body.position)
            distance = math.sqrt(dot_product(displacement,displacement))
            gravitational_field = Vec3(-1*displacement*GRAVITATIONAL_STRENGTH*body.mass/(distance**3))
            return gravitational_field
        except:
            return Vec3(0,0,0)

    def do_electromagnetism(self,body):
        try:
            displacement = Vec3(self.position-body.position)
            distance = math.sqrt(dot_product(displacement,displacement))
        except:
            return Vec3(0,0,0)

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