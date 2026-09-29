#unusable if scene has more than 500 trianglez.
#rendering suzanne is impossible

import pygame, sys, math
from utility import vec2, vec3, normalize
from config import *
from Engine import *

fps = 0 #to measure fps

#INITIALITING PYGAME 
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
font = pygame.font.SysFont("Courier", 15) 

#Simple Mesh
cubeModel = Object(
    verticies = [
        [ 1, -1, -1],
        [ 1, -1,  1],
        [-1, -1,  1],
        [-1, -1, -1],
        [ 1,  1, -1],
        [ 1,  1,  1],
        [-1,  1,  1],
        [-1,  1, -1],
    ],
    triangles = [
        [1, 2, 3],
        [7, 6, 5],
        [4, 5, 1],
        [5, 6, 2],
        [2, 6, 7],
        [0, 3, 7],
        [0, 1, 3],
        [4, 7, 5],
        [0, 4, 1],
        [1, 5, 2],
        [3, 2, 7],
        [4, 0, 7],
    ],
    position = [3, 1, 7]
)
pyramidModel = Object(
    verticies=[
        [    0, -1,    1],
        [-0.87, -1, -0.5],
        [ 0.86, -1, -0.5],
        [    0,  1,  0]
    ],
    triangles=[
        [0, 1, 2],
        [3, 1, 0],
        [0, 2, 3],
        [2, 1, 3],
    ],
    position=[0, 0, -3]
)
suzanne = Object.loadMesh(r"C:\Users\Aryan\OneDrive\Documents\VSCodeStuff\pyFPS\game1\suzanne.txt", (0, 0, 3))
floorModel = Object(
    verticies = [
        [ 5, 1, -5],
        [ 5, 1,  5],
        [-5, 1, -5],
        [-5, 1,  5]
    ],
    triangles = [
        [2, 1, 0],
        [3, 1, 2]
    ],
    position=[0, -2.0001, 0],
    inside = True
)

debugModel = Object(
    verticies=[
        [ 1,  1, 1],
        [ 1, -1, 1],
        [-1,  1, 1]
    ],
    triangles = [[0, 1, 2]],
    position=[0, 0, 1],
    inside = True
)

suzanne.yawPitchRotation(math.pi, 0)

light = DirectionalLight((1, -3, 1))
player = Player(screen, vec2(1280, 768), 64, vec3(0, 0, 0), 0, 0, speed = 2/updatesPerSecond)
gizmo = Gizmo(screen, player.camera, player.viewport)

scene = Scene([suzanne])

#UPDATE AND DISPLAY FUNCTIONS
def update():
    player.movement.update()
    scene.updateObjects()

def display(interpolation):
    #if not player.idle or sceneChange or numpy.all(player.viewport.zBuffer == math.inf):
    # will implement dirty scenes later. 
    
    player.viewport.flush()
    gizmo.clear()

    if not player.movement.idle: 
        player.movement.interpolate(interpolation)
    
    player.render(scene, [light])

    gizmo.drawLine(vec3(1, -1, 3), vec3(-1, 1, 3))
    gizmo.set()

    txtRect = font.render(f"{fps}", True, "white")
    screen.blit(txtRect, (0, 0))


#DEWITTER GAME LOOP
nextGameTick = pygame.time.get_ticks()
startTime = pygame.time.get_ticks()
loops = 0
interpolation = 0

currentFrame = 0
running = True

if __name__ == "__main__":
    while running:
        loops = 0
        keysHeld = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        while (pygame.time.get_ticks() > nextGameTick and loops < maxFrameSkip):
            update()
            nextGameTick += timePerUpdate
            loops += 1

        interpolation = float( pygame.time.get_ticks() + timePerUpdate - nextGameTick ) / float(timePerUpdate)
        display(interpolation)
        currentFrame += 1
        pygame.display.flip()

        curTime = pygame.time.get_ticks()
        if curTime - startTime >= 1000:
            fps = currentFrame
            currentFrame = 0
            startTime = curTime
        
    pygame.quit()
    sys.exit()
