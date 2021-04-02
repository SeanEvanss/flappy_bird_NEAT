import os
import neat
import pygame
import time
import random
pygame.font.init()

#Constants
WIN_WIDTH= 500
WIN_HEIGHT= 800

BIRD_IMGS=[pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

PIPE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

STAT_FONT= pygame.font.SysFont("comicsans",50)
GAME_OVER= pygame.font.SysFont("comicsans",200)

SINGLE_PLAYER=True

class Bird:
    IMGS= BIRD_IMGS
    MAX_ROTATION= 25
    ROT_VEL= 20
    ANIM_TIME= 5

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tilt=0
        self.tick_count=0
        self.vel=0
        self.height=self.y
        self.img_count=0
        self.img= self.IMGS[0]

    def jump(self):
        self.vel= -10.5 #Remember 0,0 is the top left so negative vel means it would go up. Don't ask, I don't know why pygame is that way.
        self.tick_count =0
        self.height=self.y

    def move(self):
        self.tick_count +=1
        displacement= self.vel*self.tick_count + 1.5*self.tick_count**2 #This is to calculate how our bird would be moving (in an arc)

        if displacement >= 16:
            displacement= 16
        if displacement <0:
            displacement -=2

        self.y= self.y+ displacement #Updats our y position

        if(displacement<0 or self.y < self.height+50):
            if self.tilt < self.MAX_ROTATION:
                self.tilt= self.MAX_ROTATION
        else:
            if(self.tilt >= -90):
                self.tilt -= self.ROT_VEL
    def draw(self,win):
        self.img_count +=1

        if(self.img_count < self.ANIM_TIME):
            self.img= self.IMGS[0]
        elif (self.img_count < self.ANIM_TIME*2):
            self.img = self.IMGS[1]
        elif (self.img_count < self.ANIM_TIME*3):
            self.img = self.IMGS[2]
        elif (self.img_count < self.ANIM_TIME*4):
            self.img = self.IMGS[1]
        elif (self.img_count < self.ANIM_TIME*5):
            self.img = self.IMGS[0]
            self.img_count=0

        if(self.tilt<= -80):
            self.img= self.IMGS[1]
            self.img_count= self.ANIM_TIME*2

        rotated_img= pygame.transform.rotate(self.img, self.tilt)
        new_rect= rotated_img.get_rect(center= self.img.get_rect(topleft= (self.x,self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP= 180
    VEL= 5

    def __init__(self,x):
        self.x= x
        self.height=0
        self.top=0
        self.bottom=0;

        self.PIPE_TOP=pygame.transform.flip(PIPE_IMG,False,True)
        self.PIPE_BOTTOM=PIPE_IMG

        self.passed= False
        self.set_height()

    def set_height(self):
        self.height= random.randrange(50,450)
        self.top= self.height- self.PIPE_TOP.get_height()
        self.bottom= self.height+self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask= bird.get_mask()
        top_mask= pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - round(bird.x), self.top- round(bird.y))
        bottom_offset = (self.x - round(bird.x), self.bottom - round(bird.y))

        bottom_collide= bird_mask.overlap(bottom_mask, bottom_offset)
        top_collide= bird_mask.overlap(top_mask, top_offset)

        if(bottom_collide or top_collide):
            print("Collide ")
            return True

        return False

class Base:
    VEL= 5
    WIDTH= BASE_IMG.get_width()
    IMG= BASE_IMG

    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2= self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1+self.WIDTH<0:
            self.x1= self.x2+ self.WIDTH

        if self.x2+ self.WIDTH<0:
            self.x2= self.x1+ self.WIDTH

    def draw(self,win):
        win.blit(self.IMG,(self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, bird, pipes, base,score):
    win.blit(BG_IMG,(0,0))

    for pipe in pipes:
        pipe.draw(win)
    text= STAT_FONT.render("Score:" + str(score),1,(255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    bird.draw(win)
    pygame.display.update()

def main():
    bird= Bird(230,350)
    base= Base(730)
    pipes=[Pipe(600)]
    score=0

    win= pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

    clock= pygame.time.Clock()
    run=True

    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                run=False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()
        add_pipe= False
        rem_pipe= False
        rem=[]
        for pipe in pipes:
            if pipe.collide(bird):
                run=False

            if pipe.x + pipe.PIPE_TOP.get_width()<0:
                rem.append(pipe)
                rem_pipe= True
                #pipes.pop(0)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed= True
                add_pipe= True

            pipe.move()

        if(add_pipe):
            score+=1
            pipes.append(Pipe(600))
        if rem_pipe:
            pipes.pop(0)
        if bird.y+ bird.img.get_height()>=730: #Bird hits the ground

            run=False

        base.move()
        draw_window(win, bird, pipes, base,score)


    pygame.quit()
    quit()

def run(config_path):
    config_path= neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    population= neat.Population(config_path)
    population.add_reporter(neat.StdOutReporter(True))
    stats= neat.StatisticsReporter()
    population.add_reporter(stats)

    winner= population.run(main(),50)

if __name__ == '__main__':
    '''
    local_dir= os.path.dirname(os.path.join(__file__))
    config_path= os.path.join(local_dir, "config.txt")
    run()
    '''
    main()



