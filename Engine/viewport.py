import pygame, numpy, math
from utility import vec2, clamp

# # Approach abandoned after the MIT Rasterization Guide recommended different approach (see comment above tileTriangle)
# # #Separated Axis Theorem, thanks the almight youtube alg for recommending the video.
# def overlap(triangle : list[vec2, vec2, vec2], rect : list[vec2, vec2, vec2, vec2]):
#     A, B, C = triangle
#     P, Q, R, S = rect
#     #check if one shape enclose other
#     xAxis = vec2(1, 0)
#     projTri = [xAxis.dot(P) for P in triangle]
#     projRect = [xAxis.dot(P) for P in rect]
#     triA, triB = min(projTri), max(projTri)
#     rectA, rectB = min(projRect), max(projRect)

#     if ((rectA <= triA and rectB >= triB) or (rectA >= triA and rectB <= triB)):
#         return (True, True)

#     normals = [(C-B).normal(), (A-C).normal(), (B-A).normal(), (Q-P).normal(), (R-Q).normal(), (S-R).normal(), (P-S).normal()]
#     normals = set(normals)

#     for normal in normals:
#         projTri = [normal.dot(P) for P in triangle]
#         projRect = [normal.dot(P) for P in rect]
#         triA, triB = min(projTri), max(projTri)
#         rectA, rectB = min(projRect), max(projRect)

#         if (triB >= rectA and rectB >= triA) :
#             continue
#         return (False, False)
#     return (True, False)
class Viewport (pygame.Surface):
    def __init__(self, size : vec2, tileSize, screen : pygame.Surface):
        super().__init__((size.x, size.y))

        self.zBuffer = numpy.full((size.x, size.y), math.inf) # contains columns not rows to be more like surfarray [col][row]

        self.tileSize = tileSize
        self.tilesInWidth = size.x // tileSize 
        self.tilesInHeight = size.y // tileSize

        #stores which triangle lie in the tile
        self.tiles = dict([((y, x),[]) for y in range(self.tilesInHeight) for x in range(self.tilesInWidth)])

        #stores the structure of the grid.
        self.tileGrid = dict()
        for row, col in self.tiles.keys():
            xMin, yMin = col*self.tileSize, row*self.tileSize
            xMax, yMax = xMin+self.tileSize, yMin+self.tileSize
            ndcY, ndcX = numpy.meshgrid(
                numpy.linspace(2*yMin/self.height - 1, 2*yMax/self.height - 1, num = self.tileSize),
                numpy.linspace(2*xMin/self.width - 1, 2*xMax/self.width - 1, num = self.tileSize)
            )
            self.tileGrid[(row, col)] = (ndcY, ndcX, xMin, yMin, xMax, yMax)

        self.pixelBuffer = numpy.full((size.x, size.y, 3), 35, dtype = numpy.uint8)
        self.screen = screen

    #https://fileadmin.cs.lth.se/graphics/research/papers/2005/cr/conservative.pdf
    def tileTriangle(self, triangle, color, edgeFuncs):
        ndcXs = [(self.tilesInWidth) * (P[0]/P[3] + 1)/2 for P in triangle]
        ndcYs = [(self.tilesInHeight) * (P[1]/P[3] + 1)/2 for P in triangle]
        xMax, xMin = clamp(math.ceil(max(ndcXs)), 0, self.tilesInWidth), clamp(math.floor(min(ndcXs)), 0, self.tilesInWidth)
        yMax, yMin = clamp(math.ceil(max(ndcYs)), 0, self.tilesInHeight), clamp(math.floor(min(ndcYs)), 0, self.tilesInHeight)
        
        p, q, r = [vec2(P[0]/P[3], P[1]/P[3]) for P in triangle]
        edgeNormals = [(q-p).normal(), (r-q).normal(), (p-r).normal()]
        offsets = [vec2(2*self.tileSize/self.width if normal.x >= 0 else 0, 2*self.tileSize/self.height if normal.y >= 0 else 0) for normal in edgeNormals]
    
        for row in range(yMin, yMax):
            for col in range(xMin, xMax):
                rejected = False
                s = vec2(2 * (col * self.tileSize) / self.width - 1, 2 * (row * self.tileSize) / self.height - 1)
                for e, t in zip(edgeFuncs, offsets): 
                    eSum = e[0]*(s.x + t.x) + e[1]*(s.y + t.y) + e[2]
                    if eSum <= 0:
                        rejected = True
                        break
                if not rejected:
                    self.tiles[(row, col)].append({
                        'triangle' : triangle,
                        'color' : color,
                        'edge functions' : edgeFuncs,
                    })

    def set(self):
        pygame.surfarray.blit_array(self, self.pixelBuffer)
        x,y = self.screen.width//2, self.screen.height//2
        self.screen.blit(self, (x - self.width // 2, y - self.height // 2))
                
    def flush(self):
        #We have the seperate tile entity so that we dont need to keep rebuilting grid everyframe.
        for tileList in self.tiles.values():
            tileList.clear()        
        self.zBuffer.fill(math.inf)
        self.pixelBuffer.fill(35)
