#movement handler
from utility import vec3, normalize
from config import mouseSensitivity, updatesPerSecond
import pygame, math

class movement:
    def __init__(self, initialPosition, theta, psi, speed):
        self.position = initialPosition
        self.theta = theta
        self.psi = psi
        self.speed = speed

        self.position = initialPosition
        self.displacementVector = vec3(0, 0, 0)
        self.dTheta = 0
        self.dPsi = 0
        self.theta = theta
        self.psi = psi

        self.idle = True

    def move(self, dTheta, dPsi, displacementVector : vec3):
        self.dPsi = dPsi
        self.dTheta = dTheta
        self.displacementVector = displacementVector
                
        self.theta += self.dTheta
        self.psi += self.dPsi
        self.position += self.displacementVector
    
    def interpolate(self, interpolation):
        self.move(self.dTheta*interpolation, self.dPsi * interpolation, self.displacementVector * interpolation)

    def update(self):
        keysHeld = pygame.key.get_pressed()
        theta, psi = 0, 0
        if keysHeld[pygame.K_UP]:
            psi -= mouseSensitivity * math.pi/updatesPerSecond
        if keysHeld[pygame.K_DOWN]:
            psi += mouseSensitivity * math.pi/updatesPerSecond
        if keysHeld[pygame.K_LEFT]:
            theta -= mouseSensitivity * math.pi/updatesPerSecond
        if keysHeld[pygame.K_RIGHT]:
            theta += mouseSensitivity * math.pi/updatesPerSecond

        dx, dy, dz = 0, 0, 0
        if keysHeld[pygame.K_w]: 
            dz += self.speed 
        if keysHeld[pygame.K_s]: 
            dz -= self.speed 
        if keysHeld[pygame.K_a]: 
            dx += self.speed 
        if keysHeld[pygame.K_d]: 
            dx -= self.speed

        if keysHeld[pygame.K_SPACE]:
            dy -= self.speed

        if (theta or psi or dx or dz or dy):
            self.idle = False
            
            parallel = normalize([math.sin(self.theta + theta), -math.sin(self.psi + psi), math.cos(self.theta + theta)])
            normal = [-parallel[2], 0, parallel[0]]
            diagVector = normalize([dx, dy, dz], self.speed)
            if diagVector == None:
                diagVector = [0, 0, 0]

            displacementVector = vec3(normal[0] * diagVector[0] + normal[2] * diagVector[2], parallel[1] * diagVector[2] + diagVector[1], parallel[0] * diagVector[0] + parallel[2] * diagVector[2])

            self.move(theta, psi, displacementVector)
        else : self.idle = True
