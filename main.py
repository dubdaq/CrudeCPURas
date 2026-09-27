#unusable if scene has more than 500 trianglez.
#rendering suzanne is impossible

import pygame, sys, math
from utility import vec2, vec3, normalize
from config import *
from Engine import Player, Object, DirectionalLight, Gizmo

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
        [ 0, -1, -0.73],
        [ 1, -1,  1],
        [-1, -1,  1],
        [0,   1,  0.42]
    ],
    triangles=[
        [0, 1, 2],
        [3, 1, 0],
        [0, 2, 3],
        [2, 1, 3],
    ],
    position=[0, 0, -3]
)
suzanne = Object.loadMesh(r"C:\Users\Aryan\OneDrive\Documents\VSCodeStuff\pyFPS\game1\suzanne.txt", (2, 0, 1))
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
    inside = False
)

cubeModel.yawPitchRotation(math.pi/3, math.pi/6)
pyramidModel.render()
cubeModel.render()
suzanne.render()
floorModel.render()

light = DirectionalLight((1, -3, 1))
player = Player(screen, vec2(1152, 768), 64, vec3(-5, 0, 5), 2*math.pi/3, 0, speed = 2/updatesPerSecond)
gizmo = Gizmo(screen, player.camera, player.viewport)

#UPDATE AND DISPLAY FUNCTIONS
def update():
    suzanne.yawPitchRotation(math.pi/updatesPerSecond, 0)
    pyramidModel.yawPitchRotation(0, math.pi/updatesPerSecond)
    theta, psi = 0, 0
    if keys[pygame.K_UP]:
        psi -= mouseSensitivity * math.pi/updatesPerSecond
    if keys[pygame.K_DOWN]:
        psi += mouseSensitivity * math.pi/updatesPerSecond
    if keys[pygame.K_LEFT]:
        theta -= mouseSensitivity * math.pi/updatesPerSecond
    if keys[pygame.K_RIGHT]:
        theta += mouseSensitivity * math.pi/updatesPerSecond

    dx, dy, dz = 0, 0, 0
    if keys[pygame.K_w]: 
        dz += player.speed 
    if keys[pygame.K_s]: 
        dz -= player.speed 
    if keys[pygame.K_a]: 
        dx += player.speed 
    if keys[pygame.K_d]: 
        dx -= player.speed

    if keys[pygame.K_SPACE]:
        dy -= player.speed

    if (theta or psi or dx or dz or dy):
        player.idle = False
        
        parallel = normalize([math.sin(player.theta + theta), -math.sin(player.psi + psi), math.cos(player.theta + theta)])
        normal = [-parallel[2], 0, parallel[0]]
        diagVector = normalize([dx, dy, dz], player.speed)
        if diagVector == None:
            diagVector = [0, 0, 0]

        displacementVector = vec3(normal[0] * diagVector[0] + normal[2] * diagVector[2], parallel[1] * diagVector[2] + diagVector[1], parallel[0] * diagVector[0] + parallel[2] * diagVector[2])

        player.move(theta, psi, displacementVector)

    else:
        player.idle = True

def display(interpolation):
    #if not player.idle or sceneChange or numpy.all(player.viewport.zBuffer == math.inf):
    # will implement dirty scenes later. 
    
    suzanne.yawPitchRotation(math.pi/updatesPerSecond * interpolation, 0)
    pyramidModel.yawPitchRotation(math.pi/updatesPerSecond * interpolation, 0)

    player.interpolate(interpolation)
    player.viewport.flush()
    gizmo.clear()
    player.render(Object.renderList, [light])
    gizmo.drawLine(vec3(2, 0, -1), vec3(3, 1, 7))
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
while running:
    loops = 0
    keys = pygame.key.get_pressed()

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
