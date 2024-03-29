from ursina import *
from camera_controller import Spectator
from body_controller import Body, TIME_INTERVAL
import numpy as np

simulating = False  # Global variable used to pause/unpause the simulator

bodies = []     # All physical bodies are stored in a "bodies" list so they can easily access each other's data
                # If a body is not added to this list, the simulator will ignore it

def do_collisions(bodies):
    # Gets each body to check for collisions and run their collision methods.
    # Then returns a list of the new velocities
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

def calculate_net_acceleration(body):
    new_acceleration = Vec3(0,0,0)
    for body2 in bodies:
        if body2 == body:
            continue
        else:
            new_acceleration += body.get_new_acceleration(body2)
    return new_acceleration

def update():
    # Main loop - runs continuously
    if simulating:
        global bodies
        new_states= []
        for body in bodies: # Calculate next states for each body due to gravitational effects, then apply them.
            new_acc = calculate_net_acceleration(body)
            new_vel = body.get_new_velocity()
            new_pos = body.get_new_position()
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
            simulating = False
        else:
            mouse.locked = True
            simulating = True
    if key == "p": # Pause/unpause simulation, but not the camera
        if simulating:
            simulating = False
        else:
            simulating = True

if __name__ == "__main__":
    app = Ursina()
    window.title = "3D Orbital Simulator"
    window.borderless = False
    window.fullscreen = False
    window.forced_aspect_ratio = 19/10
    window.exit_button.visible = False
    window.fps_counter.enabled = True
    window.vsync = True

    # Initial Conditions
    bodies.append(Body(mass=10,position=(0,0,80),velocity=(-100,20,0)))
    bodies.append(Body(mass=10000))
    bodies.append(Body(mass=500,position=(0,-40,0),velocity=(150,0,0)))
    bodies.append(Body(mass=20,position=(0,40,0),velocity=(0,-10,0)))
    for i in range(100):
        bodies.append(Body(mass=10,position=(50*i+50,0,0)))

    # Propogate velocities backwards by half a step for the Leapfrog Method
    for body in bodies:
        body.acceleration = calculate_net_acceleration(body)
        delta_v = Vec3(body.acceleration*TIME_INTERVAL/2)
        body.velocity = Vec3(body.velocity-delta_v)

    Spectator(speed=40)
    app.run()
