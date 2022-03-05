import random, sys, time, math, pygame
from pygame.locals import *
import os

''' 게임에 들어가는 사운드 효과를 불러오고 변수에 저장하는 단계이다. '''

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


''' 변수 값을 미리 설정해두는 단계. 필요할때는 여기로 돌아와서 그 숫자를 조정해주면 된다. '''


FPS = 30 # 화면을 얼마나 업데이트 할지
WINWIDTH = 640 # 프로그램의 윈도우 너비. 픽셀 단위
WINHEIGHT = 480 # 프로그램의 윈도우 높이. 픽셀 단위
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

BACKGROUNDCOLOR = (126, 150, 156)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERASLACK = 90     # 중앙에서 괴물이 얼마나 멀어지면 카메라를 움질일 것인지 결정
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 10    # how high the player bounces
STARTSIZE = 30       # 플레이어가 어떤 크기에서 시작하는지
WINSIZE = 300        # 오메가 괴물이 되려면 얼마나 커져야 하는지
INVULNTIME = 2       # 적과 부딪힌 다음 얼마의 기간 동안 무적인지. 초 단위
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3        # how much health the player starts with

NUMOBJ = 80        # 활성 영역 안에 배경사물을 몇개 보여줄지
NUMHOSTS = 30    # 활성 영역 안에 둘 적 수
HOSTMINSPEED = 3 # 괴물의 가장 느린 속도
HOSTMAXSPEED = 7 # 괴물의 가장 빠른 속도
DIRCHANGEFREQ = 2    # 프레임당 방향을 바꿀 수 있는 확률. %단위
LEFT = 'left'
RIGHT = 'right'

''' 이 프로그램에는 3개의 데이터 구조가 있다. 플레이어 괴물, 적 사람, 그리고 배경의 오브젝트.
각 데이터 구조는 딕셔너리이며 해당 키를 가지고 있다.

- 3개의 데이터 구조가 공통적으로 사용하는 키 : 
'x' = 게임 세계에서 객체의 왼쪽 가장자리 좌표
'y' = 게임 세계에서 객체의 위쪽 좌표
'rect' = 스크린에 객체가 위치해야 하는 영역이며 pygam.Recr 객체로 표시

- Player 데이터 구조에서 사용하는 키 : 
'surface' = 화면에 그릴 괴물 이미지를 저장하는 객체
'facing' = Left나 Right로 설정. 플레이어가 어느 방향으로 보고 있을지 결정한다.
'size' = 플레이어의 너피와 높이. 픽셀 단위이다.
'bounce' = 현재 플레이어가 점프 동작 중 어떤 위치에 있는지 나타낸다. 0은 그냥 서 있는 경우이고, BOUNCERATE(점프완료)까지 점프한다.
'health' = 플레이어의 라이프가 얼마나 남아 있는지 보여주는 정수값

- 적(PERSON) 데이터 구조에서 사용하는 키 : 
'surface' = 화면에 그릴 적 이미지를 저장하는 pygame.Surface객체.
'movex' = 프레임당 적이 몇 픽셀을 수평으로 움직였는지 저장한다. 음수는 왼쪽으로 움직인 것을, 양수는 오른쪽으로 움직인 것을 의미.
'movey' = 프레임당 다람쥐가 몇 픽셀을 수직으로 움직였는지 저장한다. 음수는 위쪽으로 움직인 것을, 양수는 아래쪽으로 움직은 것을 의미.
'bounce' = 플레이어와 동일
'bouncerate' = 적이 얼마나 빨리 점프하는지 나타낸다. 숫자가 작을수록 빠르게 점프한다.
'bounceheight' = 적이 얼마나 높이 점프하는지 나타낸다. 픽셀 단위.

- 오브젝트 데이터 구조에서 사용하는 키 : 
OBJimage = 오프젝트 이미지들의 pygame.surface객체들을 가리키는 인덱스 숫자. '''



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


''' 게임 제작에 필요한 변수들을 설정하는 단계 '''

def runGame():
    # 새 게임을 시작할 때 변수를 설정한다.
    invulnerableMode = False  # 플레이어가 적과 부딪힌 다음 무적이 되었는지
    invulnerableStartTime = 0 # 무적이 되기 시작한 시간
    gameOverMode = False      # 플레이어가 졌는지
    gameOverStartTime = 0     # 플레이어가 진 시간
    winMode = False           # 플레이어가 이겼는지

    # 게임에 필요한 글씨를 쓰기 위한 surface를 만든다.
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('You have achieved OMEGA Host!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camerax 와 cameray 는 카메라 뷰의 가장 왼쪽 상단을 말한다.
    camerax = 0
    cameray = 0

    O_Objs = []    # 게임의 모든 오브젝트 객체를 저장
    personObjs = [] # 플레이어가 아닌 적 개체들을 저장한다.
    # 플레이어 괴물 객체를 저장한다.
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

    # 화면상에 무작위로 오브젝트를 늘어놓고 시작한다.
    for i in range(10):
        O_Objs.append(makeNewOBJ(camerax, cameray))
        O_Objs[i]['x'] = random.randint(0, WINWIDTH)
        O_Objs[i]['y'] = random.randint(0, WINHEIGHT)

    while True: # main game loop
        # 무적인 상태를 꺼야 하는지 검사한다.
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        # 적 개체들을 움직인다.
        for sObj in personObjs:
            # 적 개체들을 움직이면서 그들의 점프 정도를 조정한다.
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0 # 점프하는 정도 리셋

            # 무작위로 방향을 바꾼다.
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                if sObj['movex'] > 0: # faces right
                    sObj['surface2'] = pygame.transform.scale(R_PERSON_IMG, (sObj['width'], sObj['height']))
                else: # faces left
                    sObj['surface2'] = pygame.transform.scale(L_PERSON_IMG, (sObj['width'], sObj['height']))


        # 지워야 할 객체가 있는지 검사
        for i in range(len(O_Objs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, O_Objs[i]):
                del O_Objs[i]
        for i in range(len(personObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, personObjs[i]):
                del personObjs[i]

        # 오브젝트와 적이 충분하지 않으면 추가한다.
        while len(O_Objs) < NUMOBJ:
            O_Objs.append(makeNewOBJ(camerax, cameray))
        while len(personObjs) < NUMHOSTS:
            personObjs.append(makeNewPerson(camerax, cameray))

        # 카메라슬랙을 벗어났으면 camerax와 cameray를 조정한다.
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


        '''본격적으로 객체들을 화면에 나타나게 하는 단계'''

    
        # 지정한 색의 배경화면을 그린다.
        DISPLAYSURF.fill(BACKGROUNDCOLOR)

        # 화면에 모든 오브젝트 객체를 그린다.
        for gObj in O_Objs:
            gRect = pygame.Rect( (gObj['x'] - camerax,
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(OBJIMAGES[gObj['objImage']], gRect)


        # 적 객체들을 그린다.
        for sObj in personObjs:
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface2'], sObj['rect'])


        # 플레이어 괴물을 그린다.
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # 생명력을 그린다.
        drawHealthMeter(playerObj['health'])

        ''' 왼쪽을 보면 왼쪽을 보는 이미지를, 오른쪽을 보면 오른쪽을 보는 이미지를 디스플레이 '''

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


        ''' 플레이어를 움직이는 단계 '''

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


            ''' 플레이어와 적 개체가 충돌했을때, 플레이어의 생명을 깎을지 적이 먹히는지 판단해주는 단계 '''

            # check if the player has collided with any people
            for i in range(len(personObjs)-1, -1, -1):
                psObj = personObjs[i]
                if 'rect' in psObj and playerObj['rect'].colliderect(psObj['rect']):
                    # a player/person collision has occurred

                    if psObj['width'] * psObj['height'] <= playerObj['size']**2:
                        # 플레이어가 더 커서 적을 먹는 경우

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
                        # 플레이어가 더 작아서 생명력이 깎이는 경우

                        hurt.play() # play sound effect
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            fail.play() # play sound effect
                            gameOverMode = True # turn on "game over mode"
                            gameOverStartTime = time.time()

        ''' 괴물이 죽었는지, 아니면 일정 사이즈에 도달해서 win했는지 판단해주는 단계 '''

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


''' 생명력 바 디자인 단계 '''

def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


''' 아래는 점프의 속도와 높이를 조절하는 단계이다. '''

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


''' 카메라 뷰 조정을 위한 단계이다. 괴물이 왼쪽으로 이동하는지, 오른쪽으로 이동하는지에 따라 카메라의 뷰가 달라지게 하는 단계.
카메라의 뷰가 옮겨감에 따라 새로운 적 객체와 오브젝트도 소환하게 한다. '''

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