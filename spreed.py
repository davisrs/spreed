import pygame, sys

from pygame.locals import *

class Spreed(object):
    def __init__(self):
        # init pygame
        pygame.init()

        if not pygame.font: print('Warning, fonts disabled')
        if not pygame.mixer: print('Warning, sound disabled')

        # init display 
        self.size = pygame.display.list_modes()[0]
        self.screen = pygame.display.set_mode(self.size, FULLSCREEN)
        pygame.display.set_caption('spreed')

        # init font
        self.font_size = 72

        if pygame.font:
            self.font = pygame.font.Font(None, self.font_size)
        else:
            print("Error!")
            
        # read text
        f = open('input.txt', 'r')
        self.raw_text = f.read()
        self.words = self.raw_text.split()
        self.words.append("--- END ---")

        # init clock
        self.clock = pygame.time.Clock()

        # init state variables
        self.running = True
        self.pause = True 
        self.word = 0
        self.speed = 300 # wpm

    def run(self):
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

            if not self.pause:
                # advance word
                self.word += 1
                self.word %= len(self.words) # loop at end

            # cap framerate
            self.clock.tick(self.speed/60)

            # update screen
            pygame.display.flip()

if __name__ == '__main__':
    spreed = Spreed()
    spreed.run()
