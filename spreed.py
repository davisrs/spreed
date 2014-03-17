import pygame, sys
import argparse
import math

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
            self.amb_font = pygame.font.Font(None, self.font_size * 2)
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
        self.show_progress = True
        self.show_ambient = True
        self.pause = True 
        self.word = 0

    def run(self):
        # get initial time
        time = pygame.time.get_ticks() 

        # main loop
        while self.running:
            # current percentage of reading
            percent = int(len(self.words) / 100)

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False 
                if event.type is KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    if event.key == K_q:
                        self.running = False
                    if event.key == K_p:
                        self.show_progress = not self.show_progress
                    if event.key == K_SPACE:
                        self.pause = not self.pause
                    if event.key == K_LEFT:
                        self.word -= 1
                    if event.key == K_RIGHT:
                        self.word += 1
                    if event.key == K_0:
                        self.word = 0
                    if event.key == K_1:
                        self.word = percent * 10 
                    if event.key == K_2:
                        self.word = percent * 20
                    if event.key == K_3:
                        self.word = percent * 30
                    if event.key == K_4:
                        self.word = percent * 40 
                    if event.key == K_5:
                        self.word = percent * 50
                    if event.key == K_6:
                        self.word = percent * 60
                    if event.key == K_7:
                        self.word = percent * 70
                    if event.key == K_8:
                        self.word = percent * 80
                    if event.key == K_9:
                        self.word = percent * 90

            self.word %= len(self.words)

            # clear screen
            self.screen.fill((0, 0, 0))
            
            # render text
            self.text = self.font.render(self.words[self.word], 1, 
                                         (255, 255, 255))
            self.textpos = self.text.get_rect(
                                centerx=self.screen.get_width() / 2,
                                centery=self.screen.get_height() / 2)
            self.screen.blit(self.text, self.textpos)

            # draw progress bar
            if self.show_progress:
                self.draw_progress()

            # draw ambient text symbols
            if self.show_ambient:
                self.ambient_text()

            # update screen
            pygame.display.flip()

            # get time
            newtime = pygame.time.get_ticks() 

            if self.word == len(self.words) - 1:
                self.pause = True

            # advance word
            if not self.pause and newtime - time > 1000 / (self.speed / 60):
                time = pygame.time.get_ticks() 
                self.word += 1

    def draw_progress(self):
        # current progress
        ratio = self.word / len(self.words)

        # progress bar coordinates
        bar_x = self.screen.get_width() / 10
        bar_y = self.screen.get_height() - (self.screen.get_height() / 8)
        bar_w = self.screen.get_width() - 2 * bar_x 
        bar_h = bar_w / 30
        
        # progress bar frame
        outer_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        inner_rect = pygame.Rect(bar_x, bar_y, max(bar_w * ratio, 1), bar_h)

        # draw the frame
        pygame.draw.rect(self.screen, pygame.Color("white"), outer_rect, 2)
        pygame.draw.rect(self.screen, pygame.Color("white"), inner_rect)

    def ambient_text(self):
        if self.words[self.word].endswith("?"):
            symb = self.font.render("?", 1, (255, 255, 255))
            symb_pos = self.text.get_rect(
                                centerx = self.screen.get_width() 
                                        - self.screen.get_width() / 5,
                                centery = self.screen.get_height() / 2)
            self.screen.blit(symb, symb_pos)

if __name__ == '__main__':
    spreed = Spreed()
    spreed.run()
