import numpy, math
from utility import normal, vec3, normalize

class DirectionalLight:
    def __init__(self, direction : vec3, color = (255, 255, 255)):
        self.direction = normalize(direction)
        self.color = numpy.array(color)

class Object:
    renderList = []
    def __init__(self, verticies, triangles, position = (0, 0, 0), smooth = False, inside = True):
        self.verticies = numpy.array(verticies, dtype = numpy.float32)
        self.triangles = triangles
        self.position = numpy.array([0.0, 0.0, 0.0])
        self.move(*position)

        self.theta = 0
        self.psi = 0

        self.normals = []

        for a, b, c in self.triangles:
            self.normals.append(normal(self.verticies[a], self.verticies[b], self.verticies[c]))

        self.normals = numpy.array(self.normals)
        self.inside = inside

    def move(self, Tx, Ty, Tz):
        self.verticies += numpy.array([Tx, Ty, Tz])
        self.position += numpy.array([Tx, Ty, Tz])

    #yaw then pitch rotation.
    def yawPitchRotation(self, theta, psi):
        cTheta, sTheta = math.cos(theta), math.sin(theta)
        cPsi, sPsi = math.cos(psi), math.sin(psi)
        R = numpy.array(
                    [
                        [cTheta,        0,     -sTheta],
                        [sPsi*sTheta,   cPsi,   sPsi*cTheta],
                        [cPsi*sTheta,  -sPsi,   cPsi*cTheta],
                    ]
                )
        self.verticies = (self.verticies - self.position) @ R + self.position
        self.normals = self.normals @ R
        self.theta += theta
        self.psi += psi

    def scale(self, factor):
        self.verticies = numpy.array([[factor*i for i in vertex] for vertex in self.verticies])

    def render(self):
        Object.renderList.append(self)

    @staticmethod
    def loadMesh(filePath, position):
        verts, triangles = [], []
        with open(filePath, "r") as file:
            for line in file.readlines():
                if "v " in line :
                    x, y, z = [float(i) for i in line[1:].split()]
                    verts.append([x, y, z])
                if "f " in line :
                    triangles.append([int(i.split("/")[0])-1 for i in line[1:].split()])
        return Object(verts, triangles, position)
