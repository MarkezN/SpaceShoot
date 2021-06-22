import pygame
import os
import time
import random
from random import randrange
pygame.font.init()

width, height = 850, 850
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Wars")

#imgs
redShip = pygame.image.load("assets/enemyRed.png")
greenShip = pygame.image.load("assets/enemyGreen.png")
blueShip = pygame.image.load("assets/enemyBlue.png")


playerShip = pygame.image.load("assets/shuttle.png")


redLaser = pygame.image.load("assets/laserRed.png")
greenLaser = pygame.image.load("assets/laserGreen.png")
blueLaser = pygame.image.load("assets/laserBlue.png")
yellowLaser = pygame.image.load("assets/laserYellow.png")


#background scaling image
back = pygame.transform.scale(pygame.image.load("assets/spaceFelix.jpg"), (width, height))

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(img)

	def draw(self, win):
		win.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def offscreen(self, height):
		return not(self.y < height and self.y >= 0)			
		
	
	def collision(self, obj):
		return collide(obj, self)	


class SpaceShip:

	# how often can player shoot lasers
	coolDown = 20

	def __init__(self, x , y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0


	def draw(self, win):
		win.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(win)

	def moveLasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.offscreen(height):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)	


	def cooldown(self):
		if self.cool_down_counter >= self.coolDown:	
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1	

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1			

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()		


class Player(SpaceShip):
	
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = playerShip
		self.laser_img = yellowLaser

		#collision
		self.mask = pygame.mask.from_surface(self.ship_img)	
		self.max_health = health

	def moveLasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.offscreen(height):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)

	def healthbar(self, win):
		pygame.draw.rect(win, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))						
		pygame.draw.rect(win, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))						

	def draw(self, win):
		super().draw(win)
		self.healthbar(win)


class Enemy(SpaceShip):

	color_map = {
			"red": (redShip, redLaser),
			"green": (greenShip, greenLaser),
			"blue": (blueShip, blueLaser)
	}

	def __init__(self, x , y, color, health = 100):
		super().__init__(x, y, health)
		self.ship_img, self.laser_img = self.color_map[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel	

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x + 15, self.y + 20, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1			


def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():

	run = True

	FPS = 60
	level = 0
	lives = 5

	mainFont = pygame.font.SysFont("sans-serif", 45)
	lostFont = pygame.font.SysFont("comicsans", 70)

	enemies = []
	wave_len = 5
	enemy_vel = 1
	player_vel = 5
	laser_vel = 5

	player = Player(300, 630)

	clock = pygame.time.Clock()

	lost = False
	lost_count = 0

	def redraw_window():

		#background starting pos
		win.blit(back, (0, 0))

		
		livesLab = mainFont.render(f"Lives: {lives}", 1, (255,255,0))
		levelLab = mainFont.render(f"Level: {level}", 1, (255,0,0))

		win.blit(livesLab, (10, 10))
		win.blit(levelLab, (10,45))

		for enemy in enemies:
			enemy.draw(win)

		player.draw(win)	

		if lost:
			lostLabel = lostFont.render("YOU LOST!!", 1, (255,255,255))
			win.blit(lostLabel, (width/2 - lost_label.get_width()/2, 350))

		pygame.display.update()

	while run:
		
		clock.tick(FPS)
		redraw_window()

		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue		

		if len(enemies) == 0:
			level += 1
			wave_len += 5
			for i in range(wave_len):
				enemy = Enemy(random.randrange(50, width -100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)

		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				quit()

		# movement			
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT] and player.x - player_vel > 0:
			player.x -= player_vel	
		if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < width: 
			player.x += player_vel
		if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < height: 
			player.y += player_vel
		if keys[pygame.K_UP] and player.y - player_vel > 0: 	
			player.y -= player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.moveLasers(laser_vel, player)

			if random.randrange(0, 2*60) == 1:
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)	
	

			elif enemy.y + enemy.get_height() > height:
				lives -= 1
				enemies.remove(enemy)

		player.moveLasers(-laser_vel, enemies)		


def main_menu():

	title_font = pygame.font.SysFont("comicsans", 70)
	run = True
	while run:
		win.blit(back, (0,0))
		title_label = title_font.render("Mouse click for start ...", 1, (255,255,255))
		win.blit(title_label, (width/2 - title_label.get_width()/2, 350))
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if	event.type == pygame.MOUSEBUTTONDOWN:
				main()
	pygame.quit()			

main_menu()	