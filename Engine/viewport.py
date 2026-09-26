import pygame, numpy, math
from utility import vec2, clamp

#Separated Axis Theorem, thanks the almight youtube alg for recommending the video.
def overlap(triangle : list[vec2, vec2, vec2], rect : list[vec2, vec2, vec2, vec2]):
    A, B, C = triangle
    P, Q, R, S = rect
    normals = [(C-B).normal(), (A-C).normal(), (B-A).normal(), (Q-P).normal(), (R-Q).normal(), (S-R).normal(), (P-S).normal()]
    normals = set(normals)

    for normal in normals:
        projTri = [normal.dot(P) for P in triangle]
        projRect = [normal.dot(P) for P in rect]
        triA, triB = min(projTri), max(projTri)
        rectA, rectB = min(projRect), max(projRect)

        if (triB >= rectA and rectB >= triA) :
            continue
        return False
    return True


class Viewport (pygame.Surface):
    def __init__(self, size : vec2, tileSize):
        super().__init__((size.x, size.y))

        self.zBuffer = numpy.full((size.x, size.y), math.inf) # contains columns not rows to be more like surfarray [col][row]

        self.tileSize = tileSize
        self.tilesInWidth = size.x // tileSize #No of tiles along the width
        self.tilesInHeight = size.y // tileSize

        self.tiles = dict([((y, x),[]) for y in range(self.tilesInHeight) for x in range(self.tilesInWidth)])

        self.tileGrid = dict()
        for row, col in self.tiles.keys():
            xMin, yMin = col*self.tileSize, row*self.tileSize
            xMax, yMax = xMin+self.tileSize, yMin+self.tileSize
            ndcY, ndcX = numpy.meshgrid(
                numpy.linspace(2*yMin/self.height - 1, 2*yMax/self.height - 1, num = self.tileSize),
                numpy.linspace(2*xMin/self.width - 1, 2*xMax/self.width - 1, num = self.tileSize)
            )
            self.tileGrid[(row, col)] = (ndcY, ndcX, xMin, yMin, xMax, yMax)

    #given triangle must be tiled. If it lies in a tile, it be appended to that tile.
    def tileTriangle(self, triangle, color, edgeFuncs):   
        ndcXs = [(self.tilesInWidth) * (P[0]/P[3] + 1)/2 for P in triangle]
        ndcYs = [(self.tilesInHeight) * (P[1]/P[3] + 1)/2 for P in triangle]
        xMax, xMin = clamp(math.ceil(max(ndcXs)), 0, self.tilesInWidth), clamp(math.floor(min(ndcXs)), 0, self.tilesInWidth)
        yMax, yMin = clamp(math.ceil(max(ndcYs)), 0, self.tilesInHeight), clamp(math.floor(min(ndcYs)), 0, self.tilesInHeight)
        for row in range(yMin, yMax):
            for col in range(xMin, xMax):
                x0 = 2 * (col * self.tileSize) / self.width - 1
                y0 = 2 * (row * self.tileSize) / self.height - 1
                x1 = 2 * ((col + 1) * self.tileSize) / self.width - 1
                y1 = 2 * ((row + 1) * self.tileSize) / self.height - 1

                rectCorners  =  [vec2(x0, y0), vec2(x1, y0), vec2(x1, y1), vec2(x0, y1),]
                triCorners = [vec2(P[0]/P[3], P[1]/P[3]) for P in triangle]

                if (overlap(triCorners, rectCorners)) :
                    self.tiles[(row, col)].append({
                        'triangle' : triangle,
                        'color' : color,
                        'edge functions' : edgeFuncs
                    })  

    # def tileTriangle(self, triangle, color, edgeFuncs):   
    #         # if not isinstance(edgeFuncs, numpy.ndarray):
    #         #     return
    #         #Triangle is in homogeneous space.
    #         ndcXs = [(self.tilesInWidth) * (P[0]/P[3] + 1)/2 for P in triangle]
    #         ndcYs = [(self.tilesInHeight) * (P[1]/P[3] + 1)/2 for P in triangle]
    #         xMax, xMin = clamp(math.ceil(max(ndcXs)), 0, self.tilesInWidth), clamp(math.floor(min(ndcXs)), 0, self.tilesInWidth)
    #         yMax, yMin = clamp(math.ceil(max(ndcYs)), 0, self.tilesInHeight), clamp(math.floor(min(ndcYs)), 0, self.tilesInHeight)
    #         for row in range(yMin, yMax):
    #             for col in range(xMin, xMax):
    #                 self.tiles[(row, col)].append({
    #                     'triangle' : triangle,
    #                     'color' : color,
    #                     'edge functions' : edgeFuncs
    #                 })
    
                
    def flush(self):
        #We have the seperate tile entity so that we dont need to keep rebuilting grid everyframe.
        for tileList in self.tiles.values():
            tileList.clear()        
        self.fill((35,35,35))
        self.zBuffer.fill(math.inf)
