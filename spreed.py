import pygame, sys
import argparse

from pygame.locals import *

class Spreed(object):
    def __init__(self):
        # init pygame
        pygame.init()

        if not pygame.font: print('Warning, fonts disabled')
        if not pygame.mixer: print('Warning, sound disabled')

        # init argparser 
        self.argparser = argparse.ArgumentParser(description =
                                                 "A speed reading application")
        self.argparser.add_argument("file", 
                                    help = "The text file you want to spreed.")
        self.argparser.add_argument("-s", "--speed", dest="speed",
                                    help = "Words per minute to spreed.",
                                    type=int, default=300)
        self.argparser.add_argument("-f", "--font-size", dest="font_size",
                                    help="The font size you wish to choose",
                                    type=int, default=72) 
        
        # parse arguments
        args = self.argparser.parse_args()
        self.file = args.file
        self.speed = args.speed 
        self.font_size = args.font_size

        # init display 
        self.size = pygame.display.list_modes()[0]
        self.screen = pygame.display.set_mode(self.size, FULLSCREEN)
        pygame.display.set_caption('spreed')

        # turn off the mouse (pointer)
        pygame.mouse.set_visible(False)

        # init font
        if pygame.font:
            self.font = pygame.font.Font(None, self.font_size)
        else:
            print("Error!")
            
        # read text
        f = open(self.file, 'r')
        self.raw_text = f.read()
        self.words = self.raw_text.split()
        self.words.append("--- END ---")

        # init clock
        self.clock = pygame.time.Clock()

        # init state variables
        self.running = True
        self.pause = True 
        self.word = 0

    def run(self):
        # get initial time
        time = pygame.time.get_ticks() 

        # main loop
        while self.running:
            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False 
                if event.type is KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    if event.key == K_q:
                        self.running = False
                    if event.key == K_SPACE:
                        self.pause = not self.pause
                    if event.key == K_LEFT:
                        self.word -= 1
                    if event.key == K_RIGHT:
                        self.word += 1
                    if event.key == K_0:
                        self.word = 0

            # clear screen
            self.screen.fill((0, 0, 0))
            
            # render text
            self.text = self.font.render(self.words[self.word], 1, 
                                         (255, 255, 255))
            self.textpos = self.text.get_rect(
                                centerx=self.screen.get_width()/2,
                                centery=self.screen.get_height()/2)
            self.screen.blit(self.text, self.textpos)

            # update screen
            pygame.display.flip()

            # get time
            newtime = pygame.time.get_ticks() 

            # advance word
            if not self.pause and newtime - time > 1000/(self.speed/60):
                time = pygame.time.get_ticks() 
                self.word += 1
                self.word %= len(self.words) # loop at end

if __name__ == '__main__':
    spreed = Spreed()
    spreed.run()
