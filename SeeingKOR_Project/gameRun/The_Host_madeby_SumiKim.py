import random, sys, time, math, pygame
from pygame.locals import *
import os

pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()                              # initialize pygame

try:
    pygame.mixer.music.load(os.path.join('music', 'hanriver.mp3')) #load music
    fail = pygame.mixer.Sound(os.path.join('music','MONSTER.wav'))  #load sound
    hurt = pygame.mixer.Sound(os.path.join('music','hit.wav'))  #load sound
    eat = pygame.mixer.Sound(os.path.join('music','headchop.wav'))  #load sound
    win = pygame.mixer.Sound(os.path.join('music','m_victory.wav'))  #load sound


except:
    raise(UserWarning, "could not load or play soundfiles in 'music' folder :-(")

pygame.mixer.music.play(-1)  # play music non-stop


FPS = 30 # frames per second to update the screen
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

BACKGROUNDCOLOR = (126, 150, 156)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERASLACK = 90     # how far from the center the host moves before moving the camera
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 10    # how high the player bounces
STARTSIZE = 30       # how big the player starts off
WINSIZE = 300        # how big the player needs to be to win
INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3        # how much health the player starts with

NUMOBJ = 80        # number of objects in the active area
NUMHOSTS = 30    # number of hostss in the active area
HOSTMINSPEED = 3 # slowest host speed
HOSTMAXSPEED = 7 # fastest host speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_HOST_IMG, L_PERSON_IMG, R_HOST_IMG, R_PERSON_IMG, OBJIMAGES

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('HOST.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('The Host')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    L_HOST_IMG = pygame.image.load('HOST.png')
    L_PERSON_IMG = pygame.image.load('Person.png')
    R_HOST_IMG = pygame.transform.flip(L_HOST_IMG, True, False)
    R_PERSON_IMG = pygame.transform.flip(L_PERSON_IMG, True, False)

    OBJIMAGES = []
    for i in range(1, 6):
        OBJIMAGES.append(pygame.image.load('object%s.png' % i))

    while True:
        runGame()


def runGame():
    # set up variables for the start of a new game
    invulnerableMode = False  # if the player is invulnerable
    invulnerableStartTime = 0 # time the player became invulnerable
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
    winMode = False           # if the player has won

    # create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('You have achieved OMEGA Host!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camerax and cameray are the top left of where the camera view is
    camerax = 0
    cameray = 0

    O_Objs = []    # stores all the objects in the game
    personObjs = [] # stores all the non-player person objects
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(L_HOST_IMG, (STARTSIZE,STARTSIZE)),
                 'surface2': pygame.transform.scale(L_PERSON_IMG, (STARTSIZE,STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'health': MAXHEALTH}

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

    # start off with some random object images on the screen
    for i in range(10):
        O_Objs.append(makeNewOBJ(camerax, cameray))
        O_Objs[i]['x'] = random.randint(0, WINWIDTH)
        O_Objs[i]['y'] = random.randint(0, WINHEIGHT)

    while True: # main game loop
        # Check if we should turn off invulnerability
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        # move all the people
        for sObj in personObjs:
            # move the person, and adjust for their bounce
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0 # reset bounce amount

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                if sObj['movex'] > 0: # faces right
                    sObj['surface2'] = pygame.transform.scale(R_PERSON_IMG, (sObj['width'], sObj['height']))
                else: # faces left
                    sObj['surface2'] = pygame.transform.scale(L_PERSON_IMG, (sObj['width'], sObj['height']))


        # go through all the objects and see if any need to be deleted.
        for i in range(len(O_Objs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, O_Objs[i]):
                del O_Objs[i]
        for i in range(len(personObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, personObjs[i]):
                del personObjs[i]

        # add more Objects & people if we don't have enough.
        while len(O_Objs) < NUMOBJ:
            O_Objs.append(makeNewOBJ(camerax, cameray))
        while len(personObjs) < NUMHOSTS:
            personObjs.append(makeNewPerson(camerax, cameray))

        # adjust camerax and cameray if beyond the "camera slack"
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # draw the background
        DISPLAYSURF.fill(BACKGROUNDCOLOR)

        # draw all the objects on the screen
        for gObj in O_Objs:
            gRect = pygame.Rect( (gObj['x'] - camerax,
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(OBJIMAGES[gObj['objImage']], gRect)


        # draw the other people
        for sObj in personObjs:
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface2'], sObj['rect'])


        # draw the player Host
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # draw the health meter
        drawHealthMeter(playerObj['health'])

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT: # change player image
                        playerObj['surface'] = pygame.transform.scale(L_HOST_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT: # change player image
                        playerObj['surface'] = pygame.transform.scale(R_HOST_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                    
                elif winMode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                # stop moving the player's Host
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
            if moveRight:
                playerObj['x'] += MOVERATE
            if moveUp:
                playerObj['y'] -= MOVERATE
            if moveDown:
                playerObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # reset bounce amount

            # check if the player has collided with any people
            for i in range(len(personObjs)-1, -1, -1):
                psObj = personObjs[i]
                if 'rect' in psObj and playerObj['rect'].colliderect(psObj['rect']):
                    # a player/person collision has occurred

                    if psObj['width'] * psObj['height'] <= playerObj['size']**2:
                        # player is larger and eats the PERSON
                        eat.play() # play sound effect
                        playerObj['size'] += int( (psObj['width'] * psObj['height'])**0.2 ) + 1
                        del personObjs[i]

                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(L_HOST_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(R_HOST_IMG, (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:
                            winMode = True # turn on "win mode"

                    elif not invulnerableMode:
                        # player is smaller and takes damage
                        hurt.play() # play sound effect
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            fail.play() # play sound effect
                            gameOverMode = True # turn on "game over mode"
                            gameOverStartTime = time.time()
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # end the current game

        # check if the player has won.
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)




def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounceRate means a slower bounce.
    # Larger bounceHeight means a higher bounce.
    # currentBounce will always be less than bounceRate
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)

def getRandomVelocity():
    speed = random.randint(HOSTMINSPEED, HOSTMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewPerson(camerax, cameray):
    ps = {}
    generalSize = random.randint(5, 30)
    multiplier = random.randint(1, 3)
    ps['width']  = (generalSize + random.randint(0, 15)) * multiplier
    ps['height'] = ps['width']
    ps['x'], ps['y'] = getRandomOffCameraPos(camerax, cameray, ps['width'], ps['height'])
    ps['movex'] = getRandomVelocity()
    ps['movey'] = getRandomVelocity()
    if ps['movex'] < 0: # person is facing left
        ps['surface2'] = pygame.transform.scale(L_PERSON_IMG, (ps['width'], ps['height']))
    else: # person is facing right
        ps['surface2'] = pygame.transform.scale(R_PERSON_IMG, (ps['width'], ps['height']))
    ps['bounce'] = 0
    ps['bouncerate'] = random.randint(10, 18)
    ps['bounceheight'] = random.randint(10, 50)
    return ps


def makeNewOBJ(camerax, cameray):
    gr = {}
    gr['objImage'] = random.randint(0, len(OBJIMAGES) - 1)
    gr['width']  = OBJIMAGES[0].get_width()
    gr['height'] = OBJIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr


def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()