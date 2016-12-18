# Block Breaker Game
# Chapter 9

import sys, time, random, math, pygame
from pygame.locals import *
from MyLibrary import *
import cv2
import numpy as np
levels = (
(1,4,4,2,4,4,6,3,4,5,4,4, 
 4,3,8,0,0,3,3,0,0,6,3,4, 
 1,3,0,4,0,5,8,6,4,0,3,4, 
 4,3,8,7,7,3,3,8,8,4,3,4, 
 4,3,3,2,3,4,2,4,4,4,4,0, 
 3,4,3,3,3,5,3,3,4,3,3,4, 
 3,3,7,0,0,3,7,0,0,0,4,4, 
 3,8,0,4,0,6,7,0,5,6,4,4, 
 3,0,0,0,4,7,8,0,0,0,4,0, 
 4,4,3,3,4,8,4,4,3,3,4,4),

(1,1,1,1,1,1,1,1,1,1,1,1, 
 1,1,1,1,1,1,1,1,1,1,1,1, 
 1,1,1,1,1,1,1,1,1,1,1,1, 
 1,1,1,1,1,1,1,1,1,1,1,1, 
 1,1,1,1,1,0,0,1,1,1,1,1, 
 1,1,1,1,1,0,0,1,1,1,1,1, 
 1,1,1,1,1,1,1,1,1,1,1,1, 
 1,1,1,1,1,1,1,1,1,1,1,1, 
 1,1,1,1,1,1,1,1,1,1,1,1, 
 1,1,1,1,1,1,1,1,1,1,1,1),

(2,2,2,2,2,2,2,2,2,2,2,2, 
 2,0,0,2,2,2,2,2,2,0,0,2, 
 2,0,0,2,2,2,2,2,2,0,0,2, 
 2,2,2,2,2,2,2,2,2,2,2,2, 
 2,2,2,2,2,2,2,2,2,2,2,2, 
 2,2,2,2,2,2,2,2,2,2,2,2, 
 2,2,2,2,2,2,2,2,2,2,2,2, 
 2,0,0,2,2,2,2,2,2,0,0,2, 
 2,0,0,2,2,2,2,2,2,0,0,2, 
 2,2,2,2,2,2,2,2,2,2,2,2),

(3,3,3,3,3,3,3,3,3,3,3,3, 
 3,3,0,0,0,3,3,0,0,0,3,3, 
 3,3,0,0,0,3,3,0,0,0,3,3, 
 3,3,0,0,0,3,3,0,0,0,3,3, 
 3,3,3,3,3,3,3,3,3,3,3,3, 
 3,3,3,3,3,3,3,3,3,3,3,3, 
 3,3,0,0,0,3,3,0,0,0,3,3, 
 3,3,0,0,0,3,3,0,0,0,3,3, 
 3,3,0,0,0,3,3,0,0,0,3,3, 
 3,3,3,3,3,3,3,3,3,3,3,3),
 

)
def GetPos():
	global cxx,cyy,cxx_o,cyy_o
	# Take each frame
	_, frame = cap.read()
	frame = cv2.flip(frame,1)  #0:inves up/down 1:mirror (right/left)  -1:inves up/down ,right/left
	# Convert BGR to HSV
	#frame2= frame.copy()
	frame = cv2.GaussianBlur(frame,(77,77),0)
	h,w,d=frame.shape

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	# define range of blue color in HSV
	lower_green = np.array([60,50,50])
	upper_green = np.array([80,255,255])
	# Threshold the HSV image to get only blue colors
	mask = cv2.inRange(hsv, lower_green, upper_green)
	#mask_org=mask.copy()
	# Bitwise-AND mask and original image
	#res = cv2.bitwise_and(frame,frame, mask= mask)

	img2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	cx=np.zeros(len(contours))
	cy=np.zeros(len(contours))
	if cxx>0:
		cxx_o=cxx
		cyy_o=cyy
	
	if len(contours)>0:

		cxx=0
		cyy=0
		#print (len(contours))
		cnt = contours[0]
		M = cv2.moments(cnt)
		#print (M)
		if M['m00']>1:
			for i in range(len(contours)): 

				cx[i] = int(M['m10']/M['m00'])
				cy[i] = int(M['m01']/M['m00'])
				cxx=cxx+cx[i]
				cyy=cyy+cy[i]
				
		#global cxx,cyy		
		cxx=cxx/(len(contours))
		cyy=cyy/(len(contours))
		return cxx,cyy	
	else:	
		#print(cxx_o,cyy_o)
		return cxx_o,cyy_o	
	
def audio_init():
	global hit, coinflip
	
	#initialize the audio mixer
	pygame.mixer.init() #not always called by pygame.init()

	#load sound files
	hit = pygame.mixer.Sound("hit.wav")
	coinflip =pygame.mixer.Sound("coinflip.wav")

def play_sound(sound):
	channel = pygame.mixer.find_channel(True)
	channel.set_volume(0.5)
	channel.play(sound)
#this function increments the level
def goto_next_level():
	global level, levels
	level += 1
	if level > len(levels)-1: level = 0
	load_level()

#this function updates the blocks in play
def update_blocks():
	global block_group, waiting
	if len(block_group) == 0: #all blocks gone?
		goto_next_level()
		waiting = True
	block_group.update(ticks, 50)
		
#this function sets up the blocks for the level
def load_level():
	global level, block, block_image, block_group, levels
	
	block_image = pygame.image.load("blocks.png").convert_alpha()

	block_group.empty() #reset block group
	
	for bx in range(0, 12):
		for by in range(0,10):
			block = MySprite()
			block.set_image(block_image, 58, 28, 4)
			x = 40 + bx * (block.frame_width+1)
			y = 60 + by * (block.frame_height+1)
			block.position = x,y

			#read blocks from level data
			num = levels[level][by*12+bx]
			block.first_frame = num-1	#下一關會變顏色，就是另一個frame
			block.last_frame = num-1
			if num > 0: #0 is blank
				block_group.add(block)

	print(len(block_group))

	
#this function initializes the game
def game_init():
	global screen, font, timer
	global paddle_group, block_group, ball_group
	global paddle, block_image, block, ball

	pygame.init()
	screen = pygame.display.set_mode((800,600))
	pygame.display.set_caption("Block Breaker Game")
	font = pygame.font.Font(None, 36)
	pygame.mouse.set_visible(False)
	timer = pygame.time.Clock()

	#create sprite groups
	paddle_group = pygame.sprite.Group()
	block_group = pygame.sprite.Group()
	ball_group = pygame.sprite.Group()

	#create the paddle sprite
	paddle = MySprite()
	paddle.load("paddle.png")
	paddle.position = 400, 540
	paddle_group.add(paddle)

	#create ball sprite
	ball = MySprite()
	ball.load("ball.png")
	ball.position = 400,300
	ball_group.add(ball)



#this function moves the paddle
def move_paddle():
	global movex,movey,keys,waiting,count,pos_x,pos_y
	#if count>=1:
	pos_x_O=pos_x
	pos_x,pos_y=GetPos()
	print("pos_x=",pos_x)
	#	count=0
	#else:
	#	count+=1
	paddle_group.update(ticks, 50)

	if keys[K_SPACE]:
		if waiting:
			waiting = False
			reset_ball()
	elif keys[K_LEFT]: paddle.velocity.x = -12.0
	elif keys[K_RIGHT]: paddle.velocity.x = 12.0
	else:
		#if movex < -2: paddle.velocity.x = movex
		#elif movex > 2: paddle.velocity.x = movex
		#else: paddle.velocity.x = 0
		#paddle.velocity.x = 0
	#paddle.X += paddle.velocity.x
	
		if pos_x>1 and pos_x<720:
			paddle.X=int(pos_x*(800/640))

		if paddle.X > 710: paddle.X = 710
	
	#if paddle.X < 0: paddle.X = 0
	#elif paddle.X > 710: paddle.X = 710

#this function resets the ball's velocity
def reset_ball():
	ball.velocity = Point(6, -12.0)
	#print(ball.velocity)

#this function moves the ball
def move_ball():
	global waiting, ball, game_over, lives

	#move the ball			  
	ball_group.update(ticks, 50)
	if waiting:
		ball.X = paddle.X + 40
		ball.Y = paddle.Y - 20
	ball.X += ball.velocity.x
	ball.Y += ball.velocity.y
	if ball.X < 0:
		ball.X = 0
		ball.velocity.x *= -1  #反方向
	elif ball.X > 780:
		ball.X = 780
		ball.velocity.x *= -1  #反方向
	if ball.Y < 0:
		ball.Y = 0
		ball.velocity.y *= -1  #反方向
	elif ball.Y > 580: #missed paddle
		waiting = True
		lives -= 1
		if lives < 1: game_over = True

#this function test for collision between ball and paddle
def collision_ball_paddle():
	if pygame.sprite.collide_rect(ball, paddle):
		play_sound(hit)
		ball.velocity.y = -abs(ball.velocity.y)#Y反方向
		bx = ball.X + 8	 #球等於16X16 ,半徑8
		by = ball.Y + 8
		px = paddle.X + paddle.frame_width/2
		py = paddle.Y + paddle.frame_height/2
		if bx < px: #left side of paddle?
			ball.velocity.x = -abs(ball.velocity.x)#左方向
		else: #right side of paddle?
			ball.velocity.x = abs(ball.velocity.x)#右方向

#this function tests for collision between ball and blocks
def collision_ball_blocks():
	global score, block_group, ball
	
	hit_block = pygame.sprite.spritecollideany(ball, block_group)
	if hit_block != None:
		play_sound(coinflip)
		score += 10
		block_group.remove(hit_block)
		bx = ball.X + 8
		by = ball.Y + 8

		#hit middle of block from above or below?
		if bx > hit_block.X+5 and bx < hit_block.X + hit_block.frame_width-5:
			if by < hit_block.Y + hit_block.frame_height/2: #above?
				ball.velocity.y = -abs(ball.velocity.y)
			else: #below?
				ball.velocity.y = abs(ball.velocity.y)

		#hit left side of block?
		elif bx < hit_block.X + 5:
			ball.velocity.x = -abs(ball.velocity.x)
		#hit right side of block?
		elif bx > hit_block.X + hit_block.frame_width - 5:
			ball.velocity.x = abs(ball.velocity.x)

		#handle any other situation
		else:
			ball.velocity.y *= -1
	


#main program begins
cap = cv2.VideoCapture(0)
ret = cap.set(3,800)             ##Default is 640X480
ret = cap.set(4,600)             ##change to 800x600
game_init()
audio_init()
game_over = False
waiting = True
score = 0
lives = 3
level = 0
load_level()
count=0
pos_x = 300
pos_y = 450
cxx=0
cyy=0
cxx_o=0
cyy_o=0
#repeating loop
while True:

	timer.tick(60)
	ticks = pygame.time.get_ticks()

	#handle events
	for event in pygame.event.get():
		if event.type == QUIT: sys.exit()
		elif event.type == MOUSEMOTION:
			movex,movey = event.rel
		elif event.type == MOUSEBUTTONUP:
			if waiting:
				waiting = False
				reset_ball()
		elif event.type == KEYUP:
			if event.key == K_RETURN: goto_next_level()

	#handle key presses
	keys = pygame.key.get_pressed()
	if keys[K_ESCAPE]: sys.exit()

	#do updates
	if not game_over:
		update_blocks()
		move_paddle()
		move_ball()
		collision_ball_paddle()
		collision_ball_blocks()

	#do drawing
	screen.fill((50,50,100))
	block_group.draw(screen)
	ball_group.draw(screen)
	paddle_group.draw(screen)
	print_text(font, 0, 0, "SCORE " + str(score))
	print_text(font, 200, 0, "LEVEL " + str(level+1))
	print_text(font, 400, 0, "BLOCKS " + str(len(block_group)))
	print_text(font, 670, 0, "BALLS " + str(lives))
	if game_over:
		print_text(font, 300, 380, "G A M E	  O V E R")
	pygame.display.update()
	
