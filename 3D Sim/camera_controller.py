from ursina import *

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
