import pygame, math, sys, random
from pygame.locals import *

window_size = (600, 600)
MAXIMUM_TICK_SPEED = 240
time_interval = 1/MAXIMUM_TICK_SPEED
GRAVITATIONAL_CONSTANT = 6.67*10
DRAW_SCALE_FACTOR = 20
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
bodies = []
SIMULATING = False

class Body:

    def __init__(self, mass = 0.0, position = None, velocity = None, acceleration = None):
        self.mass = mass
        self.position = position if position != None else (0,0)
        self.velocity = velocity if velocity != None else (0,0)
        self.acceleration = acceleration if acceleration != None else (0,0)
        self.radius = int(10*math.log(mass,10))

    def change_position(self):
        displacement = scalar_multiply(time_interval,self.velocity)
        return vector_add(self.position,displacement)

    def change_velocity(self):
        delta_v = scalar_multiply(time_interval,self.acceleration)
        return vector_add(self.velocity,delta_v)

    def change_acceleration(self):
        acceleration = (0,0)
        for body in bodies:
            try:
                displacement = vector_subtract(self.position,body.position)
                distance = math.sqrt(dot_product(displacement,displacement))
                delta_a = scalar_multiply(-1*GRAVITATIONAL_CONSTANT*body.mass/(distance**3),displacement)
                acceleration = vector_add(acceleration,delta_a)
            except:
                continue
        return acceleration

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.position[0]),int(self.position[1])), self.radius)

    def draw_downscaled(self):
        x = self.position[0]-int(window_size[0]/2)
        y = self.position[1]-int(window_size[0]/2)
        r = math.sqrt(dot_product((x,y),(x,y)))
        theta = math.atan2(y,x)
        if r > 1:
            new_r = math.log(r,10)*DRAW_SCALE_FACTOR
        else:
            new_r = r
        new_x = int(new_r*math.cos(theta)+int(window_size[0]/2))
        new_y = int(new_r*math.sin(theta)+int(window_size[0]/2))
        pygame.draw.circle(screen, BLUE, (new_x,new_y), int(math.log(self.mass,10)))


def terminate():
    pygame.quit()
    sys.exit()

def dot_product(vect1,vect2):
    return vect1[0]*vect2[0]+vect1[1]*vect2[1]

def vector_add(vect1,vect2):
    return (vect1[0]+vect2[0],vect1[1]+vect2[1])

def vector_subtract(vect1,vect2):
    return (vect1[0]-vect2[0],vect1[1]-vect2[1])

def scalar_multiply(scalar,vect):
    return (scalar*vect[0],scalar*vect[1])

def check_for_collision(body1, body2):
    displacement = vector_subtract(body1.position,body2.position)
    distance = math.sqrt(dot_product(displacement,displacement))
    if distance <= body1.radius+body2.radius:
        return True
    else:
        return False

def get_collision_velocity(body1,body2):
    mass_fraction = -2*body2.mass/(body1.mass+body2.mass)
    relative_velocity = vector_subtract(body1.velocity,body2.velocity)
    displacement = vector_subtract(body1.position,body2.position)
    distance = math.sqrt(dot_product(displacement,displacement))
    displacement_multiplier = mass_fraction*dot_product(relative_velocity,displacement)/(distance**2)
    delta_v = scalar_multiply(displacement_multiplier,displacement)
    return delta_v

def do_collisions(bodies):
    new_bodies = []
    for body1 in bodies:
        change_in_velocity = (0,0)
        for body2 in bodies:
            if body1==body2:
                continue
            if check_for_collision(body1,body2):
                change_in_velocity = vector_add(change_in_velocity,get_collision_velocity(body1,body2))
        new_vel = vector_add(body1.velocity,change_in_velocity)
        new_body = Body(body1.mass,body1.position,new_vel,body1.acceleration)
        new_bodies.append(new_body)
    return new_bodies


pygame.init()
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Orbit Simulator")
clock = pygame.time.Clock()

bodies.append(Body(10000,(100,300),(0,-20)))
bodies.append(Body(10000,(500,300),(0,20)))
bodies.append(Body(10000,(300,100),(20,0)))
bodies.append(Body(10000,(300,500),(-20,0)))

"""bodies.append(Body(10,(300,200),(81.670,0)))
bodies.append(Body(10000,(300,300),(0,0)))"""

"""for i in range(5):
    for j in range(5):
        bodies.append(Body(10,(100+100*i+random.randint(-50,50),100+100*j+random.randint(-50,50))))"""

#Propogate velocities backwards by half a step for the Leapfrog Method
for body in bodies:
    body.acceleration = body.change_acceleration()
    delta_v = scalar_multiply(time_interval/2,body.acceleration)
    body.velocity = vector_subtract(body.velocity,delta_v)

while True:
    if SIMULATING:
        new_bodies = []
        for body in bodies:
            new_acc = body.change_acceleration()
            new_vel = body.change_velocity()
            new_pos = body.change_position()
            new_body = Body(body.mass,new_pos,new_vel,new_acc)
            new_bodies.append(new_body)
        bodies = new_bodies
        bodies = do_collisions(bodies)

    screen.fill(WHITE)
    for body in bodies:
        body.draw()
    for body in bodies:
        body.draw_downscaled()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if event.type == KEYDOWN:
            if event.key == pygame.K_p:
                if SIMULATING:
                    SIMULATING = False
                else:
                    SIMULATING = True
    clock.tick(MAXIMUM_TICK_SPEED)
