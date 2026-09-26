import pygame, numpy, math
from utility import vec3, vec2

def linearClip(A, B, zNear):
    dA, dB = A[3] - zNear, B[3] - zNear
    if dA >= 0 and dB >= 0:
        return A, B         
    if dA < 0 and dB < 0:
        return None          
    t = dA / (dA - dB)
    intersection = A + t * (B - A)
    return (intersection, B) if dA < 0 else (A, intersection)

def dist(A : vec2, B : vec2):
    return math.sqrt((A.x - B.x)**2 + (A.y - B.y)**2)

class Gizmo (pygame.Surface):
    def __init__(self, screen, camera, viewport : pygame.Surface):
        super().__init__((viewport.width, viewport.height), pygame.SRCALPHA)
        self.camera = camera
        self.viewport = viewport
        self.screen = screen

    def clear(self):
        self.fill((0, 0, 0, 0))
        x,y = self.screen.width//2, self.screen.height//2
        self.screen.blit(self, (x - self.width // 2, y - self.height // 2))

    def setPixel(self, pixelX, pixelY):
        #print(pixelX, pixelY)
        self.set_at((pixelX, pixelY), (0, 255, 0, 255))

        x,y = self.screen.width//2, self.screen.height//2
        self.screen.blit(self, (x - self.width // 2, y - self.height // 2))

    #Bresenham line algorithm stolen from glorious wikipedia
    def pixelLine(self, pixelA : vec2, pixelB : vec2, color = (255, 0, 0, 255)):
        dx, dy = abs(int(pixelB.x - pixelA.x)), -1 * abs(int(pixelB.y - pixelA.y))
        sx = 1 if pixelA.x < pixelB.x else -1
        sy = 1 if pixelA.y < pixelB.y else -1

        error = dx + dy

        while True:
            self.set_at(list(pixelA), color)
            e2 = 2 * error
            if e2 >= dy:
                if pixelA.x == pixelB.x:
                    break
                error += dy
                pixelA.x += sx
            if e2 <= dx:
                if pixelA.y == pixelB.y:
                    break
                error += dx
                pixelA.y += sy

    def drawLine(self, worldA : vec3, worldB : vec3, color = (255, 0, 0, 255)):
        clipA, clipB = numpy.array(worldA.hmg) @ self.camera.camTransform(), numpy.array(worldB.hmg) @ self.camera.camTransform()
        linClip = linearClip(clipA, clipB, self.camera.zNear)
        if not linClip : return
        clipA, clipB = linClip

        pixelA = vec3(int(self.width * 0.5 * (clipA[0]/clipA[3] + 1)), int(self.height * 0.5 * (clipA[1]/clipA[3] + 1)), clipA[3])
        pixelB = vec3(int(self.width * 0.5 * (clipB[0]/clipB[3] + 1)), int(self.height * 0.5 * (clipB[1]/clipB[3] + 1)), clipB[3])
        ABDist = dist(pixelA, pixelB)
        if ABDist == 0: return

        dx, dy = abs(int(pixelB.x - pixelA.x)), -1 * abs(int(pixelB.y - pixelA.y))
        sx = 1 if pixelA.x < pixelB.x else -1
        sy = 1 if pixelA.y < pixelB.y else -1

        error = dx + dy
        currentPixel = vec2(pixelA.x, pixelA.y)

        while True:
            t = dist(currentPixel, pixelA) / ABDist
            zVal = pixelA.z + t * (pixelB.z - pixelA.z)

            if (currentPixel.y >= 0 and currentPixel.y < self.viewport.height) and currentPixel.x >= 0 and currentPixel.x < self.viewport.width:
                if self.viewport.zBuffer[currentPixel.x][currentPixel.y] > zVal:
                    self.viewport.zBuffer[currentPixel.x][currentPixel.y] = zVal
                    self.set_at(list(currentPixel), color)
                
            e2 = 2 * error
            if e2 >= dy:
                if currentPixel.x == pixelB.x:
                    break
                error += dy
                currentPixel.x += sx
            if e2 <= dx:
                if currentPixel.y == pixelB.y:
                    break
                error += dx
                currentPixel.y += sy

    def set(self):
        x,y = self.screen.width//2, self.screen.height//2
        self.screen.blit(self, (x - self.width // 2, y - self.height // 2))