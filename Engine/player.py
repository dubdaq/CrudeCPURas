import numpy, math
from Engine.camera import Camera
from Engine.viewport import Viewport
from utility import vec2, vec3

class Player:
    def __init__(self, screen, viewSize : vec2, gridSize : int, initialPosition : vec3, theta, psi, speed : float, zNear = 0.1, zFar = 20, hfov = math.radians(90), vfov = math.radians(60)):
        self.speed = speed

        self.position = initialPosition
        self.displacementVector = vec3(0, 0, 0)
        self.dTheta = 0
        self.dPsi = 0
        self.theta = theta
        self.psi = psi

        self.idle = False

        self.viewport = Viewport(viewSize, gridSize, screen)
        self.camera = Camera(initialPosition, self.theta, self.psi, zNear, zFar, hfov, vfov)

    def move(self, dTheta, dPsi, displacementVector):
        self.dPsi = dPsi
        self.dTheta = dTheta
        self.displacementVector = displacementVector

        self.camera.position.x += self.displacementVector.x
        self.camera.position.z += self.displacementVector.z
        self.camera.position.y += self.displacementVector.y
        self.theta += self.dTheta
        self.psi += self.dPsi

        self.camera.move(self.position, self.theta, self.psi)
    
    def interpolate(self, interpolation):
        self.move(self.dTheta*interpolation, self.dPsi * interpolation, self.displacementVector * interpolation)

    #Rendering stuff
    def render(self, objects, lights):
        self.camera.rasterizeTriangles(self.viewport, objects, lights) 

        for tilePosition, (ndcY, ndcX, xMin, yMin, xMax, yMax) in self.viewport.tileGrid.items():
            for triangle in self.viewport.tiles[tilePosition]:
                A, B, C = triangle['edge functions']
    
                #computing all alpha, betas and gammas for all pixels
                alpha = A[0]*ndcX + A[1]*ndcY + A[2]
                beta  = B[0]*ndcX + B[1]*ndcY + B[2]
                gamma = C[0]*ndcX + C[1]*ndcY + C[2]
    
                #computing whether the pixel lies inside the triangle for all pixels
                inside = (alpha >= 0) & (beta > 0) & (gamma > 0) 
    
                #computing all zVals
                wSum = alpha + beta + gamma
                zVal = numpy.full_like(wSum, self.camera.zFar)
                numpy.divide(
                    #we need to use the vertex opposite the side calculated
                    alpha*triangle['triangle'][2][3] + beta*triangle['triangle'][0][3] + gamma*triangle['triangle'][1][3],
                    wSum,
                    out=zVal,
                    where=inside
                )
    
                zBufferSlice = self.viewport.zBuffer[xMin : xMax, yMin: yMax]
                closer = inside & (zVal < zBufferSlice) & (zVal < self.camera.zFar)
                zBufferSlice[closer] = zVal[closer]
                self.viewport.pixelBuffer[xMin: xMax, yMin: yMax][closer] = triangle['color']
    
        self.viewport.set() 
