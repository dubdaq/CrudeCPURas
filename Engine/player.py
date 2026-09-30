import numpy, math
from Engine.camera import Camera
from Engine.viewport import Viewport
from Engine.movement import movement
from utility import vec2, vec3

from numba import njit

colors = [
    (45, 40, 151),
    (122, 35, 35),
    (211, 177, 40),
    (32, 138, 72),
    (169, 47, 169),
    (100, 100, 100)
]

@njit
def fastCompute(x0, y0, ndcX, ndcY, A, B, C, z0, z1, z2):
    alpha = A[0]*(ndcX + x0) + A[1]*(ndcY + y0) + A[2]
    beta  = B[0]*(ndcX + x0) + B[1]*(ndcY + y0) + B[2]
    gamma = C[0]*(ndcX + x0) + C[1]*(ndcY + y0) + C[2]

    #computing whether the pixel lies inside the triangle for all pixels
    inside = (alpha >= 0) & (beta > 0) & (gamma > 0) 
    #computing all zVals
    wSum = alpha + beta + gamma 
    
    #we need to use the vertex opposite the side calculated
    zVal = (alpha*z2 + beta*z0 + gamma*z1)/wSum

    return zVal, inside


class Player:
    def __init__(self, screen, viewSize : vec2, gridSize : int, initialPosition : vec3, theta, psi, speed : float, zNear = 0.1, zFar = 20, hfov = math.radians(90), vfov = math.radians(60)):
        self.movement = movement(initialPosition, theta, psi, speed)
        self.viewport = Viewport(viewSize, gridSize, screen)
        self.camera = Camera(self.movement, zNear, zFar, hfov, vfov)

    #Rendering stuff

    def render(self, scene, lights):
        self.camera.rasterizeTriangles(self.viewport, scene, lights, self.movement.idle) 

        ndcY, ndcX = self.viewport.tileGrid
        zVal = numpy.full_like(ndcX, self.camera.zFar)

        for tilePosition, data in self.viewport.tiles.items():
            w, h = 2*self.viewport.tileSize/self.viewport.width, 2*self.viewport.tileSize/self.viewport.height
            
            row, col = tilePosition
            xMin, yMin = col *self.viewport.tileSize, row *self.viewport.tileSize
            xMax, yMax = xMin+self.viewport.tileSize, yMin+self.viewport.tileSize
        
            y0, x0 = 2*yMin/self.viewport.height - 1, 2*xMin/self.viewport.width - 1
            offsets = [(x0, y0), (x0+w, y0), (x0, y0+h)]


            for index in range(len(data['triangles'])):
                A, B, C = data['edge functions'][index]
                triangle = data['triangles'][index]

                if not data['coverage'][index]:
                    zVal, inside = fastCompute(x0, y0, ndcX, ndcY, A, B, C, 
                                               triangle[0][3], triangle[1][3], triangle[2][3])

                    #njit dont support array slicing like this
                    zBufferSlice = self.viewport.zBuffer[xMin : xMax, yMin: yMax]
                    closer = inside & (zVal < zBufferSlice) & (zVal < self.camera.zFar)
                    
                    zBufferSlice[closer] = zVal[closer]
                    self.viewport.pixelBuffer[xMin: xMax, yMin: yMax][closer] = data['colors'][index]
                
                else:
                    zInvs = []
                    for nX, nY in offsets:
                        alpha = A[0]*nX + A[1]*nY + A[2]
                        beta  = B[0]*nX + B[1]*nY + B[2]
                        gamma = C[0]*nX + C[1]*nY + C[2]
                        zInvs.append((alpha+beta+gamma)/(alpha*triangle[2][3] + beta*triangle[0][3] + gamma*triangle[1][3]))

                    tx, ty = ndcX/w, ndcY/h
                    zInv = zInvs[0] + tx*(zInvs[1]-zInvs[0]) + ty*(zInvs[2]-zInvs[0])
                    zVal = 1.0 / zInv

                    zBufferSlice = self.viewport.zBuffer[xMin : xMax, yMin: yMax]
                    closer = (zVal < zBufferSlice) & (zVal < self.camera.zFar)
                    zBufferSlice[closer] = zVal[closer]
                    self.viewport.pixelBuffer[xMin: xMax, yMin: yMax][closer] = data['colors'][index]
        self.viewport.set() 
