import numpy, math
from config import aspect
from utility import vec3

def lerp(A, B, t):
    lerpedVals = [ A[i] + (B[i] - A[i]) * t for i in range(4)]
    return lerpedVals 

def fanTriangulate(polygonVertices):
    polygonVertices = list(polygonVertices)
    size = len(polygonVertices)
    triangles = []
    for index in range(0, size - 2):
        triangles.append([polygonVertices[0], polygonVertices[(index + 1) % size], polygonVertices[(index + 2) % size]])
    return triangles

#Clipping only for near plane. Sutherland-Hodgeman Implementation
def clippedTriangle(polygonVerts, zNear):
    for i in range(len(polygonVerts)):
        currentPoint = polygonVerts[i]
        prevPoint = polygonVerts[(i-1) % len(polygonVerts)]

        #We interpolate instead of considering the actual intersection
        d1, d2 = currentPoint[2] + zNear, prevPoint[2] + zNear

        if currentPoint[2] + zNear >= 0:
            if prevPoint[2] + zNear < 0:
                yield lerp(currentPoint, prevPoint, d1 / (d1 - d2))
            yield currentPoint

        elif prevPoint[2] + zNear >= 0:
            yield lerp(currentPoint, prevPoint, d1 / (d1 - d2))

def signedArea(triangle):    
    a, b, c, x, y, z, p, q, r = triangle.ravel()
    #The factors used with a,b,c in this calculation would be our edge function values
    #its a pretty simple idea, using signedArea to find out which side of the line and point lies.
    return 0.5 * (a*(y*r - z*q) + b*(z*p - r*x) + c*(x*q-p*y))

def signedAreaCoeffs(P0, P1):
    A = P0[1]*P1[2] - P1[1]*P0[2]   # y0*w1 - y1*w0
    B = P1[0]*P0[2] - P0[0]*P1[2]   # x1*w0 - x0*w1
    C = P0[0]*P1[1] - P1[0]*P0[1]   # x0*y1 - x1*y0
    return A, B, C 

def edgeFunction(triangle):
    newTri = numpy.delete(triangle, 2, 1)

    P0, P1, P2 = newTri
    e0 = signedAreaCoeffs(P1, P2)  # opposite P0
    e1 = signedAreaCoeffs(P2, P0)  # opposite P1
    e2 = signedAreaCoeffs(P0, P1)  # opposite P2
    return e0, e1, e2

class Camera:
    def __init__(self, initialPosition : vec3, theta, psi, zNear, zFar, hfov, vfov):
        self.position = initialPosition
        self.theta = theta
        self.psi = psi

        self.zNear = zNear
        self.zFar = zFar

        self.hfov = hfov
        self.vfov = vfov
        
        fx = 1/math.tan(self.hfov/2)
        fy = aspect * fx 
        a, b = (self.zFar + self.zNear)/(self.zFar - self.zNear), -(2*self.zFar*self.zNear)/(self.zFar - self.zNear)

        self.projectionMatrix = numpy.array([
            [fx,  0, 0, 0], 
            [ 0, -fy, 0, 0], 
            [ 0,  0, a, 1], 
            [ 0,  0, b, 0]])

    def move(self, position : vec3, theta, psi):
        self.position = position
        self.theta = theta
        self.psi = psi

    def camTransform(self):
        cTheta, sTheta = math.cos(self.theta), math.sin(self.theta)
        cPsi, sPsi = math.cos(self.psi), math.sin(self.psi)
        tx, ty, tz = self.position

        R = numpy.array(
            [
                [ cTheta, sPsi*sTheta, cPsi*sTheta, 0],
                [ 0     , cPsi       , -sPsi      , 0],
                [-sTheta, sPsi*cTheta, cPsi*cTheta, 0],
                [ 0     , 0          , 0          , 1],
            ]
        )

        Tinv = numpy.array(
            [
                [  1,   0,   0, 0],
                [  0,   1,   0, 0],
                [  0,   0,   1, 0],
                [-tx, -ty, -tz, 1]
            ]
        )
        viewMatrix = Tinv @ R

        return viewMatrix @ self.projectionMatrix

    def viewMatrix(self):
        cTheta, sTheta = math.cos(self.theta), math.sin(self.theta)
        cPsi, sPsi = math.cos(self.psi), math.sin(self.psi)
        tx, ty, tz = self.position

        R = numpy.array(
            [
                [ cTheta, sPsi*sTheta, cPsi*sTheta, 0],
                [ 0     , cPsi       , -sPsi      , 0],
                [-sTheta, sPsi*cTheta, cPsi*cTheta, 0],
                [ 0     , 0          , 0          , 1],
            ]
        )

        Tinv = numpy.array(
            [
                [  1,   0,   0, 0],
                [  0,   1,   0, 0],
                [  0,   0,   1, 0],
                [-tx, -ty, -tz, 1]
            ]
        )

        return Tinv @ R

    def rasterizeTriangles(self, viewport, objects, lights):
        for object in objects:
            vertsInWorld = numpy.hstack((object.verticies, numpy.ones((len(object.verticies), 1))))
            clipVerts = vertsInWorld @ self.camTransform()
            clipTriangles = clipVerts[object.triangles]

            for clipTriangle, triangleNormal in zip(clipTriangles, object.normals):
                finalTriangles = [clipTriangle]
                isBehind = [P[2] + self.zNear < 0 for P in clipTriangle]

                if all(isBehind):
                    continue

                if any(isBehind) and not all(isBehind):
                    finalTriangles = fanTriangulate(clippedTriangle(clipTriangle, self.zNear))

                if not object.cull:
                    finalTriangles.extend([triangle[::-1] for triangle in finalTriangles])

                for finalTriangle in finalTriangles:
                    if signedArea(numpy.delete(finalTriangle, 2, 1)) < 0.0001:
                        continue

                    edgeFuncs = edgeFunction(finalTriangle)
                    color = numpy.array([0, 0, 0])

                    for light in lights:    
                        lightIntensity = 0.5 * (numpy.dot(triangleNormal, light.direction) + 1) if isinstance(triangleNormal, numpy.ndarray) else 0
                        color = light.color * lightIntensity

                    viewport.tileTriangle(finalTriangle, color, edgeFuncs)

