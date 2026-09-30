import pygame, numpy, math
from utility import vec2, clamp

class Viewport (pygame.Surface):
    def __init__(self, size : vec2, tileSize, screen : pygame.Surface):
        super().__init__((size.x, size.y))

        self.zBuffer = numpy.full((size.x, size.y), math.inf) # contains columns not rows to be more like surfarray [col][row]

        self.tileSize = tileSize
        self.tilesInWidth = size.x // tileSize 
        self.tilesInHeight = size.y // tileSize

        #stores which triangle lie in the tile, Dict of dict is like a struct of arrays.
        self.tiles = dict([((y, x), {
            'triangles' : [],
            'edge functions' : [],
            'colors' : [],
            'coverage' : []
        }) for y in range(self.tilesInHeight) for x in range(self.tilesInWidth)])

        #the structure of the grid, stuff we avoid building again and again
        self.tileGrid = numpy.meshgrid(
            numpy.linspace(0, 2*self.tileSize/self.height, num = self.tileSize),
            numpy.linspace(0, 2*self.tileSize/self.width, num = self.tileSize),
        )
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
        w, h = 2*self.tileSize/self.width, 2*self.tileSize/self.height
        offsets = [vec2(w if normal.x >= 0 else 0, h if normal.y >= 0 else 0) for normal in edgeNormals]
    
        for row in range(yMin, yMax):
            for col in range(xMin, xMax):
                rejected = False
                fullCover = True
                s = vec2(2 * (col * self.tileSize) / self.width - 1, 2 * (row * self.tileSize) / self.height - 1)
                for e, t in zip(edgeFuncs, offsets): 
                    eSum = e[0]*(s.x + t.x) + e[1]*(s.y + t.y) + e[2]
                    oppESum = e[0]*(w + s.x - t.x) + e[1]*(h + s.y - t.y) + e[2]
                    if eSum <= 0:
                        rejected = True
                        break
                    if oppESum <= 0 and fullCover:
                        fullCover = False
                if not rejected:
                    self.tiles[(row, col)]['triangles'].append(numpy.array(triangle, dtype=numpy.float64))
                    self.tiles[(row, col)]['colors'].append(numpy.array(color, dtype = numpy.int32))
                    self.tiles[(row, col)]['edge functions'].append(numpy.array(edgeFuncs, dtype=numpy.float64))
                    self.tiles[(row, col)]['coverage'].append(fullCover)
        
    def set(self):
        pygame.surfarray.blit_array(self, self.pixelBuffer)
        x,y = self.screen.width//2, self.screen.height//2
        self.screen.blit(self, (x - self.width // 2, y - self.height // 2))
                
    def flush(self):
        #We have the seperate tile entity so that we dont need to keep rebuilting grid everyframe.
        for tileList in self.tiles.values():
            tileList['triangles'].clear()
            tileList['colors'].clear()
            tileList['edge functions'].clear()
            tileList['coverage'].clear()        
        self.zBuffer.fill(math.inf)
        self.pixelBuffer.fill(35)
    #worse case O(tiles x triangles + 2*noOfPixels) 

